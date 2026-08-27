# -*- coding: utf-8 -*-
# Part of Toasty Deployer. See LICENSE file for full copyright and licensing details.

import os

class Config:
    APP_ID = os.environ.get("APP_ID")
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
    PRIVATE_KEY_PATH = os.environ.get("PRIVATE_KEY_PATH")
    DB_PATH = os.environ.get("DB_PATH", "/opt/toasty-deployer/deployments.db")
    REPOS_DIR = os.environ.get("REPOS_DIR", "/repos")