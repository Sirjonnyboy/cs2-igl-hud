from datetime import datetime
import sqlite3
import os
import sys


def get_app_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(get_app_base_dir(), 'rounds.db')


def write_to_log(event_type, details):
    """Legacy function kept for compatibility. Logs are now only persisted to SQLite."""
    # Console logging for debugging during development
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{event_type}] {details}")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round INTEGER,
            result TEXT,
            plan_summary TEXT,
            team_bank_before INTEGER,
            team_bank_after INTEGER,
            team_spent INTEGER,
            plan_followed INTEGER,
            status TEXT,
            min_team_alive INTEGER,
            end_team_alive INTEGER,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round INTEGER,
            player TEXT,
            spent INTEGER,
            weapon_from TEXT,
            weapon_to TEXT
        )
    ''')
    conn.commit()
    conn.close()


def log_round_entry(history_entry):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO rounds (round, result, plan_summary, team_bank_before, team_bank_after, team_spent, plan_followed, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            history_entry.get('round'),
            history_entry.get('result'),
            history_entry.get('plan_summary'),
            history_entry.get('team_bank_before'),
            history_entry.get('team_bank_after'),
            history_entry.get('team_spent'),
            int(bool(history_entry.get('plan_followed'))),
            history_entry.get('status'),
            datetime.now().isoformat()
        ))
        round_id = c.lastrowid
        purchases = history_entry.get('player_purchases', [])
        for p in purchases:
            # p is like 'Name: spent $X, FROM -> TO'
            # We'll do a best-effort parse
            try:
                name_part, rest = p.split(':', 1)
                spent_str = 0
                weapon_from = ''
                weapon_to = ''
                if 'spent $' in rest:
                    try:
                        spent_str = int(rest.split('spent $')[1].split(',')[0].strip())
                    except:
                        spent_str = 0
                if '->' in rest:
                    parts = rest.split('->')
                    weapon_from = parts[0].split(',')[-1].strip()
                    weapon_to = parts[1].strip()
                c.execute('''
                    INSERT INTO purchases (round, player, spent, weapon_from, weapon_to)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    history_entry.get('round'),
                    name_part.strip(),
                    spent_str,
                    weapon_from,
                    weapon_to
                ))
            except Exception:
                continue
        # Update the inserted round row with min/end alive if present
        try:
            if 'min_team_alive' in history_entry or 'end_team_alive' in history_entry:
                c.execute('''
                    UPDATE rounds SET min_team_alive = ?, end_team_alive = ? WHERE id = ?
                ''', (
                    history_entry.get('min_team_alive'),
                    history_entry.get('end_team_alive'),
                    round_id
                ))
        except Exception:
            pass
        conn.commit()
    except Exception as e:
        write_to_log('DB', f'Failed to log round to DB: {e}')
    finally:
        try:
            conn.close()
        except:
            pass


# Initialize DB on import
init_db()