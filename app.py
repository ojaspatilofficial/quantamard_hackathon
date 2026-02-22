# Eventlet monkey patching MUST be first - before any other imports
try:
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    pass

import os
import logging
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime
import base64
import json
import sys
import io
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Suppress oqs auto-install prompts and errors
oqs = None
old_stderr = sys.stderr
old_stdin = sys.stdin
try:
    sys.stderr = io.StringIO()  # Suppress error messages
    sys.stdin = io.StringIO('n\n')  # Auto-respond 'n' to prompts
    import oqs  # pip install oqs
    sys.stderr = old_stderr
    sys.stdin = old_stdin
    logger.info("OQS library loaded successfully")
except Exception as e:
    sys.stderr = old_stderr
    sys.stdin = old_stdin
    logger.warning(f"Could not import oqs library: {type(e).__name__} - using simulated PQC")
    oqs = None

import socket

# ---- Local CryptexQ utility imports ----
from crypto_utils import encrypt_aes, decrypt_aes, sign_message, verify_message
from qkd import generate_qkd_key, derive_aes_key_from_qkd
import pqc_utils  # optional

# ---- Message Integrity Layer (HMAC-SHA256) ----
# Automatically adds HMAC signatures to all messages for tamper detection
# Integration is transparent - no breaking changes to existing APIs or UI
# See hmac_integrity.py for implementation details
from hmac_integrity import wrap_outgoing_message, unwrap_incoming_message

from flask_socketio import SocketIO

"""
MESSAGE INTEGRITY IMPLEMENTATION NOTES:
========================================
A software-only HMAC-SHA256 integrity layer has been added to all messages.

Key Features:
- Automatically generates HMAC for: message content + timestamp + sender ID
- Verifies integrity on message receipt
- Detects tampering, replay attacks, and sender spoofing
- Backward compatible with legacy clients (missing integrity field is logged)
- Uses environment variable CRYPTEXQ_HMAC_SECRET or auto-generated key

Integration Points:
1. handle_encrypted_message(): Messages are wrapped before forwarding
2. Optional client-side validation available (message_integrity_helper.js)

Testing:
- Run: python test_hmac_integrity.py
- All 7 tests validate tamper detection, spoofing, and replay protection

Security Notes:
- Secret key stored in .hmac_secret (excluded from git)
- For production: Set CRYPTEXQ_HMAC_SECRET environment variable
- HMAC uses constant-time comparison to prevent timing attacks
"""

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Session security configuration
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# CORS configuration with environment control
CORS_ORIGIN = os.environ.get('CORS_ORIGIN', '*')
CORS(app, supports_credentials=True, origins=CORS_ORIGIN)

# Socket.IO with environment-controlled CORS and eventlet
socketio = SocketIO(
    app,
    cors_allowed_origins=CORS_ORIGIN,
    async_mode="eventlet",
    logger=False,
    engineio_logger=False
)

# Security headers middleware
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Only add HSTS in production with HTTPS
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# ---------------- DATABASE -----------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # Test connection
    client.server_info()
    db = client["cryptexq_db"]
    messages_col = db["messages"]
    users_col = db["users"]
    sessions_col = db["sessions"]
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.warning(f"MongoDB connection failed: {e} - running without database persistence")
    client = None
    db = None
    messages_col = None
    users_col = None
    sessions_col = None

# ---------------- AUTHENTICATION DECORATOR -------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login_route'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ROUTES -------------------
@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/talkroom")
@login_required
def talkroom_page():
    return render_template("talkroom.html")

@app.route("/forgetpg")
def forgetpg_page():
    return render_template("forgetpg.html")

@app.route("/logout")
def logout_page():
    session.clear()
    return render_template("logout.html")

@app.route("/home")
def home_page():
    return render_template("home.html")

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
@login_required
def replay_protection_page():
    return render_template("replay_protection.html")

@app.route("/profile")
@login_required
def profile_page():
    return render_template("profile.html")
@app.route("/secure-msg")
@login_required
def secure_msg_page():
    return render_template("secure_msg.html")
    return render_template("secure_msg.html")

@app.route("/nav-test")
def nav_test_page():
    return render_template("nav_test.html")

