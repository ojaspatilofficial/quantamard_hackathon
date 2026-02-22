# ✅ Pre-Deployment Verification Checklist

Run this checklist before deploying to Render.

## 🔍 Code Verification

### 1. Server Startup Test
```bash
cd "d:\HACKATHONS\Quantamard\CRYPTEXQ (2)\EDI-SY1"
python app.py
```

**Expected Output**:
```
2026-02-22 15:03:39 [INFO] __main__: CryptexQ - Quantum-Safe Messaging Platform
2026-02-22 15:03:39 [INFO] __main__: Environment: DEVELOPMENT
2026-02-22 15:03:39 [INFO] __main__: Message integrity layer: ACTIVE
```

✅ Server starts without errors  
✅ Structured logging visible (no print statements)  
✅ Browser opens automatically at http://localhost:5000  

### 2. Verify No Print Statements
```bash
grep -n "print(" app.py
```

**Expected**: No results (all replaced with logger)

### 3. Check Git Status
```bash
git status
```

**Expected**: "On branch main, Your branch is up to date with 'origin/main'"

---

## 🌐 Environment Variables Preparation

### Generate Secrets
```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# CRYPTEXQ_HMAC_SECRET
python -c "import secrets; print(secrets.token_hex(32))"
```

**Save these values** - you'll need them for Render.

### Local Testing with Environment Variables
```bash
# Create .env file (DO NOT COMMIT)
SECRET_KEY=<paste-secret-from-above>
CRYPTEXQ_HMAC_SECRET=<paste-secret-from-above>
FLASK_ENV=production
PORT=5000
CORS_ORIGIN=*
```

Test production mode locally:
```bash
FLASK_ENV=production python app.py
```

**Expected**:
```
[INFO] __main__: Environment: PRODUCTION
```

---

## 🔒 Security Headers Test

### Manual Browser Test
1. Start server: `python app.py`
2. Open: http://localhost:5000
3. Open DevTools → Network tab
4. Reload page
5. Click on any request → Headers tab → Response Headers

**Expected Headers**:
```
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
referrer-policy: strict-origin-when-cross-origin
```

**Note**: `strict-transport-security` only appears in production (FLASK_ENV=production)

---

## 🧪 Functionality Tests

### Test 1: Landing Page
- ✅ Visit http://localhost:5000
- ✅ Page loads without errors
- ✅ Navigation bar visible
- ✅ "Welcome to CryptexQ" heading displays

### Test 2: Authentication Flow
1. ✅ Click "Sign Up" → `/signup`
2. ✅ Register: `testuser@example.com` / `password123`
3. ✅ Redirects to `/login`
4. ✅ Login with same credentials
5. ✅ Redirects to `/home`
6. ✅ User email shows in navbar

### Test 3: Secure Messaging
1. ✅ Navigate to `/secure_msg`
2. ✅ Select "QKD + AES-GCM"
3. ✅ Send test message: "Hello quantum world"
4. ✅ Check console logs:
   ```
   [INFO] __main__: Simulating QKD session...
   [INFO] __main__: Message encrypted successfully
   ```

### Test 4: Socket.IO WebSockets
1. ✅ Navigate to `/talkroom`
2. ✅ Open browser console
3. ✅ Verify WebSocket connection:
   ```javascript
   WebSocket connection to 'ws://localhost:5000/socket.io/...' succeeded
   ```
4. ✅ Send message in chat
5. ✅ Message appears in chatroom

---

## 📦 Deployment Files Verification

### Check Required Files
```bash
ls -la | grep -E "(Procfile|requirements.txt|.env.example|.gitignore)"
```

**Expected**:
```
-rw-r--r-- Procfile
-rw-r--r-- requirements.txt
-rw-r--r-- .env.example
-rw-r--r-- .gitignore
```

### Verify Procfile
```bash
cat Procfile
```

**Expected**:
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

### Verify requirements.txt
```bash
cat requirements.txt | grep -E "(Flask|eventlet|gunicorn)"
```

**Expected**:
```
Flask==2.3.2
eventlet==0.33.3
gunicorn==21.2.0
```

---

## 📚 Documentation Verification

### Check All Docs Exist
```bash
ls -la *.md
```

**Expected**:
```
README.md
SECURITY_HARDENING.md
DEPLOY_RENDER.md
PRODUCTION_SUMMARY.md
```

