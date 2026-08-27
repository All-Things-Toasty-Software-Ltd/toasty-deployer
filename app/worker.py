# -*- coding: utf-8 -*-
# Part of Toasty Deployer. See LICENSE file for full copyright and licensing details.

import hashlib
import hmac
import os
import subprocess
import time

import jwt
import requests

from app import db
from config import Config


def get_jwt():
    if not Config.PRIVATE_KEY_PATH or not os.path.exists(Config.PRIVATE_KEY_PATH):
        return None
    with open(Config.PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()
    payload = {
        'iat': int(time.time()) - 60,
        'exp': int(time.time()) + (10 * 60),
        'iss': Config.APP_ID
    }
    return jwt.encode(payload, private_key, algorithm='RS256')


def get_installation_access_token(installation_id):
    jwt_token = get_jwt()
    if not jwt_token:
        return None
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/vnd.github+json"}
    res = requests.post(url, headers=headers)
    return res.json().get("token") if res.status_code == 201 else None


def verify_signature(payload_body, signature_header):
    if not signature_header or not Config.WEBHOOK_SECRET:
        return False
    hash_object = hmac.new(Config.WEBHOOK_SECRET.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


def execute_deployment(owner, repo, commit_sha, installation_id, script_path):
    print(f"--> [THREAD] Triggered for {owner}/{repo} @ {commit_sha}", flush=True)
    run_id = db.create_run(owner, repo, commit_sha)

    token = get_installation_access_token(installation_id) if installation_id else None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"} if token else {}
    check_url = f"https://api.github.com/repos/{owner}/{repo}/check-runs"
    check_id = None

    if token:
        try:
            res = requests.post(check_url, headers=headers, json={
                "name": "Toasty Local Deployment",
                "head_sha": commit_sha,
                "status": "in_progress"
            }).json()
            check_id = res.get('id')
        except Exception as e:
            print(f"--> [WARN] Failed creating Check Run: {e}", flush=True)

    if not os.path.isfile(script_path):
        err_msg = f"Missing executable script at {script_path}"
        print(f"--> [ERROR] {err_msg}", flush=True)
        db.update_run(run_id, "failure", 127, err_msg)
        if check_id and token:
            requests.patch(f"{check_url}/{check_id}", headers=headers, json={
                "status": "completed",
                "conclusion": "failure",
                "output": {"title": "Script Missing", "summary": err_msg}
            })
        return

    print(f"--> [EXEC] Running script: {script_path}", flush=True)
    logs, exit_code = "", 1
    try:
        process = subprocess.Popen(
            ["bash", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            logs += line
            print(f"    [SCRIPT LOG] {line.strip()}", flush=True)
        process.wait()
        exit_code = process.returncode
        status = "success" if exit_code == 0 else "failure"
    except Exception as e:
        status = "failure"
        logs += f"\nProcess Execution Error: {str(e)}"

    db.update_run(run_id, status, exit_code, logs)

    if check_id and token:
        requests.patch(f"{check_url}/{check_id}", headers=headers, json={
            "status": "completed",
            "conclusion": status,
            "output": {
                "title": "Deployment Execution Logs",
                "summary": f"Executed `{script_path}` with exit code {exit_code}",
                "text": f"```bash\n{logs[-65000:]}\n```"
            }
        })
