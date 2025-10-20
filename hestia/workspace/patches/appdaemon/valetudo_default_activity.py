# AppDaemon 4
# Valetudo default-activity controller:
# - Routine queue from Room-DB (needs_cleaning==1)
# - Ad-hoc event handler (valetudo_ad_hoc_clean)
# - MQTT publish driver using HA's input_text.valetudo_base_topic
# - Schedule gate via schedule.valetudo_allowed (on=allowed, off=blocked)
# - Presence gate via binary_sensor.<room>_presence_beta
# - Optimistic completion (configurable), throttled Room-DB writebacks (>=2s)
# - Fallback segment/defaults from area_mapping.yaml nodes[*].capabilities.vacuum_control

import json
import os
import time
import uuid
from collections import deque
from datetime import timedelta

from appdaemon.plugins.hass import hassapi as hass

try:
    import yaml
except Exception:
    yaml = None


def _now_iso(app: hass.Hass) -> str:
    return app.datetime().isoformat()


class ValetudoDriver:
    def __init__(self, app: hass.Hass, topic_cmd: str, qos: int = 1):
        self.app = app
        self.topic_cmd = topic_cmd
        self.qos = qos

    def clean_segments(self, room: str, segment_ids, mode=None, job_id: str = ""):
        # Match existing HA script payload (vac_scripts.yaml)
        payload = {
            "action": "clean",
            "segment_ids": list(segment_ids),
            "iterations": 1,
            "customOrder": True,
        }
        self.app.call_service(
            "mqtt/publish",
            topic=self.topic_cmd,
            payload=json.dumps(payload),
            qos=self.qos,
            retain=False,
        )


