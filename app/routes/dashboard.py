from flask import Blueprint, render_template

from app.db import get_connection

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/deployments', methods=['GET'])
def show_dashboard():
    with get_connection() as conn:
        runs = conn.execute(
            "SELECT id, owner, repo, commit_sha, status, exit_code, created_at, logs FROM runs ORDER BY id DESC LIMIT 50").fetchall()
    return render_template('dashboard.html', runs=runs)