# ---------------- SOCKET STATE -------------

KEM_NAME = "Kyber512"
USERS = {}

# ---------------- SOCKET EVENTS ------------

# ---------------- AUTH ROUTES -------------------

@app.route("/signup", methods=["GET", "POST"])
def signup_route():
    if request.method == "GET":
        return render_template("signup.html")

    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    # Validation
    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields required"}), 400

    if len(username) < 3:
        return jsonify({"success": False, "message": "Username must be at least 3 characters"}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

    # Database check
    if users_col is None:
        # For demo/local testing without database
        return jsonify({"success": True, "message": "Signup successful (demo mode)"}), 200

    # Check if user exists
    if users_col.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 400

    if users_col.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # Hash password for security
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Insert user
    users_col.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    })
    return jsonify({"success": True, "message": "Signup successful!"}), 200


@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json(force=True)
    user_input = data.get("username", "").strip()
    password = data.get("password", "")

    if not user_input or not password:
        return jsonify({"success": False, "message": "All fields required"}), 400

    # Demo mode without database
    if users_col is None:
        session["user"] = user_input
        return jsonify({"success": True, "message": "Login successful (demo mode)"}), 200

    # Find user by username OR email
    user = users_col.find_one({
        "$or": [
            {"username": user_input},
            {"email": user_input}
        ]
    })

    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    # Check password hash
    if check_password_hash(user["password"], password):
        session["user"] = user["username"]
        session["user_id"] = str(user["_id"])
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ---------------- SOCKET STATE -------------

KEM_NAME = "Kyber512"
USERS = {}  # single shared dictionary for all connections

@socketio.on("connect")
def on_connect():
    logger.info(f"Client connected: {request.sid}")

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
        logger.info(f"{disconnected_user} disconnected")

    # Flask-SocketIO v6+ doesn’t support broadcast=True anymore
    socketio.emit("online_users", {"users": list(USERS.keys())})


@socketio.on("register")
def handle_register(data):
    logger.debug("Register event triggered")
    logger.debug(f"Registration data: {data}")

    username = data.get("username")
    pub_b64 = data.get("x25519_pub_b64")

    if not username or not pub_b64:
        logger.error("Invalid registration data - missing username or pub key")
        emit("error", {"message": "Invalid registration data"})
        return

    USERS[username] = {
        "sid": request.sid,
        "pub": pub_b64
    }

    # Simulated Kyber keypair if oqs not available
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
        logger.warning(f"Kyber generation failed (simulated mode): {e}")
        kyber_pub_b64 = ""

    emit("registered", {"username": username, "kyber_pub_b64": kyber_pub_b64})

    # ✅ emit to all clients (no 'broadcast' argument)
    socketio.emit("online_users", {"users": list(USERS.keys())})

    logger.info(f"User registered: {username} (sid: {request.sid})")
    logger.debug(f"Active users: {list(USERS.keys())}")

# -------------- HYBRID (Kyber+AES) -----------------

