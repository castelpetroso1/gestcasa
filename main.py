from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI()

conn = sqlite3.connect("db.sqlite", check_same_thread=False)
cur = conn.cursor()

# Tabelle
cur.execute("""
CREATE TABLE IF NOT EXISTS utenti(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT,
 password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS spese(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INT,
 descrizione TEXT,
 importo REAL
)
""")

conn.commit()

# ---------------- AUTH ----------------
@app.post("/register")
def register(u: dict):
    cur.execute("INSERT INTO utenti(username,password) VALUES(?,?)",
                (u["username"], u["password"]))
    conn.commit()
    return {"ok": True}

@app.post("/login")
def login(u: dict):
    cur.execute("SELECT id FROM utenti WHERE username=? AND password=?",
                (u["username"], u["password"]))
    r = cur.fetchone()
    if r:
        return {"user_id": r[0]}
    raise HTTPException(401)

# ---------------- SPESE ----------------
@app.post("/spesa")
def add_spesa(s: dict):
    cur.execute("INSERT INTO spese(user_id,descrizione,importo) VALUES(?,?,?)",
                (s["user_id"], s["descrizione"], s["importo"]))
    conn.commit()
    return {"ok": True}

@app.get("/dashboard/{uid}")
def dashboard(uid: int):
    cur.execute("SELECT SUM(importo) FROM spese WHERE user_id=?", (uid,))
    totale = cur.fetchone()[0] or 0
    return {"totale": totale}

# ---------------- FRONTEND ----------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")