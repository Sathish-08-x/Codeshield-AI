import sqlite3
import json
import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "code_detector.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_type TEXT NOT NULL,
        project_name TEXT NOT NULL,
        total_files INTEGER DEFAULT 1,
        avg_ai_score REAL NOT NULL,
        verdict TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scan_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        language TEXT NOT NULL,
        ai_score REAL NOT NULL,
        verdict TEXT NOT NULL,
        indicators_json TEXT NOT NULL,
        line_heatmaps_json TEXT NOT NULL,
        original_code TEXT NOT NULL,
        humanized_code TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        theme TEXT DEFAULT 'cyberpunk',
        font TEXT DEFAULT 'JetBrains Mono',
        particle_mode TEXT DEFAULT 'cyber_grid',
        particle_density TEXT DEFAULT 'high',
        glow_intensity INTEGER DEFAULT 85,
        scanlines_enabled INTEGER DEFAULT 1,
        sound_fx_enabled INTEGER DEFAULT 0,
        custom_accent_color TEXT DEFAULT '#00f0ff',
        updated_at TEXT NOT NULL
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS developer_profile (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        name TEXT DEFAULT 'CodeShield Engineer',
        title TEXT DEFAULT 'Full-Stack & Systems Engineer',
        bio TEXT DEFAULT 'Building neural code analyzers and secure developer tooling.',
        avatar_url TEXT DEFAULT '',
        github TEXT DEFAULT 'https://github.com',
        linkedin TEXT DEFAULT 'https://linkedin.com',
        email TEXT DEFAULT 'contact@codeshield.ai',
        portfolio TEXT DEFAULT 'https://codeshield.ai',
        skills_json TEXT DEFAULT '["Python", "FastAPI", "Security", "TypeScript"]',
        updated_at TEXT NOT NULL
    )
    """)
    
    cur.execute("SELECT id FROM user_settings WHERE id = 1")
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO user_settings (id, theme, font, particle_mode, particle_density, glow_intensity, scanlines_enabled, sound_fx_enabled, custom_accent_color, updated_at)
        VALUES (1, 'cyberpunk', 'JetBrains Mono', 'cyber_grid', 'high', 85, 1, 0, '#00f0ff', ?)
        """, (datetime.now(timezone.utc).isoformat(),))
        
    cur.execute("SELECT id FROM developer_profile WHERE id = 1")
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO developer_profile (id, name, title, bio, avatar_url, github, linkedin, email, portfolio, skills_json, updated_at)
        VALUES (1, 'Systems Architect', 'Security & Static Analysis Engineer',
                'Static code analysis engines and developer productivity tools.',
                '', 'https://github.com', 'https://linkedin.com', 'team@codeshield.ai', 'https://codeshield.ai',
                '["Python", "FastAPI", "AST", "Parsers", "Security"]', ?)
        """, (datetime.now(timezone.utc).isoformat(),))
        
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        free_scans_left INTEGER DEFAULT 5,
        is_pro INTEGER DEFAULT 0,
        participation_type TEXT DEFAULT 'General',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("SELECT id FROM users WHERE email = 'demo@codeshield.ai'")
    if not cur.fetchone():
        demo_pwd_hash = hashlib.sha256("demo123".encode()).hexdigest()
        cur.execute("""
        INSERT INTO users (username, email, password_hash, free_scans_left, is_pro, participation_type, created_at)
        VALUES ('StudentDev', 'demo@codeshield.ai', ?, 5, 0, 'Coursework', ?)
        """, (demo_pwd_hash, datetime.now(timezone.utc).isoformat()))

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_email TEXT,
        category TEXT NOT NULL,
        rating INTEGER DEFAULT 5,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def save_scan(scan_type: str, project_name: str, total_files: int, avg_ai_score: float, verdict: str, files_data: List[Dict[str, Any]]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
    INSERT INTO scans (scan_type, project_name, total_files, avg_ai_score, verdict, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (scan_type, project_name, total_files, avg_ai_score, verdict, created_at))
    scan_id = cur.lastrowid
    
    for f in files_data:
        cur.execute("""
        INSERT INTO scan_files (scan_id, filename, file_path, language, ai_score, verdict, indicators_json, line_heatmaps_json, original_code, humanized_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            f.get("filename", "unknown"),
            f.get("file_path", f.get("filename", "unknown")),
            f.get("language", "plaintext"),
            f.get("ai_score", 0.0),
            f.get("verdict", "Human"),
            json.dumps(f.get("indicators", [])),
            json.dumps(f.get("line_heatmaps", [])),
            f.get("original_code", ""),
            f.get("humanized_code", None)
        ))
        
    conn.commit()
    conn.close()
    return scan_id

