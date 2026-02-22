"""
Diagnostic server to find the issue
"""
import sys
import traceback

try:
    print("Step 1: Importing Flask...")
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
    print("✅ Imports successful")

    print("Step 2: Creating Flask app...")
    app = Flask(__name__)
    app.secret_key = 'dev-secret-key'
    CORS(app)
    print("✅ Flask app created")

    print("Step 3: Registering routes...")
    @app.route("/")
    def index_page():
        return render_template("index.html")

    @app.route("/home")
    def home_page():
        return render_template("home.html")

    print("✅ Routes registered")

    print("Step 4: Starting server...")
    from waitress import serve
    print("=" * 60)
    print("🌐 Server starting on http://localhost:5000")
    print("   Try: http://localhost:5000/home")
    print("=" * 60)
    serve(app, host="127.0.0.1", port=5000, threads=4)
    
except Exception as e:
    print("\n❌ ERROR OCCURRED:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    input("\nPress Enter to exit...")
