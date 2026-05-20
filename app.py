"""
Data Redundancy Removal System
CodeAlpha Cloud Computing Internship — Task 1
Built with: Python, Flask, Firebase Firestore
"""

from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import json
from datetime import datetime
import os

app = Flask(__name__)

# ─────────────────────────────────────────────
# Firebase Initialization
# ─────────────────────────────────────────────
def init_firebase():
    """Initialize Firebase with service account credentials."""
    if not firebase_admin._apps:
        cred_path = "serviceAccountKey.json"
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        else:
            # Demo mode: use in-memory store if no Firebase credentials
            return None
    return firestore.client()

db = init_firebase()

# ─────────────────────────────────────────────
# In-memory fallback store (Demo Mode)
# ─────────────────────────────────────────────
demo_store = []

# ─────────────────────────────────────────────
# Core Redundancy Detection Logic
# ─────────────────────────────────────────────

def generate_hash(data: dict) -> str:
    """
    Generate a SHA-256 hash from a data entry.
    This hash acts as a unique fingerprint for each record.
    """
    # Sort keys so {"a":1,"b":2} and {"b":2,"a":1} produce same hash
    normalized = json.dumps(data, sort_keys=True).lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def is_duplicate(data_hash: str) -> tuple[bool, str]:
    """
    Check if a hash already exists in Firebase or demo store.
    Returns (is_duplicate: bool, reason: str)
    """
    if db:
        # Firebase check
        docs = db.collection("records") \
                 .where("hash", "==", data_hash) \
                 .limit(1) \
                 .stream()
        for doc in docs:
            return True, f"Duplicate of record ID: {doc.id}"
        return False, ""
    else:
        # Demo mode check
        for record in demo_store:
            if record["hash"] == data_hash:
                return True, f"Duplicate of record: {record['id']}"
        return False, ""


def save_record(entry: dict, data_hash: str) -> str:
    """Save a unique record to Firebase or demo store."""
    record = {
        "data": entry,
        "hash": data_hash,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "verified_unique"
    }

    if db:
        doc_ref = db.collection("records").add(record)
        return doc_ref[1].id
    else:
        record["id"] = f"demo_{len(demo_store) + 1}"
        demo_store.append(record)
        return record["id"]


def get_all_records() -> list:
    """Fetch all records from Firebase or demo store."""
    if db:
        docs = db.collection("records").order_by("timestamp").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    else:
        return demo_store.copy()


def delete_record(record_id: str) -> bool:
    """Delete a record by ID."""
    if db:
        db.collection("records").document(record_id).delete()
        return True
    else:
        global demo_store
        before = len(demo_store)
        demo_store = [r for r in demo_store if r.get("id") != record_id]
        return len(demo_store) < before


# ─────────────────────────────────────────────
# Flask Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    mode = "Firebase Cloud" if db else "Demo (In-Memory)"
    return render_template("index.html", mode=mode)


@app.route("/api/add", methods=["POST"])
def add_entry():
    """
    Validate and add a new data entry.
    Steps:
      1. Parse incoming data
      2. Generate hash fingerprint
      3. Check for duplicates
      4. If unique → save to cloud DB
      5. Return result to frontend
    """
    try:
        payload = request.get_json()
        if not payload or not payload.get("data"):
            return jsonify({"success": False, "message": "No data provided."}), 400

        entry = payload["data"]

        # Strip whitespace from string values for better dedup
        cleaned = {k: v.strip() if isinstance(v, str) else v for k, v in entry.items()}

        # Generate unique fingerprint
        data_hash = generate_hash(cleaned)

        # Check for duplicates
        duplicate, reason = is_duplicate(data_hash)

        if duplicate:
            return jsonify({
                "success": False,
                "status": "duplicate",
                "message": f"⚠️ Duplicate detected! {reason}",
                "hash": data_hash
            })

        # Save unique record
        record_id = save_record(cleaned, data_hash)

        return jsonify({
            "success": True,
            "status": "saved",
            "message": "✅ Unique record saved to cloud database!",
            "id": record_id,
            "hash": data_hash
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route("/api/records", methods=["GET"])
def list_records():
    """Return all stored records."""
    try:
        records = get_all_records()
        return jsonify({"success": True, "records": records, "count": len(records)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/check", methods=["POST"])
def check_duplicate():
    """Check if data is duplicate without saving it."""
    try:
        payload = request.get_json()
        entry = payload.get("data", {})
        cleaned = {k: v.strip() if isinstance(v, str) else v for k, v in entry.items()}
        data_hash = generate_hash(cleaned)
        duplicate, reason = is_duplicate(data_hash)
        return jsonify({
            "is_duplicate": duplicate,
            "reason": reason,
            "hash": data_hash
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/delete/<record_id>", methods=["DELETE"])
def delete_entry(record_id):
    """Delete a record by ID."""
    try:
        success = delete_record(record_id)
        if success:
            return jsonify({"success": True, "message": "Record deleted."})
        return jsonify({"success": False, "message": "Record not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    """Return database statistics."""
    try:
        records = get_all_records()
        return jsonify({
            "total_records": len(records),
            "db_mode": "Firebase Cloud" if db else "Demo Mode",
            "last_updated": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Data Redundancy Removal System")
    print("  CodeAlpha Cloud Computing — Task 1")
    print("=" * 50)
    if db:
        print("  ✅ Connected to Firebase Firestore")
    else:
        print("  ⚠️  Running in DEMO mode (no Firebase key found)")
        print("  → Add serviceAccountKey.json to enable Firebase")
    print("  🌐 Visit: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
