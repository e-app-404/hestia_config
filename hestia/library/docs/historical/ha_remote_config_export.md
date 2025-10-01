# 🧰 Remote Home Assistant Config Export via Tailscale

This guide documents the step-by-step workflow for remotely packaging and downloading a lean copy of your Home Assistant `/config` directory using Tailscale.

---

## 🔐 Assumptions

* You are SSH'd into your HA instance via its **Tailscale IP** or **MagicDNS name**
* You are operating from your **MacBook**, with the download target folder:

```bash
/Users/evertappels/Projects/APPLE PII
```

* Home Assistant is running on port 8123 and you have shell access to `/config`

---

## ⚙️ Step-by-Step Workflow

### 🟦 1. SSH into Home Assistant

From your Mac:

```bash
ssh babylon-babes@100.105.130.99
```

Or with MagicDNS:

```bash
ssh babylon-babes@homeassistant.ts.net
```

---

### 🟪 2. Create Lean Tarball

In the HA shell:

```bash
tar --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.log" \
    --exclude="*.db" \
    --exclude="*.sqlite*" \
    --exclude="tts/" \
    --exclude="media/" \
    --exclude="deps/" \
    -czf /tmp/config_backup_lean.tar.gz -C /config .
```

This creates the tarball at `/tmp/config_backup_lean.tar.gz`.

---

### 🟨 3. Expose Tarball Over HTTP

Run a temporary Python server:

```bash
cd /tmp
python3 -m http.server 8126
```

This exposes:

```bash
http://100.105.130.99:8126/config_backup_lean.tar.gz
```

---

### 🟩 4. Download to Mac

In a separate Mac terminal:

```bash
curl -o "/Users/evertappels/Projects/APPLE PII/config_backup_lean.tar.gz" \
     http://100.105.130.99:8126/config_backup_lean.tar.gz
```

---

### 🔴 5. Stop HTTP Server

Back on the HA terminal:

```bash
Ctrl + C
```

---

## 🔁 Optional: Turn into Script

You may convert steps 2–3 into a script saved as `export_lean_config.sh` inside `/config/scripts/`:

```bash
#!/bin/bash
cd /config

tar --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.log" \
    --exclude="*.db" \
    --exclude="*.sqlite*" \
    --exclude="tts/" \
    --exclude="media/" \
    --exclude="deps/" \
    -czf /tmp/config_backup_lean.tar.gz -C /config .

cd /tmp
python3 -m http.server 8126
```

Ensure the script is executable:

```bash
chmod +x /config/scripts/export_lean_config.sh
```

Then run from HA:

```bash
bash /config/scripts/export_lean_config.sh
```

---

## 🧭 Future Enhancements

* Add cleanup step to delete tarball after download
* Auto-terminate HTTP server after `curl` detects success (using `timeout` or a wrapper)
* Secure with authentication header if exposing externally (e.g. via reverse proxy)

---

> Maintained as part of the **Janus NIE Diagnostics & Telemetry Toolchain**
