# -*- coding: utf-8 -*-
# Part of Toasty Deployer. See LICENSE file for full copyright and licensing details.

import os
import threading

from flask import Blueprint, request, jsonify

from app.worker import verify_signature, execute_deployment
from config import Config

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json or {}
    if "zen" in data:
        return jsonify({"message": "Pong"}), 200

    owner = data.get('repository', {}).get('owner', {}).get('login')
    repo = data.get('repository', {}).get('name')
    commit_sha = data.get('after') or data.get('head_commit', {}).get('id') or "HEAD"
    installation_id = data.get('installation', {}).get('id', 0)

    if not owner or not repo:
        return jsonify({"message": "Ignored"}), 200

    script_path = os.path.join(Config.REPOS_DIR, owner, f"{repo}.sh")

    thread = threading.Thread(
        target=execute_deployment,
        args=(owner, repo, commit_sha, installation_id, script_path)
    )
    thread.start()

    return jsonify({"status": "processing"}), 200
