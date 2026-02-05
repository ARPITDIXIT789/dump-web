from flask import Flask, request, jsonify, render_template
import os, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

DUMP_DIR = "DUMP"
LOG_FILE = "logs/uploaded_log.txt"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    lib = request.files.get("lib")
    mode = request.form.get("mode")

    if not lib or not lib.filename.endswith(".so"):
        return jsonify({"error": "Only .so files allowed"}), 400

    filename = "uploaded.so"
    path = os.path.join(DUMP_DIR, filename)
    lib.save(path)

    subprocess.run(
        ["python3", "arpit.py", "--mode", mode, "--dump", filename],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    result = {}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            for line in f:
                if " - " in line:
                    _, data = line.strip().split(" - ", 1)
                    result[data.split()[0]] = " ".join(data.split()[1:])

    return jsonify(result)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    os.makedirs("DUMP", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
