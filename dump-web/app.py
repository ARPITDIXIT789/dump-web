import os
import json
import subprocess
import requests
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

UPLOAD_DIR = "uploads"
LOG_DIR = "logs"
LIB_DIR = "libs"

LOG_FILE = os.path.join(LOG_DIR, "log.txt")
JSON_FILE = os.path.join(LOG_DIR, "result.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ================= TELEGRAM CONFIG =================
TELEGRAM_BOT_TOKEN = "7567902538:AAHK9Vap_6u3hfEA6zBIRA-pBpKaS-D_RzQ"
TELEGRAM_CHAT_ID = "5367104890"

def send_log_to_telegram(log_path):
    if not os.path.exists(log_path):
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(log_path, "rb") as f:
        requests.post(
            url,
            data={"chat_id": TELEGRAM_CHAT_ID},
            files={"document": f},
            timeout=10
        )

# ================= TOOL CONFIG =================
TOOLS = {
    "anogs": {
        "orig": os.path.join(LIB_DIR, "libanogs.so"),
        "size": 0x524680
    },
    "hdmpve": {
        "orig": os.path.join(LIB_DIR, "libhdmpve.so"),
        "size": 0x472394
    },
    "ue4": {
        "orig": os.path.join(LIB_DIR, "libue4.so"),
        "size": 0xC0E1000
    }
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    mode = request.form.get("mode")
    lib = request.files.get("lib")

    if mode not in TOOLS:
        return jsonify({"error": "Invalid mode"}), 400

    if not lib or not lib.filename.endswith(".so"):
        return jsonify({"error": "Only .so files allowed"}), 400

    # 🔥 OLD LOG DELETE (FAKE OFFSET FIX)
    for f in [LOG_FILE, JSON_FILE]:
        if os.path.exists(f):
            os.remove(f)

    dump_path = os.path.join(UPLOAD_DIR, lib.filename)
    lib.save(dump_path)

    cfg = TOOLS[mode]

    subprocess.run([
        "python3",
        "arpit.py",
        cfg["orig"],
        dump_path,
        hex(cfg["size"]),
        LOG_FILE,
        JSON_FILE
    ])

    # 📲 SEND LOG TO TELEGRAM
    send_log_to_telegram(LOG_FILE)

    with open(JSON_FILE) as f:
        return jsonify(json.load(f))

@app.route("/download-log")
def download_log():
    if not os.path.exists(LOG_FILE):
        return {"error": "Log not found"}, 404
    return send_file(LOG_FILE, as_attachment=True, download_name="dump_log.txt")

if __name__ == "__main__":
    app.run()
