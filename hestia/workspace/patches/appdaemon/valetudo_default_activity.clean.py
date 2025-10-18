import contextlib
import json
import os
from typing import Any

import yaml

try:
    from appdaemon.plugins.hass import hassapi  # type: ignore
except Exception:
    class hassapi:  # type: ignore
        class Hass:
            def __init__(self, *args, **kwargs) -> None:
                self.args = {}

            def log(self, *args, **kwargs) -> None:
                pass

            def error(self, *args, **kwargs) -> None:
                pass

            def call_service(self, *args, **kwargs) -> None:
                pass

            def get_state(self, *args, **kwargs):
                return None

            def run_every(self, *args, **kwargs) -> None:
                pass


class ValetudoDefaultActivity(hassapi.Hass):
    def initialize(self) -> None:
        if not hasattr(self, "args"):
            self.args = {}
        self.schedule_entity = self.args.get(
            "schedule_entity", "schedule.valetudo_allowed"
        )
        self.config_sensor = self.args.get(
            "config_sensor", "sensor.room_configs_vacuum_control"
        )
        self.default_mode = self.args.get("default_mode", "vacuum")
        self.canonical_mapping_file = self.args.get("canonical_mapping_file")
        self._mapping_path: str | None = None
        self._room_to_segment: dict[str, Any] | None = None

        with contextlib.suppress(Exception):
            self._validate_config()

        with contextlib.suppress(Exception):
            self.run_every(self._poll_loop, "now", 30)

    def _mapping_candidates(self):
        candidates = [
            self.canonical_mapping_file,
            "/config/www/area_mapping.yaml",
            "/config/domain/architecture/area_mapping.yaml",
        ]
        seen = set()
        ordered = []
        for c in candidates:
            if c and c not in seen:
                ordered.append(c)
                seen.add(c)
        return ordered

    def _resolve_mapping_path(self) -> str | None:
        for path in self._mapping_candidates():
            try:
                if path and os.path.exists(path):
                    return path
            except Exception:
                continue
        return None

    def _load_mapping(self) -> dict[str, Any]:
        if self._room_to_segment is None:
            self._mapping_path = self._resolve_mapping_path()
            if self._mapping_path and os.path.exists(self._mapping_path):
                with open(self._mapping_path) as f:
                    amap = yaml.safe_load(f) or {}
                nodes = amap.get("nodes", [])
                mapping: dict[str, Any] = {}
                for n in nodes:
                    t = n.get("type")
                    if t in ["area", "subarea"]:
                        rid = n.get("id")
                        seg = n.get("attributes", {}).get("vacuum_segment_id")
                        if rid:
                            mapping[rid] = seg
                self._room_to_segment = mapping
            else:
                self._room_to_segment = {}
        return self._room_to_segment

    def _validate_config(self) -> None:
        self._mapping_path = self._resolve_mapping_path()

    def _schedule_allowed(self) -> bool:
        state = None
        try:
            state = self.get_state(self.schedule_entity)
        except Exception:
            state = None
        return str(state).lower() in ["on", "true", "1"]

    def _poll_loop(self, *args, **kwargs) -> None:
        if not self._schedule_allowed():
            return
        try:
            raw = self.get_state(self.config_sensor, attribute="all")
        except Exception:
            raw = None
        if not raw:
            return
        attrs = raw.get("attributes", {}) if isinstance(raw, dict) else {}
        payload = attrs.get("payload")
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except Exception:
            data = None
        if not isinstance(data, dict):
            return
        for room_id, cfg in data.items():
            self._process_job(room_id, cfg)

    def _process_job(self, room_id: str, cfg: Any) -> None:
        if not self._schedule_allowed():
            return
        if not isinstance(cfg, dict):
            return
        mapping = self._load_mapping()
        if cfg.get("segment_id") is None:
            seg = mapping.get(room_id)
            if seg is not None:
                cfg["segment_id"] = seg
        if cfg.get("mode") is None:
            cfg["mode"] = self.default_mode
        self._write_back(room_id, cfg)

    def _write_back(self, room_id: str, cfg: dict[str, Any]) -> None:
        try:
            self.call_service(
                "rest_command/room_db_update_config",
                room_id=room_id,
                domain="vacuum_control",
                config_data=cfg,
            )
        except Exception as e:
            self.error(f"Valetudo write-back failed for {room_id}: {e}")