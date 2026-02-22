# 🚀 Deploy CryptexQ to Render

## Prerequisites
1. GitHub account
2. Render account (free tier available at render.com)
3. MongoDB Atlas account (free tier at mongodb.com/cloud/atlas)

---

## Step 1: Setup MongoDB Atlas (Database)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account and cluster
3. Click "Connect" → "Connect your application"
4. Copy the connection string (it looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. Add `/cryptexq_db` before the `?` to specify database name:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/cryptexq_db?retryWrites=true&w=majority
   ```

---

## Step 2: Push Code to GitHub

1. Create a new repository on GitHub
2. In your project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

---

## Step 3: Deploy on Render

### 3.1 Create Web Service
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your CryptexQ repository

### 3.2 Configure Build Settings
- **Name**: `cryptexq` (or any name you prefer)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`

### 3.3 Set Environment Variables
Click "Advanced" → "Add Environment Variable" and add:

| Key | Value |
|-----|-------|
| `MONGO_URI` | Your MongoDB Atlas connection string from Step 1 |
| `SECRET_KEY` | Generate random key (use: `python -c "import os; print(os.urandom(24).hex())"`) |
| `CRYPTEXQ_HMAC_SECRET` | Generate another random key |
| `RENDER` | `true` |
| `PYTHON_VERSION` | `3.10.5` |

### 3.4 Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes for first deployment
3. Your app will be live at: `https://your-app-name.onrender.com`

---

## Step 4: Test Your Deployment

Visit:
- Homepage: `https://your-app-name.onrender.com/home`
- Login: `https://your-app-name.onrender.com/login`
- Signup: `https://your-app-name.onrender.com/signup`

---

## Troubleshooting

### Build fails?
- Check that `requirements.txt` is in the root directory
- Ensure Python version is 3.10 or 3.11

### App crashes on startup?
- Check environment variables are set correctly
- Verify MongoDB connection string is correct
- Check Render logs: Dashboard → Your Service → Logs

### Database connection fails?
- Whitelist all IPs in MongoDB Atlas: Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)

---

## Optional: Custom Domain

1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domain"
3. Add your domain and follow DNS instructions

---

## Important Notes for Production

✅ **Password Security**: Passwords are now hashed with PBKDF2-SHA256
✅ **Session Management**: Flask sessions enabled with secure secret key
✅ **Database**: MongoDB for persistent user data
✅ **HTTPS**: Automatically handled by Render
✅ **Environment Variables**: Sensitive data stored securely

---

## Local Testing Before Deploy

Test production mode locally:
```bash
export RENDER=true
export MONGO_URI="your-mongodb-uri"
export SECRET_KEY="your-secret-key"
python app.py
```

---

## Cost

- **Render Free Tier**: Free (sleeps after 15 min of inactivity)
- **MongoDB Atlas Free Tier**: Free (512MB storage)
- **Total**: $0/month

---

## Support

If deployment fails, check:
1. Render build logs
2. MongoDB Atlas network access
3. Environment variables are correctly set
