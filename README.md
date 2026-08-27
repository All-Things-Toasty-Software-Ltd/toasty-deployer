# Toasty Deployer

A lightweight GitHub App webhook listener and automated deployment service built with Flask and Python. **Toasty
Deployer** listens for GitHub push events, runs corresponding local bash scripts, and provides both a web UI and a
structured REST API for seamless integration with Odoo.

---

## Features

- **HMAC Signature Verification:** Verifies all incoming `X-Hub-Signature-256` payloads against a configured webhook
  secret.
- **SQLite Run Storage:** Records every execution, exit code, and stdout/stderr log in a local SQLite database
  (`deployments.db`).
- **Odoo-Ready REST API:** Exposes serialized endpoints (`/api/owners/...`) for custom Odoo modules to track build
  statuses and console logs.

---

## Installation & Deployment

1. Requirements

    - Linux Server (Ubuntu/Debian recommended)

    - Python 3.10+

    - Gunicorn

    - Systemd

2. Setup Repository
    ```bash
    git clone https://github.com/All-Things-Toasty-Software-Ltd/toasty-deployer.git /opt/toasty-deployer
    cd /opt/toasty-deployer
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
   ```

3. Environment Configuration

   Create a .env file in /opt/toasty-deployer/:

    ```
   APP_ID=123456
    WEBHOOK_SECRET=your_webhook_secret_here
    PRIVATE_KEY_PATH=/opt/toasty-deployer/private-key.pem
    DB_PATH=/opt/toasty-deployer/deployments.db
    REPOS_DIR=/repos
    ```

4. Create Deployment Scripts Directory

   Deployment scripts are expected in /repos/{owner}/{repo}.sh (or the path defined by `REPOS_DIR`):

    ```bash
   mkdir -p /repos/{owner}
   nano /repos/{owner}/{repo}.sh
   chmod +x /repos/{owner}/{repo}.sh
    ```

   Example script contents:

    ```bash
   #!/usr/bin/env bash
   echo "=== Starting Deployment for bakers-archive-mobile-companion ==="
   git clone https://github.com/All-Things-Toasty-Software-Ltd/bakers-archive-mobile-companion.git
   cd bakers-archive-mobile-companion
   ./gradlew \
      :app:androidApp:assembleRelease \
      app:androidApp:bundleRelease \
      --stacktrace
   echo "=== Starting Deployment for bakers-archive-mobile-companion ==="
    ```
   
5. Systemd Service Configuration

    Create `/etc/systemd/system/toasty-deployer.service`:

    ```
    [Unit]
    Description=Toasty Deployer GitHub App Webhook Service
    After=network.target
    
    [Service]
    User=root
    WorkingDirectory=/opt/toasty-deployer
    EnvironmentFile=/opt/toasty-deployer/.env
    ExecStart=/opt/toasty-deployer/venv/bin/gunicorn --access-logfile - --error-logfile - -w 2 -b 0.0.0.0:5000 run:app
    Restart=always
    
    [Install]
    WantedBy=multi-user.target
    ```
   
    Enable and start the service:

    ```bash
   systemctl daemon-reload
   systemctl enable --now toasty-deployer
    ```
   
---

Licensing & Copyright

Copyright (c) All Things Toasty Software Ltd. All rights reserved.

Licensed under the [LGPLv3](LICENSE) License.