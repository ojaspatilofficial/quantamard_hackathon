# 🔐 CryptexQ - Quantum-Safe Messaging Platform

A secure real-time messaging application featuring Post-Quantum Cryptography (PQC), Quantum Key Distribution (QKD) simulation, and end-to-end encryption with HMAC-SHA256 integrity protection.

## 🚀 Features

- **Post-Quantum Cryptography**: Kyber512 key encapsulation (simulated)
- **Hybrid Encryption**: QKD + AES-256-GCM
- **Message Integrity**: HMAC-SHA256 signatures
- **Real-time Chat**: WebSocket-based secure messaging
- **Authentication**: Session-based login with PBKDF2-SHA256 password hashing
- **Replay Protection**: Timestamp-based attack prevention
- **SSL/TLS Support**: HTTPS with self-signed certificates for local development

## 📋 Tech Stack

- **Backend**: Flask 2.3.2, Flask-SocketIO 5.3.4
- **Database**: MongoDB (optional - works in demo mode)
- **Cryptography**: AES-256-GCM, HMAC-SHA256, X25519 key exchange
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Gunicorn + Eventlet, Render-ready

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- MongoDB (optional)
- Git

### Local Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/cryptexq.git
cd cryptexq

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The server will start at `http://localhost:5000` and automatically open in your browser.

### HTTPS Mode

```bash
python app.py --ssl
```

Access at `https://localhost:5000` (accept certificate warning for self-signed cert)

## 🌐 Deployment to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables:
   - `MONGO_URI`: Your MongoDB connection string
   - `SECRET_KEY`: Flask secret key
   - `CRYPTEXQ_HMAC_SECRET`: HMAC secret for message integrity
5. Deploy!

Render will automatically use the `Procfile` and `requirements.txt`.

## 📁 Project Structure

```
cryptexq/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
├── .env.example           # Environment variables template
│
├── templates/             # HTML templates
│   ├── base.html         # Master template
│   ├── index.html        # Landing page
│   ├── home.html         # Dashboard
│   ├── login.html        # Login page
│   ├── signup.html       # Registration
│   ├── talkroom.html     # Chat room
│   └── ...
│
├── static/
│   ├── css/
│   │   └── style.css     # Unified stylesheet
│   └── js/
│       └── message_integrity_helper.js
│
├── certs/                # SSL certificates
│   ├── ca/              # Certificate Authority
│   └── server/          # Server certificates
│
├── crypto_utils.py      # AES encryption utilities
├── hmac_integrity.py    # Message integrity layer
├── qkd.py              # QKD simulation
├── pqc_utils.py        # Post-quantum crypto (simulated)
└── dilithium_utils.py  # Digital signatures
```

## 🔒 Security Features

### Authentication
- PBKDF2-SHA256 password hashing
- Secure session management
- Login-required decorator for protected routes

### Protected Routes
- Talk Room
- Replay Protection
- Secure Messages
- User Profile

### Public Routes
- Landing Page
- Demo
- About, FAQ, Contact

## 🧪 Testing

```bash
# Test HMAC integrity
python test_hmac_integrity.py

# Test end-to-end integrity
python test_e2e_integrity.py

# Test navigation
python test_navigation.py

# Verify all routes
python verify_routes.py
```

## 📖 Usage

### First-Time User
1. Open application → Landing page
2. Click "Sign Up" → Create account
3. Login → Access all features
4. Navigate to "Talk Room" for secure chat

### Messaging
1. Both users must be registered and logged in
2. Exchange X25519 public keys automatically
3. Messages encrypted with AES-256-GCM
4. HMAC-SHA256 signature for integrity

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is part of a hackathon submission.

## 🙏 Acknowledgments

- Built for Quantamard Hackathon
- Quantum-safe cryptography research
- Post-quantum cryptography standards (NIST)

## 📧 Contact

Project Link: [https://github.com/YOUR_USERNAME/cryptexq](https://github.com/YOUR_USERNAME/cryptexq)

---

**Note**: This is a demonstration project. For production use, implement proper PQC libraries (liboqs), secure key management, and professional security audits.
