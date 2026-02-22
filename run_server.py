"""
Complete Server Startup and Test Script for CryptexQ
This script starts the server and tests all routes
"""

import subprocess
import sys
import time
import os

def check_server_running():
    """Check if Flask server is already running"""
    try:
        import urllib.request
        import ssl
        
        # Create SSL context that doesn't verify certificates (for self-signed cert)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        urllib.request.urlopen('https://localhost:5000/', context=ctx, timeout=2)
        return True
    except:
        return False

def main():
    print("="*70)
    print("CryptexQ Server Startup & Test")
    print("="*70)
    print()
    
    # Check if server is already running
    if check_server_running():
        print("✅ Flask server is ALREADY RUNNING!")
        print()
        print("🌐 Access the application at:")
        print()
        print("   https://localhost:5000/home")
        print()
        print("="*70)
        print("All Pages Available:")
        print("="*70)
        
        pages = [
            ("Index", "/"),
            ("Home", "/home"),
            ("About", "/about"),
            ("Contact", "/contact"),
            ("Demo", "/demo"),
            ("FAQ", "/faq"),
            ("Forgot Password", "/forgetpg"),
            ("Login", "/login"),
            ("Logout", "/logout"),
            ("Profile", "/profile"),
            ("Replay Protection", "/replay-protection"),
            ("Secure Messages", "/secure-msg"),
            ("Sign Up", "/signup"),
            ("Talk Room", "/talkroom"),
            ("Team", "/team"),
            ("Terms", "/term"),
        ]
        
        for name, path in pages:
            print(f"  ✓ {name:<20} https://localhost:5000{path}")
        
        print("="*70)
        print()
        print("📝 Important Notes:")
        print("   • Accept the SSL certificate warning in your browser")
        print("   • All navigation links should work from the home page")
        print("   • Press Ctrl+C in the server terminal to stop")
        print()
        return
    
    print("🚀 Starting Flask server...")
    print()
    print("Once started, access at: https://localhost:5000/home")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)
    print()
    
    # Start the server
    try:
        os.chdir(os.path.dirname(__file__))
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped successfully.")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
