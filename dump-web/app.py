from flask import Flask, request, jsonify, render_template
import os
import subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

DUMP_DIR = "DUMP"
LOG_FILE = "logs/log.txt"

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
    os.makedirs("logs", exist_ok=True)

    dump_path = os.path.join(DUMP_DIR, "uploaded.so")
    lib.save(dump_path)

    # ---- RUN DUMP TOOL ----
    subprocess.run(
        ["python3", "arpit.py", "--mode", mode, "--dump", "uploaded.so"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # ---- READ FINAL log.txt ----
    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "Log file not generated"}), 500

    output = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("===") or not line:
                continue
            # example: 2026-02-06 ... - 0x213360 C0 03 5F D6
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
