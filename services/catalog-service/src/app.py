from flask import Flask, request, jsonify
import sqlite3
import subprocess
import os

app = Flask(__name__)

# FAILLE 1 : Secret en dur (Détecté par Gitleaks)
app.config["SECRET_KEY"] = "dev-secret-do-not-use"
ADMIN_TOKEN = "admin-token-do-not-use"

@app.route("/health")
def health():
    return {"status": "ok"}

# FAILLE 2 : Injection SQL (Détecté par Semgrep/ZAP)
@app.route("/search")
def search():
    q = request.args.get("q", "")
    
    # Création DB temporaire pour la démo
    if not os.path.exists("db.sqlite"):
        conn = sqlite3.connect("db.sqlite")
        conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER, name TEXT, price REAL)")
        conn.execute("INSERT INTO products VALUES (1, 'Book A', 10.0)")
        conn.commit()
    else:
        conn = sqlite3.connect("db.sqlite")
    
    cur = conn.cursor()
    # VULNERABLE : f-string directe dans le SQL
    query = f"SELECT id, name, price FROM products WHERE name LIKE '%{q}%'"
    try:
        rows = cur.execute(query).fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FAILLE 3 : Command Injection / RCE (Détecté par Semgrep)
@app.route("/debug/run")
def debug_run():
    cmd = request.args.get("cmd", "id")
    # VULNERABLE : shell=True
    try:
        out = subprocess.check_output(cmd, shell=True, text=True)
        return {"output": out}
    except Exception as e:
        return {"error": str(e)}

# FAILLE 4 : Bug Logique (Fait échouer les tests unitaires s'il y en a)
@app.route("/discount", methods=["POST"])
def discount():
    data = request.get_json()
    pct = int(data.get("pct", 0))
    # BUG : variable 'price' non définie -> Crash 500
    # new_price = price * (100 - pct) / 100 
    return {"error": "Bug not fixed"}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)