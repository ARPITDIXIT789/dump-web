from flask import Flask, request, jsonify, render_template
import os, subprocess, json

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    lib = request.files.get("lib")
    mode = request.form.get("mode")

    if not lib or not lib.filename.endswith(".so"):
        return jsonify({"error": "Only .so allowed"}), 400

    base_map = {
        "anogs": "BASE_LIBS/libanogs.so",
        "hdmpve": "BASE_LIBS/libhdmpve.so"
    }

    if not os.path.exists(base_map[mode]):
        return jsonify({"error": "Base library not installed on server"}), 500

    os.makedirs("DUMP", exist_ok=True)
    lib.save("DUMP/uploaded.so")

    subprocess.run(
        ["python3", "arpit.py", "--mode", mode, "--dump", "uploaded.so"]
    )

    with open("logs/result.json") as f:
        data = json.load(f)

    return jsonify(data)

app.run(host="0.0.0.0", port=5000)