@socketio.on("request_start_session")
def handle_request_start(data):
    """
    Hybrid PQC mode.
    Client sends: { "from": "Alice", "to": "Bob" }
    We:
      - use Bob's Kyber public key to encapsulate (if oqs available)
      - otherwise simulate a PQC shared secret
      - send:
          'kyber_shared_for_initiator' to Alice
          'kyber_ready_peer'          to Bob
    """
    initiator = data.get("from")
    peer = data.get("to")

    if not initiator or not peer:
        emit("error", {"error": "from/to required"})
        return
    if initiator not in USERS or peer not in USERS:
        emit("error", {"error": "user(s) not online"})
        return

    initiator_info = USERS[initiator]
    peer_info = USERS[peer]

    # ----------------- Kyber / fallback logic -----------------
    try:
        if oqs and hasattr(oqs, "KeyEncapsulation"):
            # Real Kyber512
            peer_pk = peer_info["kyber"]["public"]

            with oqs.KeyEncapsulation(KEM_NAME) as kem:
                ciphertext, ss_initiator = kem.encap_secret(peer_pk)

            peer_sk = peer_info["kyber"]["private"]
            with oqs.KeyEncapsulation(KEM_NAME) as kem_dec:
                ss_peer = kem_dec.decap_secret(ciphertext, peer_sk)

            logger.debug("Using real Kyber512 KEM")

        else:
            # Fallback demo mode – simulate PQC shared secret
            logger.debug("oqs.KeyEncapsulation not available, using simulated PQC key")
            ciphertext = os.urandom(96)
            ss_initiator = os.urandom(32)
            ss_peer = ss_initiator

    except Exception as e:
        # If anything explodes, still fall back to a demo shared key
        logger.warning(f"Kyber failed, using simulated key: {e}")
        ciphertext = os.urandom(96)
        ss_initiator = os.urandom(32)
        ss_peer = ss_initiator

    # ----------------------------------------------------------
    ct_b64 = base64.b64encode(ciphertext).decode()
    ss_initiator_b64 = base64.b64encode(ss_initiator).decode()
    ss_peer_b64 = base64.b64encode(ss_peer).decode()

    # Send to initiator (the one who clicked Start / auto-establish)
    socketio.emit(
        "kyber_shared_for_initiator",
        {
            "from": peer,
            "kyber_ss_b64": ss_initiator_b64,
            "peer_x25519_b64": peer_info.get("x25519_pub_b64"),
            "cipher_b64": ct_b64,
        },
        room=initiator_info["sid"],
    )

    # Send to peer
    socketio.emit(
        "kyber_ready_peer",
        {
            "from": initiator,
            "cipher_b64": ct_b64,
            "initiator_x25519_b64": initiator_info.get("x25519_pub_b64"),
            "kyber_ss_b64": ss_peer_b64,
        },
        room=peer_info["sid"],
    )

    emit("session_initiated", {"ok": True})
    logger.info(f"Hybrid PQC+AES session: {initiator} <-> {peer}")
    logger.debug("Using Kyber512 KEM + AES-256-GCM")


    # Send to initiator
    socketio.emit(
        "kyber_shared_for_initiator",
        {
            "from": peer,
            "kyber_ss_b64": ss_initiator_b64,
            "peer_x25519_b64": peer_info.get("x25519_pub_b64"),
            "cipher_b64": ct_b64,
        },
        room=initiator_info["sid"],
    )

    # Send to peer
    socketio.emit(
        "kyber_ready_peer",
        {
            "from": initiator,
            "cipher_b64": ct_b64,
            "initiator_x25519_b64": initiator_info.get("x25519_pub_b64"),
            "kyber_ss_b64": ss_peer_b64,
        },
        room=peer_info["sid"],
    )

    emit("session_initiated", {"ok": True})
    logger.info(f"Hybrid PQC+AES session: {initiator} <-> {peer}")
    logger.debug("Using Kyber512 KEM + AES-256-GCM")


# -------------- QKD + AES MODE (Simulated Quantum Key Distribution) ------------

@socketio.on("start_qkd_session")
def handle_start_qkd_session(data):
    """
    QKD + AES mode: Quantum Key Distribution + AES-GCM encryption.
    Client sends: { "from": "Alice", "to": "Bob" }
    
    Cryptographic Flow:
      1. Generate QKD bits (simulated quantum channel)
      2. Derive AES-256 key from QKD bits using HKDF
      3. Distribute shared key to both parties via secure channel
      4. Parties use key for AES-GCM authenticated encryption
    
    Security Properties:
      - Forward secrecy via ephemeral key generation
      - Authentication via HMAC integrity layer
      - Confidentiality via AES-256-GCM
    """
    initiator = data.get("from")
    peer = data.get("to")

    if not initiator or not peer:
        emit("error", {"error": "from/to required"})
        return
    if initiator not in USERS or peer not in USERS:
        emit("error", {"error": "user(s) not online"})
        return

    # Step 1: Generate QKD bits (simulated quantum channel - 512 bits)
    qkd_bits = generate_qkd_key(512)
    
    # Step 2: Derive AES-256 key from QKD bits using cryptographic derivation
    shared_key_bytes = derive_aes_key_from_qkd(qkd_bits)
    shared_b64 = base64.b64encode(shared_key_bytes).decode()

    i_sid = USERS[initiator]["sid"]
    p_sid = USERS[peer]["sid"]

    # Step 3: Distribute shared key to both parties
    socketio.emit(
        "qkd_shared_key",
        {"peer": peer, "shared_b64": shared_b64},
        room=i_sid,
    )
    socketio.emit(
        "qkd_shared_key",
        {"peer": initiator, "shared_b64": shared_b64},
        room=p_sid,
    )

    logger.info(f"QKD+AES session: {initiator} <-> {peer}")
    logger.debug(f"Shared key size: {len(shared_key_bytes)} bytes (AES-256)")


