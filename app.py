from flask import (
    Flask, request, redirect, url_for,
    render_template, send_from_directory, jsonify, flash
)
import os
from werkzeug.utils import secure_filename

# ── Config ────────────────────────────────────────────────────────────
UPLOAD_FOLDER = "storage_uploads"
ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif",
    "wav", "mp3", "mp4", "json", "csv"
}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "super‑secret‑change‑me"        # for flash messages

# ── Helpers ───────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ── Routes ────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return redirect(url_for("storage"))


@app.route("/storage", methods=["GET"])
def storage():
    files = sorted(os.listdir(app.config["UPLOAD_FOLDER"]))
    return render_template("index.html", files=files)


# ── Upload route ───────────────────────────────────────────
@app.route("/upload_file", methods=["POST"])
def upload_file():          # ← rename from `upload` to `upload_file`
    """
    Saves an uploaded file, then redirects back to /storage.
    """
    if "file" not in request.files:
        flash("No file field")
        return redirect(url_for("storage"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(url_for("storage"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        flash(f"Uploaded {filename}")
    else:
        flash("File type not allowed")

    return redirect(url_for("storage"))


@app.route("/storage/files/<path:filename>")
def uploaded_file(filename):
    """Stream file to the client."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)


@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        flash(f"Deleted: {filename}")
    except FileNotFoundError:
        flash("File not found")
    return redirect(url_for("storage"))


# Optional JSON API so Zara can query the store programmatically
@app.route("/api/files")
def api_files():
    files = sorted(os.listdir(app.config["UPLOAD_FOLDER"]))
    return jsonify(files)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
