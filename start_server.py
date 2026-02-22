#!/usr/bin/env python3
"""
CryptexQ Server Launcher
Checks requirements and starts the Flask server
"""

import sys
import os
import subprocess

print("=" * 60)
print("CryptexQ Server Launcher")
print("=" * 60)
print()

# Check Python version
print(f"✓ Python {sys.version}")

# Check if we're in the correct directory
if not os.path.exists("app.py"):
    print("✗ ERROR: app.py not found!")
    print("  Please run this script from the EDI-SY1 directory")
    sys.exit(1)

print("✓ Found app.py")

# Check if templates directory exists
if not os.path.exists("templates"):
    print("✗ ERROR: templates directory not found!")
    sys.exit(1)

print("✓ Found templates directory")

# Check required modules
required_modules = ['flask', 'flask_cors', 'flask_socketio', 'pymongo']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
        print(f"✓ {module} installed")
    except ImportError:
        print(f"✗ {module} NOT installed")
        missing_modules.append(module)

if missing_modules:
    print()
    print("=" * 60)
    print("MISSING DEPENDENCIES!")
    print("=" * 60)
    print()
    print("Please install missing modules:")
    print(f"pip install {' '.join(missing_modules)}")
    print()
    response = input("Would you like to install them now? (y/n): ")
    if response.lower() == 'y':
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_modules)
    else:
        sys.exit(1)

# Check SSL certificates
cert_exists = os.path.exists("certs/server/server.crt")
key_exists = os.path.exists("certs/server/server.key")

if cert_exists and key_exists:
    print("✓ SSL certificates found")
else:
    print("⚠ Warning: SSL certificates not found")
    print("  Server may fail to start")
    print("  Generate certificates by running: python certs/server/generate_server_cert.py")

print()
print("=" * 60)
print("Starting Flask Server...")
print("=" * 60)
print()
print("Once the server starts, open your browser and navigate to:")
print()
print("  🌐 https://localhost:5000/home")
print()
print("Note: You'll see an SSL warning - click 'Advanced' and 'Proceed'")
print()
print("Press Ctrl+C to stop the server")
print()
print("=" * 60)
print()

# Start the server
try:
    subprocess.run([sys.executable, "app.py"])
except KeyboardInterrupt:
    print()
    print("Server stopped.")
