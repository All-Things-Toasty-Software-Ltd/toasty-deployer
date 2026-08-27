from flask import Blueprint, jsonify

from app.db import get_connection

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/owners', methods=['GET'])
def list_owners():
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT owner FROM runs").fetchall()
    return jsonify({"owners": [r['owner'] for r in rows]})


@api_bp.route('/owners/<owner>', methods=['GET'])
def list_repos(owner):
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT repo FROM runs WHERE owner=?", (owner,)).fetchall()
    return jsonify({"owner": owner, "repositories": [r['repo'] for r in rows]})


@api_bp.route('/owners/<owner>/<repo>', methods=['GET'])
def list_runs(owner, repo):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, commit_sha, status, exit_code, created_at FROM runs WHERE owner=? AND repo=? ORDER BY id DESC",
            (owner, repo)
        ).fetchall()
    return jsonify({"owner": owner, "repo": repo, "runs": [dict(r) for r in rows]})


@api_bp.route('/owners/<owner>/<repo>/<int:run_id>', methods=['GET'])
def get_run(owner, repo, run_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, owner, repo, commit_sha, status, exit_code, logs, created_at FROM runs WHERE owner=? AND repo=? AND id=?",
            (owner, repo, run_id)
        ).fetchone()
    if not row:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(dict(row))
