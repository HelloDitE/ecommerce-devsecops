from flask import Flask, request, jsonify, send_file
import sqlite3
import subprocess
import os

app = Flask(__name__)

# (1) Secret en dur (détectable par Trivy/Gitleaks)
app.config["SECRET_KEY"] = "dev-secret-do-not-use"
ADMIN_TOKEN = "admin-token-do-not-use"

@app.route("/health")
def health():
    return {"status": "ok"}

# (2) SQL injection (Détectable par SAST/ZAP)
@app.route("/search")
def search():
    q = request.args.get("q", "")
    # Simulation de base de données pour l'exemple
    if not os.path.exists("db.sqlite"):
        conn = sqlite3.connect("db.sqlite")
        conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER, name TEXT, price REAL)")
        conn.execute("INSERT INTO products VALUES (1, 'Book A', 10.0)")
        conn.commit()
    else:
        conn = sqlite3.connect("db.sqlite")
    
    cur = conn.cursor()
    # VULNERABLE: concaténation directe
    query = f"SELECT id, name, price FROM products WHERE name LIKE '%{q}%'"
    try:
        rows = cur.execute(query).fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# (3) Command injection (Critique !)
@app.route("/debug/run")
def debug_run():
    cmd = request.args.get("cmd", "id")
    # VULNERABLE: shell=True
    try:
        out = subprocess.check_output(cmd, shell=True, text=True)
        return {"output": out}
    except Exception as e:
        return {"error": str(e)}

# (4) Bug volontaire pour tester le pipeline (Tests unitaires)
@app.route("/discount", methods=["POST"])
def discount():
    data = request.get_json()
    pct = int(data.get("pct", 0))
    # BUG: variable 'price' n'est pas définie ici ! Ça va planter (500).
    # new_price = price * (100 - pct) / 100 
    # Pour l'instant on laisse le bug pour faire échouer le pipeline
    return {"error": "Bug not fixed"}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)