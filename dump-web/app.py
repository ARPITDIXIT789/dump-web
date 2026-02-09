from flask import Flask, request, jsonify, render_template, send_file
import os
import subprocess
import requests

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

DUMP_DIR = "DUMP"
LOG_DIR = "logs"
LOG_FILE = "logs/log.txt"

# ================= TELEGRAM CONFIG =================
TELEGRAM_BOT_TOKEN = "7567902538:AAHK9Vap_6u3hfEA6zBIRA-pBpKaS-D_RzQ"
TELEGRAM_CHAT_ID = "5367104890"

def send_log_to_telegram():
    if not os.path.exists(LOG_FILE):
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(LOG_FILE, "rb") as f:
        requests.post(
            url,
            data={"chat_id": TELEGRAM_CHAT_ID},
            files={"document": f},
            timeout=10
        )

# ================= ROUTES =================

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    lib = request.files.get("lib")
    mode = request.form.get("mode")

    if not lib or not lib.filename.endswith(".so"):
        return jsonify({"error": "Only .so files allowed"}), 400

    os.makedirs(DUMP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    dump_path = os.path.join(DUMP_DIR, "uploaded.so")
    lib.save(dump_path)

    # ---- RUN DUMP TOOL ----
    subprocess.run(
        ["python3", "arpit.py", "--mode", mode, "--dump", "uploaded.so"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # ---- SEND LOG TO TELEGRAM ----
    send_log_to_telegram()

    # ---- READ log.txt ----
    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "Log file not generated"}), 500

    output = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("===") or not line:
                continue
            try:
                _, data = line.split(" - ", 1)
                output.append(data)
            except ValueError:
                continue

    return jsonify({
        "status": "success",
        "mode": mode,
        "results": output
    })

# ===== LOG DOWNLOAD =====
@app.route("/download-log")
def download_log():
    if not os.path.exists(LOG_FILE):
        return {"error": "Log not found"}, 404
    return send_file(LOG_FILE, as_attachment=True, download_name="dump_log.txt")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