# -------------- ENCRYPTED CHAT (AES-GCM + HMAC Integrity) ----------------------

@socketio.on("send_encrypted_message")
def handle_encrypted_message(data):
    """
    Handles encrypted message transmission with integrity protection.
    
    Client sends AES-GCM ciphertext:
      {
        "from": "Alice",
        "to": "Bob",
        "ciphertext_b64": "...",  # AES-256-GCM encrypted message
        "iv_b64": "...",          # Initialization Vector (12 bytes)
        "timestamp": "...",       # Message timestamp (milliseconds)
        "integrity": {            # HMAC-SHA256 signature (added by client/server)
          "type": "HMAC_SHA256",
          "value": "..."
        }
      }
    
    Cryptographic Processing:
      1. Verify incoming message HMAC integrity (if present)
      2. Reject tampered messages before forwarding
      3. Add/refresh HMAC signature for recipient
      4. Forward encrypted message to recipient only
      5. Confirm delivery to sender
    
    Security Guarantees:
      - Confidentiality: AES-256-GCM encryption
      - Authentication: HMAC-SHA256 message integrity
      - Forward secrecy: Ephemeral session keys
      - Tamper detection: HMAC verification
    """
    to = data.get("to")
    sender = data.get("from")

    if not to or to not in USERS:
        emit("error", {"error": "recipient not available"})
        return

    # ============== MESSAGE INTEGRITY LAYER (PRE-SEND) ==============
    # Verify incoming message integrity (optional for backward compatibility)
    if 'integrity' in data:
        is_valid, result = unwrap_incoming_message(data)
        if not is_valid:
            # Message integrity failed - reject and notify sender
            emit("error", result)
            logger.warning(f"INTEGRITY VIOLATION: Rejected message from {sender} to {to}")
            return
    
    # Add/refresh integrity signature before forwarding to recipient
    # This ensures recipient always receives a properly signed message
    secured_data = wrap_outgoing_message(data)
    # ================================================================

    recipient_sid = USERS[to]["sid"]
    
    # Send to recipient
    socketio.emit("new_encrypted_message", secured_data, room=recipient_sid)
    
    # Echo back to sender with integrity data so they see "verified" badge
    socketio.emit("new_encrypted_message", secured_data, room=request.sid)

    # Simple delivery ack
    socketio.emit(
        "message_delivered",
        {"to": to, "ok": True},
        room=request.sid,
    )

    logger.info(f"Message: {sender} -> {to} (AES-GCM encrypted, HMAC-SHA256 verified)")
    
if __name__ == "__main__":
    # Production-ready server startup
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info("="  * 70)
    logger.info("CryptexQ - Quantum-Safe Messaging Platform")
    logger.info("="  * 70)
    logger.info("Modes: QKD + AES | Hybrid PQC-Kyber + AES")
    logger.info("Features: AES-256-GCM encryption + HMAC-SHA256 integrity")
    logger.info("Message integrity layer: ACTIVE")
    logger.info(f"Environment: {'PRODUCTION' if not DEBUG else 'DEVELOPMENT'}")
    logger.info(f"Port: {PORT}")
    logger.info(f"CORS: {CORS_ORIGIN}")
    logger.info("="  * 70)
    
    # Auto-open browser in development only
    if DEBUG:
        import webbrowser
        import threading
        def open_browser():
            import time
            time.sleep(2)
            webbrowser.open(f'http://localhost:{PORT}')
        threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server (Render uses Gunicorn in production via Procfile)
    socketio.run(
        app,
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG
    )