class ValetudoDefaultActivity(hass.Hass):
    def initialize(self):
        # ---- Config (defaults kept minimal) ----
        update_service_cfg = self.args.get("ha", {}).get(
            "room_db_update_service", "rest_command.room_db_update_config"
        )
        # AppDaemon wants domain/service with '/', accept dot and normalize:
        self.update_service = update_service_cfg.replace(".", "/")

        self.cfg = {
            "mqtt": {
                "command_topic": self.args.get("valetudo", {})
                .get("mqtt", {})
                .get("command_topic", "valetudo/robot/command"),
                "qos": int(self.args.get("mqtt", {}).get("base_qos", 1)),
            },
            "ha": {
                "room_configs_sensor": self.args.get("ha", {}).get(
                    "room_configs_sensor", "sensor.room_configs_vacuum_control"
                ),
                "presence_glob_suffix": self.args.get("ha", {}).get(
                    "presence_sensors_glob", "_presence_beta"
                ),
                "schedule_entity": self.args.get("ha", {}).get(
                    "schedule_entity", "schedule.valetudo_allowed"
                ),
                "mapping_path": self.args.get("ha", {}).get(
                    "mapping_path", "/addon_configs/a0d7b954_appdaemon/www/area_mapping.yaml"
                ),
                "base_topic_entity": self.args.get("ha", {}).get(
                    "base_topic_entity", "input_text.valetudo_base_topic"
                ),
            },
            "policy": {
                "batch_size": int(self.args.get("policy", {}).get("batch_size", 2)),
                "require_presence_clear": bool(
                    self.args.get("policy", {}).get("require_presence_clear", True)
                ),
                "max_job_runtime_minutes": int(
                    self.args.get("policy", {}).get("max_job_runtime_minutes", 60)
                ),
                "optimistic_writeback": bool(
                    self.args.get("policy", {}).get("optimistic_writeback", False)
                ),
                "optimistic_job_seconds": int(
                    self.args.get("policy", {}).get("optimistic_job_seconds", 90)
                ),
                "rate_limit_seconds": int(self.args.get("policy", {}).get("rate_limit_seconds", 2)),
            },
        }

        # ---- Runtime ----
        self.driver = ValetudoDriver(
            self, self.cfg["mqtt"]["command_topic"], self.cfg["mqtt"]["qos"]
        )
        self.queue = deque()
        self.queued_rooms = set()
        self.active = None  # {"room":..., "job_id":..., "started": epoch, "timeout_handle": handle}
        self.last_write_ts = {}  # {(room, domain): epoch}

        # Resolve MQTT command topic from base topic helper
        self.base_topic_entity = self.cfg["ha"]["base_topic_entity"]
        self._set_command_topic_from_base()
        self.listen_state(self._on_base_topic_change, self.base_topic_entity)

        # Events & ticks
        self.listen_event(self._on_ad_hoc, "valetudo_ad_hoc_clean")
        self.run_every(self._tick, self.datetime() + timedelta(seconds=5), 30)

        # Load area mapping (fallback for segment_id/default_mode)
        self.area_map = {}
        mapping_path = self.cfg["ha"]["mapping_path"]
        if os.path.exists(mapping_path) and yaml:
            try:
                with open(mapping_path, encoding="utf-8") as f:
                    doc = yaml.safe_load(f) or {}
                nodes = doc.get("nodes") or []
                built = {}
                for n in nodes:
                    rid = (n or {}).get("id")
                    vc = ((n or {}).get("capabilities") or {}).get("vacuum_control") or {}
                    if rid and vc:
                        built[rid] = vc
                self.area_map = built
                self.log(
                    f"Loaded area_mapping nodes with vacuum caps: {len(self.area_map)} rooms",
                    level="INFO",
                )
            except Exception as e:
                self.error(f"Failed to load area_mapping.yaml: {e}")
        else:
            self.log(
                "area_mapping.yaml not found or PyYAML missing; continuing without fallback",
                level="WARNING",
            )

        self.log("ValetudoDefaultActivity initialized", level="INFO")

    # ---------- Core Tick ----------
    def _tick(self, *args, **kwargs):
        self._enqueue_routine()
        if not self.active and self.queue:
            self._start_next_job()

    # ---------- Routine Enqueue ----------
    def _enqueue_routine(self):
        payload = self.get_state(self.cfg["ha"]["room_configs_sensor"], attribute="payload")
        if not payload or not str(payload).startswith("{"):
            return
        try:
            data = json.loads(payload)
        except Exception:
            self.error("Invalid JSON in room_configs_vacuum_control.payload")
            return

        candidates = []
        for r, cfg in data.items():
            v = cfg.get("needs_cleaning", 0)
            if isinstance(v, bool):
                if v:
                    candidates.append(r)
            else:
                if str(v) in ("1", "true", "True"):
                    candidates.append(r)

        if not candidates:
            return

        added = 0
        for room in candidates:
            if room in self.queued_rooms or (self.active and self.active.get("room") == room):
                continue
            if not self._policy_allows(room):
                continue
            seg = data.get(room, {}).get("segment_id")
            if seg is None:
                seg = self._fallback_segment(room)
            if seg is None:
                self.log(f"Skipping {room}: missing segment_id", level="WARNING")
                continue
            mode = (
                data.get(room, {}).get("default_mode")
                or self._fallback_default_mode(room)
                or "standard"
            )
            job = self._mk_job(room, [seg], mode, "routine")
            self.queue.append(job)
            self.queued_rooms.add(room)
            added += 1
            if added >= self.cfg["policy"]["batch_size"]:
                break

    # ---------- Ad-hoc Event ----------
    def _on_ad_hoc(self, event_name, data, kwargs):
        room = str(data.get("room", "")).strip()
        force = bool(data.get("force", False))  # overrides schedule gate
        force_presence = bool(data.get("force_presence", False))
        if not room:
            self.error("ad-hoc: missing 'room'")
            return

        payload = self.get_state(self.cfg["ha"]["room_configs_sensor"], attribute="payload")
        seg = None
        mode = "standard"
        if payload and str(payload).startswith("{"):
            try:
                d = json.loads(payload)
                seg = d.get(room, {}).get("segment_id")
                mode = d.get(room, {}).get("default_mode") or "standard"
            except Exception:
                pass
        if seg is None:
            seg = self._fallback_segment(room)
        if seg is None:
            self.error(
                f"ad-hoc: room '{room}' missing segment_id (not in Room-DB or area_mapping nodes)"
            )
            return

        if not force and not self._policy_allows(
            room,
            force_presence=force_presence,
            force_schedule=False,
        ):
            self.log(f"ad-hoc: policy deferred for {room}", level="INFO")
            return

        if room not in self.queued_rooms and not (self.active and self.active.get("room") == room):
            job = self._mk_job(room, [seg], self._fallback_default_mode(room) or mode, "adhoc")
            self.queue.appendleft(job)
            self.queued_rooms.add(room)
            self.log(f"ad-hoc job queued: {room}", level="INFO")

    # ---------- Job Lifecycle ----------
    def _start_next_job(self):
        if not self.queue:
            return
        job = self.queue.popleft()
        self.queued_rooms.discard(job["room"])
        self.active = {
            "room": job["room"],
            "job_id": job["job_id"],
            "started": time.time(),
            "job": job,
        }

        # Publish command
        self.driver.clean_segments(job["room"], job["segments"], job["mode"], job["job_id"])
        self.log(f"Job STARTING: {job}", level="INFO")

        # Timeout guard
        timeout_secs = max(60, self.cfg["policy"]["max_job_runtime_minutes"] * 60)
        self.active["timeout_handle"] = self.run_in(self._on_job_timeout, timeout_secs)

        # MVP: optimistic completion (optional)
        if self.cfg["policy"]["optimistic_writeback"]:
            self.run_in(self._on_job_success, int(self.cfg["policy"]["optimistic_job_seconds"]))

    def _on_job_success(self, *args, **kwargs):
        if not self.active:
            return
        job = self.active["job"]
        self.log(f"Job DONE (optimistic): {job}", level="INFO")
        self._writeback(
            job["room"],
            {
                "needs_cleaning": 0,
                "last_cleaned": _now_iso(self),
                "last_result": {
                    "job_id": job["job_id"],
                    "status": "success",
                    "started_at": _now_iso(self),
                    "finished_at": _now_iso(self),
                    "notes": "optimistic_complete",
                },
            },
        )
        self._clear_active()

    def _on_job_timeout(self, *args, **kwargs):
        if not self.active:
            return
        job = self.active["job"]
        self.error(f"Job TIMEOUT: {job}")
        self._writeback(
            job["room"],
            {
                "last_result": {
                    "job_id": job["job_id"],
                    "status": "failed",
                    "started_at": _now_iso(self),
                    "finished_at": _now_iso(self),
                    "notes": "timeout_no_state",
                }
            },
        )
        self._clear_active()

    def _clear_active(self):
        if self.active and self.active.get("timeout_handle"):
            import contextlib

            with contextlib.suppress(Exception):
                self.cancel_timer(self.active["timeout_handle"])
        self.active = None

    # ---------- Helpers ----------
    def _mk_job(self, room, segments, mode, job_type):
        return {
            "room": room,
            "segments": segments,
            "mode": mode,
            "job_type": job_type,
            "job_id": str(uuid.uuid4()),
        }

    def _policy_allows(self, room, force_presence=False, force_schedule=False):
        # Schedule gate (on = allowed, off = blocked)
        sched = self.cfg["ha"]["schedule_entity"]
        if not force_schedule and sched:
            st = self.get_state(sched)
            if st == "off":
                return False
        # Presence gate
        if self.cfg["policy"]["require_presence_clear"] and not force_presence:
            sensor = f"binary_sensor.{room}{self.cfg['ha']['presence_glob_suffix']}"
            if self.get_state(sensor) == "on":
                return False
        return True

    def _writeback(self, room, config_delta: dict):
        domain = "vacuum_control"
        key = (room, domain)
        last = self.last_write_ts.get(key, 0)
        now = time.time()
        # add a tiny jitter to smooth concurrent writers
        jitter = 0.2
        wait = self.cfg["policy"]["rate_limit_seconds"] - (now - last) + jitter
        if wait > 0:
            self.run_in(lambda *_: self._writeback(room, config_delta), int(wait) + 1)
            return

        payload = {
            "room_id": room,
            "domain": domain,
            "config_data": config_delta,
            "schema_expected": 1,
        }
        # REST layer applies tojson; we pass native dicts
        self.call_service(self.update_service, **payload)
        self.last_write_ts[key] = time.time()
        self.log(f"Room-DB writeback: {payload}", level="INFO")

    # ---- MQTT base topic handling ----
    def _set_command_topic_from_base(self, *args, **kwargs):
        base = (self.get_state(self.base_topic_entity) or "valetudo/robot").strip().rstrip("/")
        topic = f"{base}/MapSegmentationCapability/action/start_segment_action"
        self.driver.topic_cmd = topic
        self.log(f"Valetudo command topic set to: {topic}", level="INFO")

    def _on_base_topic_change(self, entity, attribute, old, new, kwargs):
        self._set_command_topic_from_base()

    # ---- Fallback lookups from area_mapping.yaml ----
    def _fallback_segment(self, room):
        try:
            return (self.area_map.get(room) or {}).get("segment_id")
        except Exception:
            return None

    def _fallback_default_mode(self, room):
        try:
            return (self.area_map.get(room) or {}).get("default_mode")
        except Exception:
            return None