### Verify SECURITY_HARDENING.md Content
```bash
grep -A 5 "Security Headers Middleware" SECURITY_HARDENING.md
```

**Expected**: Section with 5 security headers listed

---

## 🚀 GitHub Repository Check

### Verify Remote URL
```bash
git remote -v
```

**Expected**:
```
origin  https://github.com/ojaspatilofficial/quantamard_hackathon.git (fetch)
origin  https://github.com/ojaspatilofficial/quantamard_hackathon.git (push)
```

### Verify Latest Commits
```bash
git log --oneline -3
```

**Expected** (most recent first):
```
32becf2 Add production hardening completion summary
ecf836f Add comprehensive Render deployment guide and updated .env.example
2e75dc2 Production hardening: structured logging, security headers, eventlet async, environment-based config
```

### Verify Clean Working Tree
```bash
git status
```

**Expected**:
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

## 🎯 Render Deployment Readiness

### Pre-Deployment Checklist

- ✅ Server starts locally without errors
- ✅ All print statements replaced with logging
- ✅ Security headers present in HTTP responses
- ✅ Authentication flow works (signup/login)
- ✅ Secure messaging functional
- ✅ WebSocket connections work
- ✅ Procfile configured correctly
- ✅ requirements.txt includes all dependencies
- ✅ .env.example has all required variables
- ✅ .gitignore excludes secrets (.env, *.key)
- ✅ Documentation complete (README, SECURITY_HARDENING, DEPLOY_RENDER)
- ✅ GitHub repository up to date
- ✅ No uncommitted changes
- ✅ SECRET_KEY and CRYPTEXQ_HMAC_SECRET generated

### Environment Variables for Render

**Copy these to Render Dashboard → Environment**:

```
SECRET_KEY = <paste-64-hex-char-secret>
CRYPTEXQ_HMAC_SECRET = <paste-64-hex-char-secret>
FLASK_ENV = production
CORS_ORIGIN = https://your-app.onrender.com
```

**Optional**:
```
MONGO_URI = mongodb+srv://...
```

---

## 🚦 Deploy to Render

Once all checklist items pass:

1. **Go to**: https://render.com
2. **Sign in** with GitHub
3. **New + → Web Service**
4. **Connect**: `ojaspatilofficial/quantamard_hackathon`
5. **Configure**:
   - Name: `cryptexq-quantum-messaging`
   - Region: Oregon (US West)
   - Branch: `main`
   - Build: `pip install -r requirements.txt`
   - Start: (auto-detected from Procfile)
6. **Add Environment Variables** (see above)
7. **Create Web Service**
8. **Wait 2-3 minutes** for deployment
9. **Access**: `https://cryptexq-quantum-messaging.onrender.com`

---

## ✅ Post-Deployment Verification

### Test 1: Landing Page
```bash
curl -I https://your-app.onrender.com/
```

**Expected**: `HTTP/2 200`

### Test 2: Security Headers
```bash
curl -I https://your-app.onrender.com/ | grep -E "(x-content-type|x-frame|strict-transport)"
```

**Expected**:
```
x-content-type-options: nosniff
x-frame-options: DENY
strict-transport-security: max-age=31536000; includeSubDomains
```

### Test 3: Check Render Logs
Render Dashboard → Logs tab

**Expected**:
```
[INFO] CryptexQ - Quantum-Safe Messaging Platform
[INFO] Environment: PRODUCTION
[INFO] Message integrity layer: ACTIVE
```

### Test 4: Functional Test
1. Visit: `https://your-app.onrender.com`
2. Sign up with test account
3. Login
4. Send encrypted message
5. Verify in Render logs:
   ```
   [INFO] Simulating QKD session...
   [INFO] Message encrypted successfully
   ```

---

## 🎉 Success Criteria

**All items must pass**:

- ✅ Local server starts without errors
- ✅ No print statements in code
- ✅ Security headers present in responses
- ✅ Authentication flow works
- ✅ WebSocket connections functional
- ✅ GitHub repository clean and up-to-date
- ✅ Render deployment successful (HTTP 200)
- ✅ Production logs show "PRODUCTION" environment
- ✅ Encrypted messaging works on production URL

---

**Checklist Status**: ✅ READY TO DEPLOY  
**Estimated Deploy Time**: 5 minutes  
**Next Step**: Follow `DEPLOY_RENDER.md` guide
