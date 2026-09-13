import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, Response
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017")
MONGO_DB = os.environ.get("MONGO_DB", "telegram_transfer_bot")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]


def compute_stats():
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    total_transferred = db.transferred_messages.count_documents({})
    transferred_24h = db.transferred_messages.count_documents(
        {"copied_at": {"$gte": last_24h}}
    )
    active_jobs = db.jobs.count_documents({"status": "running"})
    failed_24h = db.logs.count_documents(
        {"level": "ERROR", "timestamp": {"$gte": last_24h}}
    )

    return {
        "total_transferred": total_transferred,
        "transferred_24h": transferred_24h,
        "active_jobs": active_jobs,
        "failed_24h": failed_24h,
    }


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify(status="ok"), 200
    except Exception as e:
        return jsonify(status="error", detail=str(e)), 503


@app.get("/stats")
def stats():
    return jsonify(compute_stats())


@app.get("/metrics")
def metrics():
    s = compute_stats()
    lines = [
        "# HELP bot_messages_transferred_total Total messages transferred",
        "# TYPE bot_messages_transferred_total counter",
        f"bot_messages_transferred_total {s['total_transferred']}",
        "# HELP bot_messages_transferred_24h Messages transferred in last 24h",
        "# TYPE bot_messages_transferred_24h gauge",
        f"bot_messages_transferred_24h {s['transferred_24h']}",
        "# HELP bot_active_jobs Currently running jobs",
        "# TYPE bot_active_jobs gauge",
        f"bot_active_jobs {s['active_jobs']}",
        "# HELP bot_failed_24h Errors logged in last 24h",
        "# TYPE bot_failed_24h gauge",
        f"bot_failed_24h {s['failed_24h']}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", 8000))
    app.run(host="0.0.0.0", port=port)
