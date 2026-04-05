import os
import json
import shutil
import time
import re
from flask import Flask, render_template, request, redirect, session, send_from_directory

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "uploads"
RECYCLE_FOLDER = "recyclebin"
USERS_FILE = "users.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECYCLE_FOLDER, exist_ok=True)


# ---------- LOAD USERS ----------

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}


# ---------- SAVE USERS ----------

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


# ---------- SIGNUP ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # PASSWORD RULES
        if len(password) < 8:
            return "Password must be at least 8 characters"

        if not re.search("[A-Z]", password):
            return "Password must contain an uppercase letter"

        if not re.search("[a-z]", password):
            return "Password must contain a lowercase letter"

        if not re.search("[0-9]", password):
            return "Password must contain a number"

        if not re.search("[@#$%^&+=!]", password):
            return "Password must contain a special character"

        if username in users:
            return "User already exists"

        users[username] = password
        save_users()

        os.makedirs(os.path.join(UPLOAD_FOLDER, username), exist_ok=True)
        os.makedirs(os.path.join(RECYCLE_FOLDER, username), exist_ok=True)

        return redirect("/login")

    return render_template("signup.html")


# ---------- LOGIN ----------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:

            session["user"] = username
            return redirect("/dashboard")

        else:
            return "Invalid username or password"

    return render_template("login.html")


# ---------- LOGOUT ----------

@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect("/login")


# ---------- DASHBOARD ----------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    user_folder = os.path.join(UPLOAD_FOLDER, user)

    if request.method == "POST":

        file = request.files["file"]

        if file and file.filename != "":
            file.save(os.path.join(user_folder, file.filename))

    files = os.listdir(user_folder)

    return render_template("dashboard.html", files=files)


# ---------- DOWNLOAD ----------

@app.route("/download/<filename>")
def download(filename):

    if "user" not in session:
        return redirect("/login")

    user_folder = os.path.join(UPLOAD_FOLDER, session["user"])

    return send_from_directory(user_folder, filename, as_attachment=True)


# ---------- DELETE → RECYCLE BIN ----------

@app.route("/delete/<filename>")
def delete(filename):

    user = session["user"]

    src = os.path.join(UPLOAD_FOLDER, user, filename)
    dst = os.path.join(RECYCLE_FOLDER, user, filename)

    shutil.move(src, dst)

    return redirect("/dashboard")


# ---------- RECYCLE BIN PAGE ----------

@app.route("/recycle")
def recycle():

    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    recycle_folder = os.path.join(RECYCLE_FOLDER, user)

    files = os.listdir(recycle_folder)

    return render_template("recycle.html", files=files)


# ---------- RESTORE FILE ----------

@app.route("/restore/<filename>")
def restore(filename):

    user = session["user"]

    src = os.path.join(RECYCLE_FOLDER, user, filename)
    dst = os.path.join(UPLOAD_FOLDER, user, filename)

    shutil.move(src, dst)

    return redirect("/recycle")


# ---------- PERMANENT DELETE ----------

@app.route("/permanent_delete/<filename>")
def permanent_delete(filename):

    user = session["user"]

    file_path = os.path.join(RECYCLE_FOLDER, user, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect("/recycle")


# ---------- AUTO DELETE AFTER 30 DAYS ----------

def auto_delete():

    now = time.time()

    for user in os.listdir(RECYCLE_FOLDER):

        user_folder = os.path.join(RECYCLE_FOLDER, user)

        for file in os.listdir(user_folder):

            path = os.path.join(user_folder, file)

            if os.stat(path).st_mtime < now - 30 * 86400:
                os.remove(path)


@app.before_request
def cleanup():
    auto_delete()


# ---------- RUN APP ----------

if __name__ == "__main__":
    app.run(debug=True)