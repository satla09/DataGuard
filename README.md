# 🛡️ DataGuard — Data Redundancy Removal System


---

## 📌 Project Overview
A cloud-based system that detects and prevents duplicate/redundant data from being stored in a Firebase Firestore database. Built with Python, Flask, and Google Firebase.

### Requirements Covered
| Requirement | Implementation |
|---|---|
| Identify & classify redundant data | SHA-256 hash comparison |
| Validation mechanism | Hash checked against all existing records |
| Prevent duplicate entries | Duplicate blocked before DB write |
| Append only unique data | Only unique hashes are saved |
| Database accuracy & efficiency | Firestore cloud DB with hash indexing |

---

## 🛠️ Tech Stack
- **Backend:** Python 3.x + Flask
- **Cloud Database:** Firebase Firestore (Google Cloud)
- **Duplicate Detection:** SHA-256 Hashing (`hashlib`)
- **Frontend:** HTML + CSS + Vanilla JavaScript

---

## 🚀 Setup Instructions

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Set up Firebase (Free, no card needed)
1. Go to [https://console.firebase.google.com](https://console.firebase.google.com)
2. Click **"Add project"** → name it `DataGuard`
3. Go to **Project Settings → Service Accounts**
4. Click **"Generate new private key"** → download the JSON file
5. Rename it to `serviceAccountKey.json`
6. Place it in the root of this project folder

### Step 3 — Enable Firestore
1. In Firebase Console → **Firestore Database**
2. Click **"Create Database"**
3. Choose **"Start in test mode"**
4. Select any region → Done!

### Step 4 — Run the app
```bash
python app.py
```

### Step 5 — Open in browser
```
http://localhost:5000
```

---

## 🎮 Demo Mode (No Firebase)
If you run the app **without** `serviceAccountKey.json`, it automatically runs in **Demo Mode** using in-memory storage. All features work — data just resets when you restart the server.

---

## 📁 Project Structure
```
CodeAlpha_DataRedundancySystem/
│
├── app.py                  # Main Flask application (core logic)
├── requirements.txt        # Python dependencies
├── serviceAccountKey.json  # Firebase credentials (NOT uploaded to GitHub)
├── README.md               # This file
│
└── templates/
    └── index.html          # Web UI
```

---

## 🔐 How Duplicate Detection Works

```
New Data Entry
      │
      ▼
  Normalize & Clean
      │
      ▼
  SHA-256 Hash Generated
      │
      ▼
  Query Firestore: does this hash exist?
      │
     / \
   YES   NO
    │     │
  BLOCK  SAVE to Firestore
  ⚠️      ✅
```


---


