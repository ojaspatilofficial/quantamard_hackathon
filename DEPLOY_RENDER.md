# 🚀 Render Deployment Guide - CryptexQ

## Quick Deploy (5 Minutes)

### Step 1: Prepare Repository
✅ **DONE** - Your repo is production-ready at:
```
https://github.com/ojaspatilofficial/quantamard_hackathon
```

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create Web Service
1. Click **New +** → **Web Service**
2. Connect your GitHub repository: `ojaspatilofficial/quantamard_hackathon`
3. Configure the service:

```
Name: cryptexq-quantum-messaging
Region: Oregon (US West) or closest to you
Branch: main
Root Directory: (leave blank)
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: (auto-detected from Procfile)
```

### Step 4: Set Environment Variables

Click **Environment** → **Add Environment Variable**:

#### Required Variables

1. **SECRET_KEY** (Flask session encryption)
   ```bash
   # Generate on your local machine:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and paste as SECRET_KEY value in Render.

2. **CRYPTEXQ_HMAC_SECRET** (Message integrity)
   ```bash
   # Generate on your local machine:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and paste as CRYPTEXQ_HMAC_SECRET value in Render.

3. **FLASK_ENV** (Production mode)
   ```
   production
   ```

#### Optional Variables (Recommended for Production)

4. **CORS_ORIGIN** (Security - restrict to your domain)
   ```
   https://cryptexq-quantum-messaging.onrender.com
   ```
   (Use your actual Render URL after deployment)

5. **MONGO_URI** (Database persistence - optional)
   ```
   mongodb+srv://<username>:<password>@cluster.mongodb.net/cryptexq?retryWrites=true&w=majority
   ```
   *Skip this if using demo mode (works without database)*

### Step 5: Deploy

1. Click **Create Web Service**
2. Wait 2-3 minutes for deployment
3. Render will:
   - Install dependencies from `requirements.txt`
   - Start server with Gunicorn + Eventlet (from `Procfile`)
   - Assign a public URL: `https://cryptexq-quantum-messaging.onrender.com`

### Step 6: Verify Deployment

Open your Render URL and check:

1. **Landing Page**: Should load with "Welcome to CryptexQ"
2. **Security Headers**: Open DevTools → Network → Response Headers
   ```
   x-content-type-options: nosniff
   x-frame-options: DENY
   x-xss-protection: 1; mode=block
   strict-transport-security: max-age=31536000; includeSubDomains
   ```
3. **Logs**: Render Dashboard → Logs tab
   ```
   [INFO] CryptexQ - Quantum-Safe Messaging Platform
   [INFO] Environment: PRODUCTION
   [INFO] Message integrity layer: ACTIVE
   ```

---

## 🔧 Troubleshooting

### Issue: Application Crash on Startup
**Solution**: Check Render Logs for errors. Common causes:
- Missing environment variables (SECRET_KEY, CRYPTEXQ_HMAC_SECRET)
- Invalid MongoDB URI (if using database)

### Issue: "Internal Server Error"
**Solution**: Check Logs tab in Render dashboard. Enable verbose logging:
```bash
# Add environment variable:
FLASK_DEBUG=1
```

### Issue: CORS Errors from Frontend
**Solution**: Update CORS_ORIGIN environment variable:
```bash
# Allow specific domain:
CORS_ORIGIN=https://your-frontend-domain.com

# OR allow multiple origins (comma-separated):
CORS_ORIGIN=https://domain1.com,https://domain2.com
```

### Issue: WebSocket Disconnections
**Solution**: Render free tier has connection limits. Upgrade to paid plan for production use.

---

## 🔒 Post-Deployment Security

### 1. Update CORS Policy
After first deployment, restrict CORS to your domain:
```bash
# In Render Dashboard → Environment:
CORS_ORIGIN=https://cryptexq-quantum-messaging.onrender.com
```

### 2. Enable HTTPS Redirect
Render automatically provides HTTPS. Verify:
```bash
# Test redirect:
curl -I http://cryptexq-quantum-messaging.onrender.com
# Should return 301 or 308 redirect to HTTPS
```

### 3. Monitor Logs
Check Render Logs daily for:
- Failed login attempts
- Integrity violation warnings
- Unusual traffic patterns

### 4. Set Up Custom Domain (Optional)
1. Render Dashboard → Settings → Custom Domains
2. Add your domain: `cryptexq.yourdomain.com`
3. Update DNS CNAME record: `cryptexq → cryptexq-quantum-messaging.onrender.com`

---

## 📊 Performance Optimization

### Free Tier Limitations
- **Spin down after 15 min inactivity** (30 sec cold start)
- **750 hrs/month free** (enough for demo)
- **Limited memory** (512 MB)

### Recommended Upgrades for Production
1. **Starter Plan** ($7/month):
   - No spin down
   - 512 MB RAM
   - Custom domain support

2. **Standard Plan** ($25/month):
   - 2 GB RAM
   - Better WebSocket performance
   - Autoscaling

---

## 🧪 Testing Production Deployment

### Test Authentication Flow
1. Visit: `https://your-app.onrender.com/signup`
2. Create account: `testuser@example.com` / `password123`
3. Login at: `https://your-app.onrender.com/login`
4. Verify redirect to home page

### Test Secure Messaging
1. Navigate to: `https://your-app.onrender.com/secure_msg`
2. Select encryption mode: "QKD + AES-GCM"
3. Send test message
4. Check logs for:
   ```
   [INFO] Simulating QKD session...
   [INFO] Message encrypted successfully
   [INFO] HMAC-SHA256 integrity verified
   ```

### Test Third-Party Verification
1. Visit: `https://your-app.onrender.com/demo`
2. Send message with third-party verification enabled
3. Verify signature in logs:
   ```
   [INFO] Digital signature: <signature_hex>
   [INFO] Verification result: VALID
   ```

---

## 📝 Environment Variables Summary

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | None | Flask session encryption key (64 hex chars) |
| `CRYPTEXQ_HMAC_SECRET` | ✅ Yes | None | HMAC message integrity key (64 hex chars) |
| `FLASK_ENV` | ✅ Yes | `development` | Set to `production` for deployment |
| `CORS_ORIGIN` | ⚠️ Recommended | `*` | Allowed origins (restrict in production) |
| `MONGO_URI` | ❌ Optional | None | MongoDB connection string (demo mode works without) |
| `PORT` | ❌ Auto | 5000 | Set by Render automatically |

---

## 🎯 Next Steps

1. ✅ Deploy to Render (5 min)
2. ✅ Set environment variables (SECRET_KEY, CRYPTEXQ_HMAC_SECRET, FLASK_ENV=production)
3. ✅ Verify security headers in browser DevTools
4. ✅ Test authentication flow (signup/login)
5. ✅ Test secure messaging with QKD/PQC modes
6. ⚠️ **For Production**: Integrate real Kyber512 with liboqs-python
7. ⚠️ **For Production**: Add MongoDB for persistence
8. ⚠️ **For Production**: Set up custom domain with CORS restriction

---

## 🔗 Useful Links

- **Live App**: `https://cryptexq-quantum-messaging.onrender.com` (after deployment)
- **GitHub Repo**: https://github.com/ojaspatilofficial/quantamard_hackathon
- **Render Dashboard**: https://dashboard.render.com
- **Documentation**: See `SECURITY_HARDENING.md` for security details

---

**Status**: ✅ READY TO DEPLOY  
**Estimated Deploy Time**: 5 minutes  
**Free Tier**: Available (750 hours/month)
