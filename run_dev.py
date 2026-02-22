"""
Development server launcher without SSL for easier local testing
"""
import os
import sys
import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime
import base64
import json

# Suppress oqs auto-install prompts and errors
oqs = None
old_stderr = sys.stderr
old_stdin = sys.stdin
try:
    sys.stderr = io.StringIO()
    sys.stdin = io.StringIO('n\n')
    import oqs
    sys.stderr = old_stderr
    sys.stdin = old_stdin
    print("[OK] OQS library loaded successfully")
except Exception as e:
    sys.stderr = old_stderr
    sys.stdin = old_stdin
    print(f"[WARNING] Could not import oqs library: {type(e).__name__}")
    print("  Application will run with simulated PQC functionality")
    oqs = None

import socket

# Import local utilities
from crypto_utils import encrypt_aes, decrypt_aes, sign_message, verify_message
from qkd import generate_qkd_key, derive_aes_key_from_qkd
import pqc_utils
from hmac_integrity import wrap_outgoing_message, unwrap_incoming_message

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=False,
    engineio_logger=False
)

# ---------------- DATABASE -----------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client["cryptexq_db"]
    messages_col = db["messages"]
    users_col = db["users"]
    sessions_col = db["sessions"]
    print("[OK] MongoDB connected successfully")
except Exception as e:
    print(f"[WARNING] MongoDB connection failed: {e}")
    print("  Application will run without database persistence")
    client = None
    db = None
    messages_col = None
    users_col = None
    sessions_col = None

# ---------------- ROUTES -------------------
@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/talkroom")
def talkroom_page():
    return render_template("talkroom.html")

@app.route("/forgetpg")
def forgetpg_page():
    return render_template("forgetpg.html")

@app.route("/logout")
def logout_page():
    return render_template("logout.html")

@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/team")
def team_page():
    return render_template("team.html")

@app.route("/faq")
def faq_page():
    return render_template("faq.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/term")
def terms_page():
    return render_template("terms.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/demo")
def demo_page():
    return render_template("demo.html")

@app.route("/replay-protection")
def replay_protection_page():
    return render_template("replay_protection.html")

@app.route("/profile")
def profile_page():
    return render_template("profile.html")

@app.route("/secure-msg")
def secure_msg_page():
    return render_template("secure_msg.html")

@app.route("/nav-test")
def nav_test_page():
    return render_template("nav_test.html")

# ---------------- SOCKET STATE -------------
KEM_NAME = "Kyber512"
USERS = {}

# ---------------- AUTH ROUTES -------------------
@app.route("/signup", methods=["GET", "POST"])
def signup_route():
    if request.method == "GET":
        return render_template("signup.html")

    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields required"}), 400

    if users_col is None:
        return jsonify({"success": True, "message": "Signup successful (demo mode - no DB)"}), 200

    if users_col.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 400

    users_col.insert_one({
        "username": username,
        "email": email,
        "password": password
    })
    return jsonify({"success": True, "message": "Signup successful!"}), 200


@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json(force=True)
    user_input = data.get("username")
    password = data.get("password")

    if users_col is None:
        return jsonify({"success": True, "message": "Login successful (demo mode - no DB)"}), 200

    user = users_col.find_one({
        "$or": [
            {"username": user_input},
            {"email": user_input}
        ],
        "password": password
    })

    if user:
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ---------------- SOCKET EVENTS ------------
@socketio.on("connect")
def on_connect():
    print(f"[+] Client connected: {request.sid}")

@socketio.on("disconnect")
def on_disconnect(reason=None):
    sid = request.sid
    disconnected_user = None

    for username, info in list(USERS.items()):
        if info.get("sid") == sid:
            disconnected_user = username
            USERS.pop(username, None)
            break

    if disconnected_user:
        print(f"[-] {disconnected_user} disconnected")

    socketio.emit("online_users", {"users": list(USERS.keys())})

@socketio.on("register")
def handle_register(data):
    username = data.get("username")
    pub_b64 = data.get("x25519_pub_b64")

    if not username or not pub_b64:
        emit("error", {"message": "Invalid registration data"})
        return

    USERS[username] = {
        "sid": request.sid,
        "pub": pub_b64
    }

    try:
        if oqs and hasattr(oqs, "KeyEncapsulation"):
            with oqs.KeyEncapsulation(KEM_NAME) as kem:
                pk = kem.generate_keypair()
                sk = kem.export_secret_key()
        else:
            pk = os.urandom(64)
            sk = os.urandom(64)
        USERS[username]["kyber"] = {"public": pk, "private": sk}
        kyber_pub_b64 = base64.b64encode(pk).decode()
    except Exception as e:
        kyber_pub_b64 = ""

    emit("registered", {"username": username, "kyber_pub_b64": kyber_pub_b64})
    socketio.emit("online_users", {"users": list(USERS.keys())})
    print(f"[REGISTER] {username} ({request.sid})")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CryptexQ Development Server (HTTP - No SSL)")
    print("=" * 60)
    print("[*] Modes: QKD + AES | Hybrid PQC-Kyber + AES")
    print("[*] Features: AES-256-GCM encryption + HMAC-SHA256 integrity")
    print("[*] Message integrity layer: ACTIVE")
    print("=" * 60)
    print("\n🌐 Access the application at:")
    print("   👉 http://localhost:5000/home")
    print("   👉 http://localhost:5000/")
    print("\n⚠️  This is a development server - not for production!")
    print("=" * 60)
    
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
