"""
FootyVision Backend - Authentication & Data API with API-Football (api-sports.io)
================================================================================
Kullanıcı Adı + Şifre tabanlı giriş/kayıt sistemi.
SQLite veritabanı, API-Football entegrasyonu ve günlük limit korumalı oran botu.
"""

import os
import sqlite3
import secrets
import json
import threading
import time
import requests
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session, g, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash

# ─── App Config ───────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app, supports_credentials=True)

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri="memory://"
)

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'footyvision.db')


def get_db():
    """Get a database connection for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database schema with new predictions totem fields."""
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            avatar      TEXT    DEFAULT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS matches (
            fixture_id  INTEGER PRIMARY KEY,
            home_team   TEXT NOT NULL,
            away_team   TEXT NOT NULL,
            home_odds   REAL DEFAULT 1.0,
            draw_odds   REAL DEFAULT 1.0,
            away_odds   REAL DEFAULT 1.0,
            league      TEXT,
            match_time  TEXT, -- e.g. "2026-06-21 21:00"
            status      TEXT DEFAULT 'upcoming',
            result      TEXT DEFAULT '',
            score       TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            match_id    INTEGER NOT NULL,
            choice      TEXT    NOT NULL,
            diff        TEXT    NOT NULL DEFAULT '1',
            label_text  TEXT    NOT NULL DEFAULT '',
            predicted_difference INTEGER DEFAULT 0,
            predicted_home_score INTEGER DEFAULT NULL,
            predicted_away_score INTEGER DEFAULT NULL,
            is_totem    BOOLEAN DEFAULT 0,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (match_id) REFERENCES matches(fixture_id) ON DELETE CASCADE,
            UNIQUE(user_id, match_id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            match_id    INTEGER NOT NULL,
            match_name  TEXT    NOT NULL DEFAULT '',
            predict     TEXT    NOT NULL DEFAULT '',
            comment     TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (match_id) REFERENCES matches(fixture_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS system_state (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL
        );
    """)
    # Ensure avatar column exists for older databases
    try:
        db.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass  # Column already exists
    db.commit()
    seed_world_cup_matches(db)


def seed_world_cup_matches(db):
    """Seed real World Cup 2026 matches with official api-sports fixture IDs."""
    # Clear previous mock matches to allow re-seeding with correct real fixtures
    db.execute("DELETE FROM matches WHERE fixture_id >= 999001 AND fixture_id <= 999999")
    
    matches = [
        (1489388, "Mexico", "South Korea", "FIFA World Cup", "2026-06-19 04:00", "finished", "1 - 0", "home"),
        (1489391, "USA", "Australia", "FIFA World Cup", "2026-06-19 22:00", "finished", "2 - 0", "home"),
        (1489390, "Scotland", "Morocco", "FIFA World Cup", "2026-06-20 01:00", "finished", "0 - 1", "away"),
        (1489389, "Brazil", "Haiti", "FIFA World Cup", "2026-06-20 03:30", "finished", "3 - 0", "home"),
        (1539006, "Türkiye", "Paraguay", "FIFA World Cup", "2026-06-20 06:00", "finished", "0 - 1", "away"),
        (1539007, "Netherlands", "Sweden", "FIFA World Cup", "2026-06-20 20:00", "finished", "5 - 1", "home"),
        (1489393, "Germany", "Ivory Coast", "FIFA World Cup", "2026-06-20 23:00", "finished", "2 - 1", "home"),
        (1489392, "Ecuador", "Curaçao", "FIFA World Cup", "2026-06-21 03:00", "upcoming", "", ""),
        (1489394, "Tunisia", "Japan", "FIFA World Cup", "2026-06-21 07:00", "upcoming", "", ""),
        (1489397, "Spain", "Saudi Arabia", "FIFA World Cup", "2026-06-21 19:00", "upcoming", "", ""),
        (1489395, "Belgium", "Iran", "FIFA World Cup", "2026-06-21 22:00", "upcoming", "", ""),
        (1489398, "Uruguay", "Cape Verde Islands", "FIFA World Cup", "2026-06-22 01:00", "upcoming", "", ""),
        
        # Real June 22 matches (TRT)
        (999001, "Argentina", "Austria", "FIFA World Cup", "2026-06-22 20:00", "upcoming", "", ""),
        (999002, "France", "Iraq", "FIFA World Cup", "2026-06-23 00:00", "upcoming", "", ""),
        (999003, "Norway", "Senegal", "FIFA World Cup", "2026-06-23 03:00", "upcoming", "", ""),
        
        # Real June 23 matches (TRT)
        (999004, "Portugal", "Uzbekistan", "FIFA World Cup", "2026-06-23 20:00", "upcoming", "", ""),
        (999005, "England", "Ghana", "FIFA World Cup", "2026-06-23 23:00", "upcoming", "", ""),
        (999006, "Panama", "Croatia", "FIFA World Cup", "2026-06-24 02:00", "upcoming", "", ""),
        (999007, "Colombia", "DR Congo", "FIFA World Cup", "2026-06-24 05:00", "upcoming", "", ""),
        
        # Real June 24 matches (TRT)
        (999008, "Switzerland", "Canada", "FIFA World Cup", "2026-06-25 01:00", "upcoming", "", ""),
        (999009, "Bosnia and Herzegovina", "Qatar", "FIFA World Cup", "2026-06-25 03:00", "upcoming", "", ""),
        (999010, "Scotland", "Brazil", "FIFA World Cup", "2026-06-25 03:00", "upcoming", "", ""),
        (999011, "Czechia", "Mexico", "FIFA World Cup", "2026-06-25 05:00", "upcoming", "", ""),
        
        # Real June 25 matches (TRT)
        (999012, "Ecuador", "Germany", "FIFA World Cup", "2026-06-25 23:00", "upcoming", "", ""),
        (999013, "Curaçao", "Ivory Coast", "FIFA World Cup", "2026-06-25 23:00", "upcoming", "", ""),
        (999014, "Japan", "Sweden", "FIFA World Cup", "2026-06-26 02:00", "upcoming", "", ""),
        (999015, "Paraguay", "Australia", "FIFA World Cup", "2026-06-26 05:00", "upcoming", "", ""),
        
        # Real June 26 matches (TRT)
        (999016, "Norway", "France", "FIFA World Cup", "2026-06-26 22:00", "upcoming", "", ""),
        (999017, "Senegal", "Iraq", "FIFA World Cup", "2026-06-26 22:00", "upcoming", "", ""),
        (999018, "Egypt", "Iran", "FIFA World Cup", "2026-06-27 06:00", "upcoming", "", ""),
        (999019, "New Zealand", "Belgium", "FIFA World Cup", "2026-06-27 06:00", "upcoming", "", ""),

        # Real June 27 matches (TRT June 28)
        (999020, "Panama", "England", "FIFA World Cup", "2026-06-28 00:00", "upcoming", "", ""),
        (999021, "Croatia", "Ghana", "FIFA World Cup", "2026-06-28 00:00", "upcoming", "", ""),
        (999022, "Colombia", "Portugal", "FIFA World Cup", "2026-06-28 02:30", "upcoming", "", ""),
        (999023, "Jordan", "Argentina", "FIFA World Cup", "2026-06-28 05:00", "upcoming", "", "")
    ]
    for fid, home, away, league, t, status, score, result in matches:
        cursor = db.execute("SELECT 1 FROM matches WHERE fixture_id = ?", (fid,))
        if not cursor.fetchone():
            db.execute("""
                INSERT INTO matches (fixture_id, home_team, away_team, league, match_time, status, score, result, home_odds, draw_odds, away_odds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1.0, 1.0, 1.0)
            """, (fid, home, away, league, t, status, score, result))
    # Correct Germany-Ivory Coast score and result if already seeded
    db.execute("UPDATE matches SET score = '2 - 1', result = 'home', status = 'finished' WHERE fixture_id = 1489393")
    db.commit()
    db.close()


# ─── API-Football Background Worker ───────────────────────────────────────────
API_KEY = "aed9131fa2f16768e0176986c3307409"

def update_matches_from_api():
    """Daily sync bot with API limit protection. Connects to api-sports.io."""
    try:
        # Open and fetch metadata, then close DB immediately to avoid locking during API calls
        db = sqlite3.connect(DATABASE)
        db.execute("PRAGMA journal_mode=WAL")
        
        # Limit control: Only run once per calendar day (UTC+3 Istanbul time)
        tz = timezone(timedelta(hours=3))
        today_str = datetime.now(tz).strftime('%Y-%m-%d')
        
        cursor = db.execute("SELECT value FROM system_state WHERE key = 'last_api_update'")
        row = cursor.fetchone()
        if row and row[0] == today_str:
            print("[BACKGROUND BOT] Already synced today. Skipping API calls to conserve limit.")
            db.close()
            return
            
        print("[BACKGROUND BOT] Initializing daily fixture & odds update...")
        # Get matches in database
        db_matches = []
        for m in db.execute("SELECT fixture_id, status FROM matches").fetchall():
            db_matches.append((m[0], m[1]))
        db.close()
        
        headers = {
            "x-apisports-key": API_KEY
        }
        
        for fid, db_status in db_matches:
            if str(fid).startswith("999"):
                continue
            # 1. Update Fixture Status and Score
            url_fix = f"https://v3.football.api-sports.io/fixtures?id={fid}"
            try:
                resp = requests.get(url_fix, headers=headers, timeout=15)
                time.sleep(7) # Respect per-minute API limit of 10 requests
                if resp.ok:
                    res = resp.json().get("response", [])
                    if res:
                        f_data = res[0]
                        fixture = f_data.get("fixture", {})
                        goals = f_data.get("goals", {})
                        
                        status_short = fixture.get("status", {}).get("short")
                        status_str = "upcoming"
                        if status_short in ["FT", "AET", "PEN"]:
                            status_str = "finished"
                        elif status_short in ["1H", "2H", "HT", "ET", "P", "LIVE"]:
                            status_str = "live"
                            
                        home_goals = goals.get("home")
                        away_goals = goals.get("away")
                        score_str = ""
                        result_str = ""
                        
                        if home_goals is not None and away_goals is not None:
                            score_str = f"{home_goals} - {away_goals}"
                            if status_str == "finished":
                                if home_goals > away_goals:
                                    result_str = "home"
                                elif away_goals > home_goals:
                                    result_str = "away"
                                else:
                                    result_str = "draw"
                                    
                        # Perform database write in a short-lived connection
                        temp_db = sqlite3.connect(DATABASE)
                        temp_db.execute("PRAGMA journal_mode=WAL")
                        temp_db.execute("""
                            UPDATE matches
                            SET status = ?, score = ?, result = ?
                            WHERE fixture_id = ?
                        """, (status_str, score_str, result_str, fid))
                        temp_db.commit()
                        temp_db.close()
                        print(f"[BACKGROUND BOT] Updated fixture {fid}: status={status_str}, score={score_str}")
                    else:
                        print(f"[BACKGROUND BOT] No fixture data returned for ID {fid}")
                else:
                    print(f"[BACKGROUND BOT] API Error on fixture {fid}: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"[BACKGROUND BOT] Exception updating fixture {fid}: {e}")
                
            # 2. Update Odds (if not finished)
            if db_status != "finished":
                url_odds = f"https://v3.football.api-sports.io/odds?fixture={fid}"
                try:
                    resp = requests.get(url_odds, headers=headers, timeout=15)
                    time.sleep(7) # Respect per-minute API limit of 10 requests
                    if resp.ok:
                        res = resp.json().get("response", [])
                        if res:
                            bookmakers = res[0].get("bookmakers", [])
                            home_odds = 1.0
                            draw_odds = 1.0
                            away_odds = 1.0
                            found_odds = False
                            
                            for bm in bookmakers:
                                for bet in bm.get("bets", []):
                                    if bet.get("name") == "Match Winner":
                                        for val in bet.get("values", []):
                                            odd_val = float(val.get("odd", 1.0))
                                            if val.get("value") == "Home":
                                                home_odds = odd_val
                                            elif val.get("value") == "Draw":
                                                draw_odds = odd_val
                                            elif val.get("value") == "Away":
                                                away_odds = odd_val
                                        found_odds = True
                                        break
                                if found_odds:
                                    break
                                    
                            # Perform database write in a short-lived connection
                            temp_db = sqlite3.connect(DATABASE)
                            temp_db.execute("PRAGMA journal_mode=WAL")
                            temp_db.execute("""
                                UPDATE matches
                                SET home_odds = ?, draw_odds = ?, away_odds = ?
                                WHERE fixture_id = ?
                            """, (home_odds, draw_odds, away_odds, fid))
                            temp_db.commit()
                            temp_db.close()
                            print(f"[BACKGROUND BOT] Updated odds for fixture {fid}: home={home_odds}, draw={draw_odds}, away={away_odds}")
                        else:
                            print(f"[BACKGROUND BOT] No odds data returned for ID {fid}")
                    else:
                        print(f"[BACKGROUND BOT] API Error on odds {fid}: {resp.status_code} - {resp.text}")
                except Exception as e:
                    print(f"[BACKGROUND BOT] Exception updating odds {fid}: {e}")
                    
        # Update run timestamp in a short-lived connection
        temp_db = sqlite3.connect(DATABASE)
        temp_db.execute("PRAGMA journal_mode=WAL")
        temp_db.execute("INSERT OR REPLACE INTO system_state (key, value) VALUES ('last_api_update', ?)", (today_str,))
        temp_db.commit()
        temp_db.close()
        print("[BACKGROUND BOT] Finished daily fixture and odds synchronization.")
    except Exception as e:
        print(f"[BACKGROUND BOT] General error in sync bot: {e}")
    except Exception as e:
        print(f"[BACKGROUND BOT] General error in sync bot: {e}")


# ─── Auth Decorator ──────────────────────────────────────────────────────────
def login_required(f):
    """Decorator: Giriş yapmamış kullanıcıyı engelle."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Giriş yapmanız gerekiyor.'}), 401
        return f(*args, **kwargs)
    return decorated


# ─── Auth Endpoints ──────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """Yeni kullanıcı kaydı: username + password."""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'error': 'Kullanıcı adı ve şifre zorunludur.'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'Kullanıcı adı 3-20 karakter arasında olmalıdır.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Şifre en az 6 karakter olmalıdır.'}), 400

    db = get_db()
    hashed = generate_password_hash(password)

    try:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Bu kullanıcı adı zaten alınmış.'}), 409

    user = db.execute("SELECT id, username FROM users WHERE username = ?", (username,)).fetchone()
    session['user_id'] = user['id']
    session['username'] = user['username']

    return jsonify({
        'message': 'Kayıt başarılı!',
        'user': {'id': user['id'], 'username': user['username']}
    }), 201


@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Kullanıcı girişi: username + password."""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'error': 'Kullanıcı adı ve şifre zorunludur.'}), 400

    db = get_db()
    user = db.execute("SELECT id, username, password FROM users WHERE username = ?", (username,)).fetchone()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Kullanıcı adı veya şifre hatalı.'}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']

    return jsonify({
        'message': 'Giriş başarılı!',
        'user': {'id': user['id'], 'username': user['username']}
    })


@app.route('/api/logout', methods=['POST'])
def logout():
    """Çıkış yap."""
    session.clear()
    return jsonify({'message': 'Çıkış yapıldı.'})


@app.route('/api/me', methods=['GET'])
def me():
    """Mevcut oturum bilgilerini döndür."""
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200

    db = get_db()
    user = db.execute("SELECT id, username, avatar FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if not user:
        return jsonify({'authenticated': False}), 200

    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'avatar': user['avatar']
        }
    })


@app.route('/api/user/avatar', methods=['POST'])
@login_required
def update_avatar():
    """Kullanıcının profil fotoğrafını (Base64) güncelle."""
    data = request.get_json(silent=True) or {}
    avatar = data.get('avatar')
    
    db = get_db()
    db.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, session['user_id']))
    db.commit()
    
    return jsonify({'message': 'Profil fotoğrafı güncellendi.', 'avatar': avatar})


# ─── Match & Leaderboard Endpoints ───────────────────────────────────────────

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Matches data endpoint mapped dynamically to tabs."""
    db = get_db()
    rows = db.execute("SELECT fixture_id, home_team, away_team, league, match_time, status, result, score, home_odds, draw_odds, away_odds FROM matches WHERE status != 'live' ORDER BY match_time ASC").fetchall()
    
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    today_date = now.strftime('%Y-%m-%d')
    tomorrow_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    day3_date = (now + timedelta(days=2)).strftime('%Y-%m-%d')
    day4_date = (now + timedelta(days=3)).strftime('%Y-%m-%d')
    
    matches_list = []
    for r in rows:
        match_date = r['match_time'][:10]
        if match_date == today_date:
            day_str = 'today'
        elif match_date == tomorrow_date:
            day_str = 'tomorrow'
        elif match_date < today_date:
            day_str = 'yesterday'
        elif match_date == day3_date:
            day_str = 'mon'
        elif match_date >= day4_date:
            day_str = 'tue'
        else:
            day_str = 'calendar'
            
        matches_list.append({
            'id': r['fixture_id'],
            'day': day_str,
            'date': r['match_time'][:10],
            'time': r['match_time'][11:16],
            'league': r['league'] or 'FIFA World Cup',
            'leagueId': (r['league'] or 'FIFA World Cup').lower().replace(' ', '-'),
            'homeTeam': r['home_team'],
            'homeLogo': r['home_team'][:3].upper(),
            'homeLogoBg': 'from-zinc-800 to-zinc-600',
            'homeLogoText': 'text-white',
            'awayTeam': r['away_team'],
            'awayLogo': r['away_team'][:3].upper(),
            'awayLogoBg': 'from-zinc-800 to-zinc-600',
            'awayLogoText': 'text-white',
            'status': 'BITTİ' if r['status'] == 'finished' else 'CANLI' if r['status'] == 'live' else 'YAKINDA',
            'score': r['score'] or '',
            'result': r['result'] or '',
            'homeOdds': r['home_odds'] or 1.0,
            'drawOdds': r['draw_odds'] or 1.0,
            'awayOdds': r['away_odds'] or 1.0
        })
    response = jsonify(matches_list)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Kullanıcıların puanlarını 4 İhtimalli Cezalı Puanlama Algoritması ile hesapla."""
    db = get_db()
    
    users = db.execute("SELECT id, username, avatar FROM users").fetchall()
    predictions = db.execute("""
        SELECT p.user_id, p.choice, p.predicted_difference, p.predicted_home_score, p.predicted_away_score, p.is_totem,
               m.result, m.score, m.home_odds, m.draw_odds, m.away_odds
        FROM predictions p
        JOIN matches m ON p.match_id = m.fixture_id
        WHERE m.status = 'finished' AND m.score != ''
    """).fetchall()
    
    user_points = {u['id']: {'username': u['username'], 'avatar': u['avatar'], 'points': 0, 'wins': 0, 'predictions': 0, 'accuracy': 0} for u in users}
    
    # Toplam bitmiş tahmin sayısı
    total_preds = db.execute("""
        SELECT p.user_id, COUNT(*) as cnt
        FROM predictions p
        JOIN matches m ON p.match_id = m.fixture_id
        WHERE m.status = 'finished'
        GROUP BY p.user_id
    """).fetchall()
    for tp in total_preds:
        uid = tp['user_id']
        if uid in user_points:
            user_points[uid]['predictions'] = tp['cnt']
            
    for p in predictions:
        uid = p['user_id']
        is_totem = bool(p['is_totem'])
        pred_diff = p['predicted_difference'] or 0
        pred_home = p['predicted_home_score']
        pred_away = p['predicted_away_score']
        
        # Parse actual score
        try:
            score_parts = p['score'].split('-')
            actual_home = int(score_parts[0].strip())
            actual_away = int(score_parts[1].strip())
            actual_diff = actual_home - actual_away
        except Exception:
            continue # Invalid score format
            
        # Determine multiplier based on actual winner
        multiplier = 1.0
        if actual_diff > 0:
            multiplier = p['home_odds'] or 1.0
        elif actual_diff == 0:
            multiplier = p['draw_odds'] or 1.0
        else:
            multiplier = p['away_odds'] or 1.0
            
        normal_diff_points = round(3 * multiplier, 2)
        points_earned = 0
        is_win = False
        
        if not is_totem:
            # Normal Prediction
            if pred_diff == actual_diff:
                points_earned = normal_diff_points
                is_win = True
            else:
                points_earned = 0
        else:
            # Totem Prediction
            if pred_home == actual_home and pred_away == actual_away:
                # 1. İhtimal: Tam İsabet
                points_earned = normal_diff_points * 2
                is_win = True
            elif pred_diff == actual_diff:
                # 2. İhtimal: Fark Doğru, Skor Yanlış
                points_earned = normal_diff_points
                is_win = True
            elif (pred_diff > 0 and actual_diff > 0) or (pred_diff < 0 and actual_diff < 0):
                # 3. İhtimal: Sadece Taraf Doğru
                points_earned = -3
            else:
                # 4. İhtimal: Komple Yatış
                points_earned = -5
                
        user_points[uid]['points'] += points_earned
        if is_win:
            user_points[uid]['wins'] += 1
            
    for uid in user_points:
        up = user_points[uid]
        up['points'] = round(up['points'], 2)
        if up['predictions'] > 0:
            up['accuracy'] = int((up['wins'] / up['predictions']) * 100)
            
    leaderboard = []
    current_username = session.get('username')
    for i, user in enumerate(sorted(user_points.values(), key=lambda x: x['points'], reverse=True)):
        leaderboard.append({
            'rank': i + 1,
            'name': user['username'],
            'points': user['points'],
            'wins': user['wins'],
            'predictions': user['predictions'],
            'accuracy': user['accuracy'],
            'isCurrentUser': user['username'] == current_username,
            'initials': user['username'][:2].upper(),
            'avatar': user['avatar']
        })
        
    return jsonify(leaderboard)


# ─── Prediction Endpoints ────────────────────────────────────────────────────

@app.route('/api/predictions', methods=['GET'])
@login_required
def get_predictions():
    """Giriş yapmış kullanıcının tahminlerini döndür."""
    db = get_db()
    rows = db.execute(
        "SELECT match_id, choice, diff, label_text, predicted_difference, predicted_home_score, predicted_away_score, is_totem FROM predictions WHERE user_id = ?",
        (session['user_id'],)
    ).fetchall()

    predictions = {}
    for row in rows:
        predictions[str(row['match_id'])] = {
            'choice': row['choice'],
            'diff': row['diff'],
            'labelText': row['label_text'],
            'predicted_difference': row['predicted_difference'],
            'predicted_home_score': row['predicted_home_score'],
            'predicted_away_score': row['predicted_away_score'],
            'is_totem': row['is_totem'],
            'saved': True
        }

    return jsonify(predictions)


@app.route('/api/predictions', methods=['POST'])
@login_required
def save_prediction():
    """Tahmin kaydet veya güncelle."""
    data = request.get_json(silent=True) or {}
    match_id = data.get('match_id')
    choice = (data.get('choice') or '').strip()
    diff = (data.get('diff') or '1').strip()
    label_text = (data.get('label_text') or '').strip()
    
    predicted_difference = data.get('predicted_difference', 0)
    predicted_home_score = data.get('predicted_home_score')
    predicted_away_score = data.get('predicted_away_score')
    is_totem = data.get('is_totem', 0)

    if not match_id or not choice:
        return jsonify({'error': 'match_id ve choice zorunludur.'}), 400

    db = get_db()
    db.execute("""
        INSERT INTO predictions (user_id, match_id, choice, diff, label_text, predicted_difference, predicted_home_score, predicted_away_score, is_totem)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, match_id) DO UPDATE SET
            choice = excluded.choice,
            diff = excluded.diff,
            label_text = excluded.label_text,
            predicted_difference = excluded.predicted_difference,
            predicted_home_score = excluded.predicted_home_score,
            predicted_away_score = excluded.predicted_away_score,
            is_totem = excluded.is_totem
    """, (session['user_id'], int(match_id), choice, diff, label_text, predicted_difference, predicted_home_score, predicted_away_score, is_totem))
    db.commit()

    return jsonify({'message': 'Tahmin kaydedildi.'})


# ─── Comment Endpoints ───────────────────────────────────────────────────────

@app.route('/api/comments', methods=['GET'])
def get_comments():
    """Tüm yorumları döndür (giriş yapmamış kullanıcılar da görebilir)."""
    db = get_db()
    rows = db.execute("""
        SELECT c.id, c.match_id, c.match_name, c.predict, c.comment, c.created_at,
               u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
        LIMIT 50
    """).fetchall()

    comments = []
    for row in rows:
        comments.append({
            'id': row['id'],
            'userName': row['username'],
            'matchId': str(row['match_id']),
            'matchName': row['match_name'],
            'predict': row['predict'],
            'comment': row['comment'],
            'timeText': row['created_at'],
            'statusText': 'Açık (Maç Bitti)'
        })

    return jsonify(comments)


@app.route('/api/comments', methods=['POST'])
@login_required
def post_comment():
    """Yorum gönder."""
    data = request.get_json(silent=True) or {}
    match_id = data.get('match_id')
    match_name = (data.get('match_name') or '').strip()
    predict = (data.get('predict') or '').strip()
    comment_text = (data.get('comment') or '').strip()

    if not match_id or not comment_text:
        return jsonify({'error': 'match_id ve comment zorunludur.'}), 400

    db = get_db()
    db.execute(
        "INSERT INTO comments (user_id, match_id, match_name, predict, comment) VALUES (?, ?, ?, ?, ?)",
        (session['user_id'], int(match_id), match_name, predict, comment_text)
    )
    db.commit()

    return jsonify({'message': 'Yorum gönderildi.'}), 201


# ─── Static File Serving ─────────────────────────────────────────────────────

@app.route('/')
def index():
    response = send_from_directory('.', 'skorfarki.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ─── Rate Limit Error Handler ────────────────────────────────────────────────

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Çok fazla istek gönderdiniz. Lütfen biraz bekleyin.',
        'retry_after': e.description
    }), 429


# ─── Initialization (Runs under Gunicorn and Development Server) ───────────────
init_db()
# Start the daily background API sync thread
threading.Thread(target=update_matches_from_api, daemon=True).start()


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print(f"  FootyVision Backend başlatıldı! Port: {port}")
    print(f"  http://localhost:{port}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=port)