def update_file_humanized_code(file_id: int, humanized_code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE scan_files SET humanized_code = ? WHERE id = ?", (humanized_code, file_id))
    conn.commit()
    conn.close()

def get_recent_scans(limit: int = 25) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def get_scan_details(scan_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    scan_row = cur.fetchone()
    if not scan_row:
        conn.close()
        return None
    
    scan_dict = dict(scan_row)
    cur.execute("SELECT * FROM scan_files WHERE scan_id = ? ORDER BY ai_score DESC", (scan_id,))
    file_rows = cur.fetchall()
    
    files = []
    for r in file_rows:
        fd = dict(r)
        fd["indicators"] = json.loads(fd["indicators_json"])
        fd["line_heatmaps"] = json.loads(fd["line_heatmaps_json"])
        del fd["indicators_json"]
        del fd["line_heatmaps_json"]
        files.append(fd)
        
    scan_dict["files"] = files
    conn.close()
    return scan_dict

def delete_scan(scan_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    cur.execute("DELETE FROM scan_files WHERE scan_id = ?", (scan_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

def get_user_settings() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_settings WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_user_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE user_settings
    SET theme = ?,
        font = ?,
        particle_mode = ?,
        particle_density = ?,
        glow_intensity = ?,
        scanlines_enabled = ?,
        sound_fx_enabled = ?,
        custom_accent_color = ?,
        updated_at = ?
    WHERE id = 1
    """, (
        settings.get("theme", "cyberpunk"),
        settings.get("font", "JetBrains Mono"),
        settings.get("particle_mode", "cyber_grid"),
        settings.get("particle_density", "high"),
        int(settings.get("glow_intensity", 85)),
        1 if settings.get("scanlines_enabled", True) else 0,
        1 if settings.get("sound_fx_enabled", False) else 0,
        settings.get("custom_accent_color", "#00f0ff"),
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()
    return get_user_settings()

def get_developer_profile() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM developer_profile WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if row:
        data = dict(row)
        try:
            data["skills"] = json.loads(data["skills_json"])
        except Exception:
            data["skills"] = []
        return data
    return {}

def update_developer_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    skills_json = json.dumps(profile.get("skills", ["Python", "FastAPI", "Security"]))
    cur.execute("""
    UPDATE developer_profile
    SET name = ?,
        title = ?,
        bio = ?,
        avatar_url = ?,
        github = ?,
        linkedin = ?,
        email = ?,
        portfolio = ?,
        skills_json = ?,
        updated_at = ?
    WHERE id = 1
    """, (
        profile.get("name", "CodeShield Engineer"),
        profile.get("title", "Systems Engineer"),
        profile.get("bio", "Static analysis and code naturalization tooling."),
        profile.get("avatar_url", ""),
        profile.get("github", ""),
        profile.get("linkedin", ""),
        profile.get("email", ""),
        profile.get("portfolio", ""),
        skills_json,
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()
    return get_developer_profile()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode()).hexdigest()

def register_user(username: str, email: str, password: str, participation_type: str = "General") -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    pwd_hash = hash_password(password)
    now_iso = datetime.now(timezone.utc).isoformat()
    
    try:
        cur.execute("""
        INSERT INTO users (username, email, password_hash, free_scans_left, is_pro, participation_type, created_at)
        VALUES (?, ?, ?, 5, 0, ?, ?)
        """, (username.strip(), email.strip().lower(), pwd_hash, participation_type, now_iso))
        conn.commit()
        user_id = cur.lastrowid
        cur.execute("SELECT id, username, email, free_scans_left, is_pro, participation_type, created_at FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row)
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Username or Email already registered")

def login_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    pwd_hash = hash_password(password)
    cur.execute("""
    SELECT id, username, email, free_scans_left, is_pro, participation_type, created_at
    FROM users
    WHERE LOWER(email) = LOWER(?) AND password_hash = ?
    """, (email.strip(), pwd_hash))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, username, email, free_scans_left, is_pro, participation_type, created_at
    FROM users WHERE id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def decrement_user_scan(user_id: Optional[int]) -> Dict[str, Any]:
    if not user_id:
        return {"allowed": True, "is_pro": False, "free_scans_left": 5, "message": "Guest scan"}
        
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_pro, free_scans_left FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"allowed": True, "is_pro": False, "free_scans_left": 5}
        
    is_pro = bool(row["is_pro"])
    free_scans = row["free_scans_left"]
    
    if is_pro:
        conn.close()
        return {"allowed": True, "is_pro": True, "free_scans_left": 999999}
        
    if free_scans > 0:
        new_scans = free_scans - 1
        cur.execute("UPDATE users SET free_scans_left = ? WHERE id = ?", (new_scans, user_id))
        conn.commit()
        conn.close()
        return {"allowed": True, "is_pro": False, "free_scans_left": new_scans}
    else:
        conn.close()
        return {
            "allowed": False,
            "is_pro": False,
            "free_scans_left": 0,
            "message": "Free tier limit reached (5/5). Please upgrade to Pro for ₹1,000 / month."
        }

def upgrade_user_to_pro(user_id: int, plan: str = "monthly_1000") -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_pro = 1 WHERE id = ?", (user_id,))
    conn.commit()
    cur.execute("SELECT id, username, email, free_scans_left, is_pro, participation_type FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_user_participation(user_id: int, p_type: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET participation_type = ? WHERE id = ?", (p_type, user_id))
    conn.commit()
    conn.close()
    return True

def save_feedback(user_name: str, user_email: Optional[str], category: str, rating: int, message: str) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
    INSERT INTO feedback (user_name, user_email, category, rating, message, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_name.strip(), user_email.strip() if user_email else None, category, rating, message.strip(), created_at))
    conn.commit()
    f_id = cur.lastrowid
    cur.execute("SELECT * FROM feedback WHERE id = ?", (f_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row)

def get_feedback_list(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results

if __name__ == "__main__":
    init_db()
