from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "requests.jsonl")

os.makedirs(LOG_DIR, exist_ok=True)


def save_log(log):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")


def load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    logs = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    return logs


requests_log = load_logs()


@app.route(
    "/",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
@app.route(
    "/<path:path>",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
def webhook(path):
    # Dashboard
    if request.method == "GET" and path == "" and not request.args:
        return render_template(
            "index.html",
            logs=requests_log
        )

    query = request.args.to_dict(flat=False)
    cookies = request.cookies.to_dict()
    headers = dict(request.headers)

    body = request.get_data(as_text=True)

    if request.is_json:
        try:
            body = request.get_json()
        except Exception:
            pass

    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        source_ip = forwarded_for.split(",")[0].strip()
    else:
        source_ip = request.remote_addr

    log = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "method": request.method,
        "path": "/" + path,
        "full_url": request.url,
        "ip": source_ip,
        "query": query,
        "cookies": cookies,
        "headers": headers,
        "body": body
    }

    requests_log.append(log)

    save_log(log)

    print("\n" + "=" * 80)
    print("[+] Incoming Request")
    print("=" * 80)

    print(f"Time   : {log['timestamp']}")
    print(f"IP     : {log['ip']}")
    print(f"Method : {log['method']}")
    print(f"Path   : {log['path']}")
    print(f"URL    : {log['full_url']}")

    print("\n[URLSearchParams]")
    print(
        json.dumps(
            log["query"],
            indent=2,
            ensure_ascii=False
        )
    )

    print("\n[Cookies]")
    print(
        json.dumps(
            log["cookies"],
            indent=2,
            ensure_ascii=False
        )
    )

    print("\n[Headers]")
    print(
        json.dumps(
            log["headers"],
            indent=2,
            ensure_ascii=False
        )
    )

    print("\n[Body]")

    if isinstance(log["body"], (dict, list)):
        print(
            json.dumps(
                log["body"],
                indent=2,
                ensure_ascii=False
            )
        )
    else:
        print(log["body"])

    print("=" * 80)

    return jsonify({
        "status": "received",
        "request_number": len(requests_log)
    })


@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(requests_log)


@app.route("/clear", methods=["POST"])
def clear():
    requests_log.clear()

    with open(LOG_FILE, "w", encoding="utf-8"):
        pass

    return jsonify({
        "status": "cleared"
    })


if __name__ == "__main__":
    print(
        """
CalloHook | Pentest Webhook Collector
-------------------------
Dashboard : http://127.0.0.1:8080
Logs      : http://127.0.0.1:8080/logs
Log File  : logs/requests.jsonl
"""
    )

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )