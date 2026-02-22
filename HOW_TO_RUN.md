# CryptexQ - How to Run This Project

## Quick Start (3 Steps)

### Step 1: Open Terminal in Project Folder
1. Open PowerShell or Command Prompt
2. Navigate to project folder:
   ```
   cd "d:\HACKATHONS\Quantamard\CRYPTEXQ (2)\EDI-SY1"
   ```

### Step 2: Install Dependencies (First Time Only)
```
pip install -r requirements.txt
```

### Step 3: Start the Server
```
python app.py
```

The server will start on: **http://localhost:5000**

⚠️ **IMPORTANT**: If you see SSL certificate errors, the server is trying to use HTTPS but failing. Use this instead:

```
python run_simple.py
```

This runs a simpler version without SSL on **http://localhost:5000**

---

## Quick Access URLs

Once server is running, open these in your browser:

- Home Page: http://localhost:5000/home
- Main Page: http://localhost:5000/
- About: http://localhost:5000/about
- Team: http://localhost:5000/team
- FAQ: http://localhost:5000/faq
- Demo: http://localhost:5000/demo
- Talk Room: http://localhost:5000/talkroom

---

## Stop the Server

Press **Ctrl + C** in the terminal

Or run:
```
Stop-Process -Name python -Force
```

---

## Troubleshooting

### Server won't start?
Try the simple version:
```
python run_simple.py
```

### Port 5000 already in use?
Stop other Python processes:
```
Stop-Process -Name python -Force
```

### Pages not loading content?
Clear browser cache: **Ctrl + Shift + Delete**
Or open in incognito mode
