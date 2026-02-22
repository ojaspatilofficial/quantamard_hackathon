"""
Simple Flask Development Server - Basic Routes Only
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'
CORS(app)

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

@app.route("/signup", methods=["GET", "POST"])
def signup_route():
    if request.method == "GET":
        return render_template("signup.html")
    return jsonify({"success": True, "message": "Signup successful (demo mode)"}), 200

@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "GET":
        return render_template("login.html")
    return jsonify({"success": True, "message": "Login successful (demo mode)"}), 200

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 CryptexQ - Simple Development Server")
    print("=" * 70)
    print("\n🌐 Access the application at:")
    print("   👉 http://localhost:5000/home")
    print("   👉 http://localhost:5000/")
    print("\n📝 Note: This is a simplified version for UI testing")
    print("   Real-time chat features require the full app.py with SocketIO")
    print("=" * 70)
    print()
    
    from waitress import serve
    print("✅ Server is starting...")
    print("   Press CTRL+C to stop\n")
    serve(app, host="0.0.0.0", port=5000)
