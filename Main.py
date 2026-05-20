import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from logger import write_to_log, log_round_entry
import sqlite3
from economy import CS2EconomyTracker

# ==========================================
# 1. THE MULTIPLAYER DASHBOARD STATE
# ==========================================
dashboard = {
    "round": 0,
    "team": "WAITING",
    "phase": "waiting",
    "enemy_money": 800,
    "enemy_suggestion": "🟢 ECO EXPECTED",
    "team_plan": "Waiting for team buy plan...",
    "team_plan_breakdown": "",
    "team_plan_support": "",
    "purchase_history": [],
    "buy_phase_snapshot": None,
    "suggestion_reserve_per_player": 800,
    "alert": "Waiting for match data...",
    "team_bank": 0,
    "team_roster": {}
}

eco_tracker = CS2EconomyTracker()
last_round_phase = "unknown"
last_health = 100

def draw_dashboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("============================================================")
    print(" 🌐 MULTIPLAYER HUB ACTIVE! Open http://localhost:22222 ")
    print("============================================================")
    print(f" Round: {dashboard['round']:02d} | Team: {dashboard['team']}")
    print("------------------------------------------------------------")
    print(" 🛑 ENEMY TRACKER")
    print(f" Est. Bank : ${dashboard['enemy_money']}")
    print(f" Strategy  : {dashboard['enemy_suggestion']}")
    print("------------------------------------------------------------")
    print(f" 🤝 TEAM ROSTER (Total Bank: ${dashboard['team_bank']})")
    for player, stats in dashboard['team_roster'].items():
        suggestion_buy = stats.get('suggestion_buy', stats.get('suggestion', 'Waiting...'))
        suggestion_for = stats.get('suggestion_for', '')
        suggestion_text = suggestion_buy + (f" | For: {suggestion_for}" if suggestion_for else "")
        print(f"  [{player}] ${stats['money']} | {stats['armor_status']} | {suggestion_text}")
    print("------------------------------------------------------------")
    print(" ⚠️ ALERTS & COMMS")
    print(f" > {dashboard['alert']}")
    print("============================================================\n")


ARMOR_COST = 650
HELMET_COST = 350
KIT_COST = 400
CT_FULL_BUY_COST = 4700
T_FULL_BUY_COST = 4300
UTILITY_COSTS = {
    'smoke': 300,
    'flash': 200,
    'he': 300,
    'molotov': 400,
    'decoy': 50,
}
WEAPON_COSTS = {
    'AK47': 2700,
    'M4A1-S': 3100,
    'M4A4': 3100,
    'AUG': 3300,
    'SG553': 3000,
    'FAMAS': 2250,
    'GALIL': 2000,
    'AWP': 4750,
    'SSG08': 1700,
    'UMP45': 1200,
    'P90': 2350,
    'MP9': 1250,
    'MAC10': 1050,
    'MP7': 1500,
    'MP5SD': 1500,
    'P250': 300,
    'TEC9': 500,
    'CZ75A': 500,
    'DESERTEAGLE': 700,
    'R8REVOLVER': 600,
    'HEGRENADE': 300,
    'SMOKE': 300,
    'FLASH': 200,
    'MOLOTOV': 400,
    'INCENDIARY': 400,
    'DECOY': 50,
}
BASE_UTIL_COST = 1000
FULL_UTIL_TEXT = "smoke + 2 flashes + HE"


def is_enemy_force(enemy_suggestion):
    return "FORCE" in enemy_suggestion or ("FULL BUY" in enemy_suggestion and "HALF" not in enemy_suggestion)


def is_enemy_eco(enemy_suggestion):
    return "ECO" in enemy_suggestion


def get_weapon_cost(weapon_name):
    return WEAPON_COSTS.get(weapon_name.upper(), 0)


def is_primary_weapon(weapon_name):
    return weapon_name.upper() in {
        'AK47', 'M4A1-S', 'M4A4', 'AUG', 'SG553', 'FAMAS', 'GALIL', 'AWP', 'SSG08',
        'UMP45', 'P90', 'MP9', 'MAC10', 'MP7', 'MP5SD'
    }


def best_support_weapon(team):
    if team == 'CT':
        return 'GALIL', WEAPON_COSTS['GALIL']
    return 'AK47', WEAPON_COSTS['AK47']


def get_team_average(dashboard):
    roster = dashboard.get('team_roster', {})
    total_players = max(len(roster), 1)
    return dashboard.get('team_bank', 0) / total_players


def capture_buy_phase_snapshot(dashboard, current_round):
    snapshot = {
        'round': current_round,
        'team_bank': dashboard.get('team_bank', 0),
        'team_plan': dashboard.get('team_plan', ''),
        'players': {},
    }
    start_alive = 0
    for name, info in dashboard.get('team_roster', {}).items():
        alive = 1 if info.get('alive', True) else 0
        start_alive += alive
        snapshot['players'][name] = {
            'money': info.get('money', 0),
            'weapon': info.get('weapon', 'Pistol'),
            'armor': info.get('armor', 0),
            'has_armor': info.get('armor', 0) >= 45,
            'has_primary': is_primary_weapon(info.get('weapon', 'Pistol')),
            'alive': bool(info.get('alive', True)),
        }
    dashboard['buy_phase_snapshot'] = snapshot
    # track alive counts for the upcoming round
    dashboard['start_team_alive'] = start_alive
    dashboard['min_team_alive'] = start_alive
    dashboard['end_team_alive'] = start_alive


def evaluate_plan_followed(plan_summary, spent, team_bank_before, team_bank_after):
    text = plan_summary.lower()
    if 'punish' in text or 'full buy' in text or 'counter force' in text or 'buy enough rifles' in text:
        return spent >= 2600
    if 'armor drops' in text or 'low team economy' in text or 'preserve' in text:
        return spent <= 2400
    if 'balanced plan' in text:
        return 1800 <= spent <= 3800
    return spent >= 1500 or spent <= 2600


def record_round_history(dashboard, current_round, enemy_won, our_team):
    snapshot = dashboard.get('buy_phase_snapshot')
    if not snapshot:
        return

    team_bank_before = snapshot.get('team_bank', 0)
    team_bank_after = dashboard.get('team_bank', 0)
    spent = max(0, team_bank_before - team_bank_after)
    plan_summary = snapshot.get('team_plan', '')
    plan_followed = evaluate_plan_followed(plan_summary, spent, team_bank_before, team_bank_after)
    result = 'loss' if enemy_won else 'win'
    status = 'grey'
    if plan_followed and result == 'win':
        status = 'green'
    elif not plan_followed and result == 'loss':
        status = 'red'
    elif plan_followed and result == 'loss':
        status = 'yellow'
    else:
        status = 'orange'

    player_purchase_details = []
    for name, start in snapshot['players'].items():
        current = dashboard['team_roster'].get(name, {})
        spent_amount = max(0, start['money'] - current.get('money', 0))
        player_purchase_details.append(
            f"{name}: spent ${spent_amount}, {start['weapon']} -> {current.get('weapon', 'Pistol')}"
        )

    history_entry = {
        'round': snapshot['round'],
        'plan_summary': plan_summary,
        'team_bank_before': team_bank_before,
        'team_bank_after': team_bank_after,
        'team_spent': spent,
        'plan_followed': plan_followed,
        'result': result,
        'status': status,
        'player_purchases': player_purchase_details,
        'min_team_alive': dashboard.get('min_team_alive'),
        'end_team_alive': dashboard.get('end_team_alive')
    }

    history = dashboard.get('purchase_history', [])
    history.insert(0, history_entry)
    dashboard['purchase_history'] = history[:10]
    dashboard['buy_phase_snapshot'] = None
    # Persist to sqlite for analytics
    try:
        log_round_entry(history_entry)
    except Exception as e:
        write_to_log('DB', f'Failed to write round entry: {e}')


def choose_drop_target(player_name, roster, drop_value):
    candidates = []
    for teammate_name, teammate_info in roster.items():
        if teammate_name == player_name:
            continue
        teammate_money = teammate_info.get('money', 0)
        if teammate_money >= ARMOR_COST:
            continue
        if teammate_money + drop_value >= ARMOR_COST:
            shortfall = ARMOR_COST - teammate_money
            candidates.append((shortfall, teammate_money, teammate_name))
    if not candidates:
        return None
    candidates.sort(key=lambda entry: (entry[0], entry[1]))
    return candidates[0][2]


def build_dynamic_buy_suggestion(player_name, p_money, has_primary, held_weapon, p_kit, dashboard, current_round):
    team_avg = get_team_average(dashboard)
    enemy_suggestion = dashboard.get('enemy_suggestion', '')
    team_size = max(len(dashboard.get('team_roster', {})), 1)
    enemy_force = is_enemy_force(enemy_suggestion)
    enemy_eco = is_enemy_eco(enemy_suggestion)
    team_bank = dashboard.get('team_bank', 0)

    if current_round == 1 or current_round == 13:
        return "🔫 PISTOL ROUND: Buy armor only. Avoid utility purchases."
    if current_round == 2 or current_round == 14:
        if p_money >= 3000:
            return "🔥 ROUND 2 WIN! FORCE!"
        return "🧊 ROUND 2 LOSS! HARD SAVE."
    if current_round >= 25:
        return "⚔️ OVERTIME: Full buys encouraged — both sides have overtime funds."

    if team_avg < 2000 and p_money > 4000 and has_primary:
        drop_value = estimate_drop_value(held_weapon)
        target_name = choose_drop_target(player_name, dashboard['team_roster'], drop_value)
        if target_name:
            teammate_money = dashboard['team_roster'][target_name].get('money', 0)
            new_money = teammate_money + drop_value
            return (
                f"🤝 IGL SUPPORT: DROP {held_weapon} TO {target_name} "
                f"(they reach ${new_money}, you keep armor)."
            )

    if enemy_force:
        if team_bank >= team_size * 2200 and p_money >= 4300:
            return "🔴 COUNTER FORCE: FULL BUY + UTIL while protecting the bank."
        if p_money >= 3000:
            return "🟡 COUNTER FORCE: HALF BUY + NADES. Keep armor and data utility."
        return "🟥 HOLD: Keep armor and nades. Do not overextend."

    if enemy_eco:
        if p_money >= 4300:
            return "🟩 PUNISH ECO: FULL BUY. Take the round."
        if p_money >= 3000:
            return "🟨 PUNISH ECO: HALF BUY and play for advantage."
        return "🟧 ECO PUNISH: Save and keep armor for the next round."

    if has_primary:
        if p_money >= 3000:
            return f"💸 BANKER: You have {held_weapon}. DROP!"
        return f"✅ SAFE: You have {held_weapon}. SAVE."

    if dashboard['team'] == "CT":
        kit_tax = 0 if p_kit else 400
        full_buy_cost = CT_FULL_BUY_COST + kit_tax
        if p_money >= full_buy_cost:
            return "🟩 FULL BUY"
        if p_money >= 3500:
            return f"🟨 HALF BUY (Spend ${p_money-2000})"
        if p_money >= 2000:
            return f"🟧 LIGHT BUY (Spend ${p_money-2000})"
        return "🟥 HARD SAVE"

    if dashboard['team'] == "T":
        if p_money >= T_FULL_BUY_COST:
            return "🟩 FULL BUY"
        if p_money >= 3000:
            return f"🟨 HALF BUY (Spend ${p_money-2000})"
        if p_money >= 2000:
            return f"🟧 LIGHT BUY (Spend ${p_money-2000})"
        return "🟥 HARD SAVE"

    return "🟧 PLAY CAREFULLY."


def build_team_buy_plan(dashboard, current_round):
    team = dashboard.get('team', 'WAITING')
    enemy_suggestion = dashboard.get('enemy_suggestion', '')
    team_bank = dashboard.get('team_bank', 0)
    team_avg = get_team_average(dashboard)
    team_size = max(len(dashboard.get('team_roster', {})), 1)
    enemy_force = is_enemy_force(enemy_suggestion)
    enemy_eco = is_enemy_eco(enemy_suggestion)
    support_weapon_name, support_weapon_cost = best_support_weapon(team)

    players = []
    for name, info in dashboard.get('team_roster', {}).items():
        weapon = info.get('weapon', 'Pistol')
        has_primary = is_primary_weapon(weapon)
        has_armor = info.get('armor', 0) >= 45
        helmet = info.get('helmet', False)
        players.append({
            'name': name,
            'money': info.get('money', 0),
            'weapon': weapon,
            'has_primary': has_primary,
            'has_armor': has_armor,
            'has_helmet': helmet,
            'needs_armor': not has_armor,
            'needs_weapon': not has_primary,
            'plan': [],
            'role': None,
        })

    players.sort(key=lambda p: p['money'], reverse=True)

    plan_type = 'balanced'
    if current_round == 1 or current_round == 13:
        plan_type = 'pistol'
    elif current_round >= 25:
        plan_type = 'overtime'
    elif enemy_eco and team_bank >= team_size * 2000:
        plan_type = 'punish_eco'
    elif enemy_force and team_bank >= team_size * 2200:
        plan_type = 'counter_force'
    elif team_avg < 1800:
        plan_type = 'eco_protect'
    elif enemy_force:
        plan_type = 'counter_cautious'
    elif enemy_eco:
        plan_type = 'eco_pressure'

    support_targets = [p for p in players if p['needs_weapon'] and p['money'] >= ARMOR_COST]
    helpers = [p for p in players if p['has_primary'] and p['has_armor']]

    assigned_support = []
    # team economy reserve to avoid ruining next round
    reserve_per_player = dashboard.get('suggestion_reserve_per_player', 800)
    for helper in helpers:
        baseline = 0
        if not helper['has_armor']:
            baseline += ARMOR_COST
        if helper['has_primary'] and helper['has_armor']:
            baseline += BASE_UTIL_COST
        available = helper['money'] - baseline
        # ensure support buy is also safe for team economy
        if available >= support_weapon_cost and support_targets and (team_bank - support_weapon_cost) >= (team_size * reserve_per_player):
            target = support_targets.pop(-1)
            helper['plan'].append(
                f"buy {support_weapon_name} for {target['name']} and keep armor + utility"
            )
            target['plan'].append(
                f"keep current utility budget; receive a {support_weapon_name} drop and buy armor"
            )
            assigned_support.append((helper['name'], target['name'], support_weapon_name))
            helper['money'] -= support_weapon_cost

    for player in players:
        if not player['plan']:
            if player['needs_weapon'] and player['has_armor']:
                # prefer buying a support weapon only if affordable and team-safe
                cost_opt = support_weapon_cost + 150
                if player['money'] >= cost_opt and (team_bank - support_weapon_cost) >= (team_size * reserve_per_player):
                    player['plan'].append(f"buy {support_weapon_name} and smoke + flash")
                elif player['money'] >= 2000:
                    player['plan'].append(f"buy {support_weapon_name} and minimal utility")
                else:
                    player['plan'].append("buy armor + light utility and use pistols")
            elif player['needs_weapon'] and not player['has_armor']:
                # prioritize armor, but only suggest if affordable and doesn't wreck team reserve
                if player['money'] >= support_weapon_cost + ARMOR_COST and (team_bank - support_weapon_cost - ARMOR_COST) >= (team_size * reserve_per_player):
                    player['plan'].append(f"buy armor + {support_weapon_name}")
                elif player['money'] >= ARMOR_COST + 700 and (team_bank - ARMOR_COST) >= (team_size * reserve_per_player):
                    player['plan'].append("buy armor + Deagle")
                elif player['money'] >= ARMOR_COST and (team_bank - ARMOR_COST) >= (team_size * reserve_per_player):
                    player['plan'].append("buy armor + smoke and save weapons")
                else:
                    player['plan'].append("save and keep pistols — cannot safely afford armor")
            elif player['has_primary'] and not player['has_armor']:
                if player['money'] >= ARMOR_COST + 500 and (team_bank - ARMOR_COST) >= (team_size * reserve_per_player):
                    player['plan'].append("buy armor + smoke + flash")
                elif player['money'] >= ARMOR_COST and (team_bank - ARMOR_COST) >= (team_size * reserve_per_player):
                    player['plan'].append("buy armor and conserve utility")
                else:
                    player['plan'].append("conserve — cannot afford armor without hurting team bank")
            elif player['has_primary'] and player['has_armor']:
                if team_bank >= team_size * 2200:
                    player['plan'].append("keep current gun, buy full util, and be ready to support a weaker teammate")
                else:
                    # only suggest full util if it's affordable for the team
                    if player['money'] >= BASE_UTIL_COST and (team_bank - BASE_UTIL_COST) >= (team_size * reserve_per_player):
                        player['plan'].append("keep current gun and buy full util if possible")
                    else:
                        player['plan'].append("keep current gun and buy minimal util")
            else:
                player['plan'].append("buy armor and light utility")

    # Build structured suggestions: buy_yourself + buy_for (support drops)
    player_suggestions = {}
    player_instructions = []
    support_map = {h: (t, w) for (h, t, w) in assigned_support}
    for player in players:
        buy_yourself = player['plan'][0] if player['plan'] else "hold current buy plan"
        buy_for = ''
        # If this player is helper buying for someone else
        for (h_name, t_name, w_name) in assigned_support:
            if h_name == player['name']:
                buy_for = f"buy {w_name} for {t_name}"
                break
        # If this player is target of a drop
        for (h_name, t_name, w_name) in assigned_support:
            if t_name == player['name']:
                # target receives drop; ensure they still have armor suggestion if needed
                # do not suggest helmet if round1 or enemy is heavy kitted
                buy_yourself = buy_yourself
                break
        player_suggestions[player['name']] = {
            'buy_yourself': buy_yourself,
            'buy_for': buy_for
        }
        player_instructions.append(f"{player['name']}: {buy_yourself} {(' | ' + buy_for) if buy_for else ''}")

    summary = []
    if plan_type == 'pistol':
        summary.append("Pistol round plan: armor and pistols only. Avoid buying utility.")
    elif plan_type == 'overtime':
        summary.append("Overtime plan: full buys are available; prioritize firepower and sustain.")
    elif plan_type == 'punish_eco':
        summary.append("Enemy eco expected: punish with rifle buys and support from players who already own armor.")
    elif plan_type == 'counter_force':
        summary.append("Enemy force expected: buy enough rifles and utility while assigning support to fragile teammates.")
    elif plan_type == 'counter_cautious':
        summary.append("Enemy force expected: favor armor and utility, only force the rounds that keep the bank intact.")
    elif plan_type == 'eco_pressure':
        summary.append("Enemy eco expected: buy selectively and push with better utility and armor support.")
    elif plan_type == 'eco_protect':
        summary.append("Low team economy: prioritize armor drops and ensure broke players stay alive for the next round.")
    else:
        summary.append("Balanced plan: buy as a team, support weak players, and keep a reserve for the next round.")

    if assigned_support:
        support_lines = []
        for helper_name, target_name, weapon_name in assigned_support:
            support_lines.append(f"{helper_name} buys {weapon_name} for {target_name}.")
        summary.append("Support assignments: " + " ".join(support_lines))

    breakdown = [
        f"Team bank: ${team_bank}, team avg: ${team_avg:.0f}",
        f"Enemy prediction: {dashboard.get('enemy_suggestion', '')}",
    ]
    breakdown.extend(player_instructions)

    return {
        'summary': ' '.join(summary),
        'breakdown': '\n'.join(breakdown),
        'support': '\n'.join(support_lines) if assigned_support else 'No specific support assignments this round.',
        'player_suggestions': player_suggestions,
    }


class GSIRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global dashboard
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(dashboard).encode('utf-8'))
        elif self.path.startswith('/api/analytics'):
            # Return simple analytics from sqlite DB
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'rounds.db')
            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                # overall stats
                c.execute("SELECT COUNT(*), SUM(CASE WHEN result='win' THEN 1 ELSE 0 END), AVG(team_spent) FROM rounds")
                total_rows = c.fetchone() or (0,0,0)
                total_rounds = total_rows[0] or 0
                total_wins = total_rows[1] or 0
                avg_spend = float(total_rows[2] or 0)

                # force/punish stats (plan_summary LIKE '%FORCE%')
                c.execute("SELECT COUNT(*), SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) FROM rounds WHERE UPPER(plan_summary) LIKE '%FORCE%'")
                force_rows = c.fetchone() or (0,0)
                force_attempts = force_rows[0] or 0
                force_wins = force_rows[1] or 0

                # plan_followed stats
                c.execute("SELECT COUNT(*), SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) FROM rounds WHERE plan_followed=1")
                pf_rows = c.fetchone() or (0,0)
                pf_attempts = pf_rows[0] or 0
                pf_wins = pf_rows[1] or 0

                # 4v5 stats (consider rounds where min_team_alive <= 4)
                c.execute("SELECT COUNT(*), SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) FROM rounds WHERE min_team_alive <= 4")
                v45_rows = c.fetchone() or (0,0)
                v45_attempts = v45_rows[0] or 0
                v45_wins = v45_rows[1] or 0

                # Round 2 Force stats
                c.execute("SELECT COUNT(*), SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) FROM rounds WHERE round=2 AND UPPER(plan_summary) LIKE '%FORCE%'")
                r2_rows = c.fetchone() or (0,0)
                r2_attempts = r2_rows[0] or 0
                r2_wins = r2_rows[1] or 0

                # recent rounds (including alive data)
                c.execute("SELECT id, round, result, plan_summary, team_bank_before, team_bank_after, team_spent, plan_followed, status, min_team_alive, end_team_alive FROM rounds ORDER BY id DESC LIMIT 20")
                recent = []
                for row in c.fetchall():
                    rid, rnd, result, plan_summary, bbefore, bafter, spent, pf, status, min_alive, end_alive = row
                    # get purchases
                    c.execute("SELECT player, spent, weapon_from, weapon_to FROM purchases WHERE round=?", (rnd,))
                    purchases = [{'player': r[0], 'spent': r[1], 'weapon_from': r[2], 'weapon_to': r[3]} for r in c.fetchall()]
                    recent.append({
                        'id': rid,
                        'round': rnd,
                        'result': result,
                        'plan_summary': plan_summary,
                        'team_bank_before': bbefore,
                        'team_bank_after': bafter,
                        'team_spent': spent,
                        'plan_followed': bool(pf),
                        'status': status,
                        'min_team_alive': min_alive,
                        'end_team_alive': end_alive,
                        'purchases': purchases
                    })
                conn.close()

                payload = {
                    'total_rounds': total_rounds,
                    'total_wins': total_wins,
                    'win_percentage': (total_wins / total_rounds * 100) if total_rounds else 0,
                    'avg_spend': avg_spend,
                    'force_attempts': force_attempts,
                    'force_wins': force_wins,
                    'force_win_pct': (force_wins / force_attempts * 100) if force_attempts else 0,
                    'plan_followed_attempts': pf_attempts,
                    'plan_followed_wins': pf_wins,
                    'plan_followed_win_pct': (pf_wins / pf_attempts * 100) if pf_attempts else 0,
                    'v45_attempts': v45_attempts,
                    'v45_wins': v45_wins,
                    'v45_win_pct': (v45_wins / v45_attempts * 100) if v45_attempts else 0,
                    'round2_force_attempts': r2_attempts,
                    'round2_force_wins': r2_wins,
                    'round2_force_win_pct': (r2_wins / r2_attempts * 100) if r2_attempts else 0,
                    'recent_rounds': recent
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        elif self.path in ('/analytics', '/analytics.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            current_dir = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(current_dir, "analytics.html")
            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                self.wfile.write(f"<pre>Failed to load analytics page: {e}</pre>".encode('utf-8'))

        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Bulletproof file locator
            current_dir = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(current_dir, "index.html")
            
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()
            self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        global last_round_phase, last_health, dashboard
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8')) if body else {}
        except Exception:
            payload = {}

        # Handle UI reserve updates
        if self.path == '/set_reserve':
            try:
                new_reserve = int(payload.get('reserve', dashboard.get('suggestion_reserve_per_player', 800)))
                dashboard['suggestion_reserve_per_player'] = new_reserve
                write_to_log('UI', f'Set reserve per player to ${new_reserve}')
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'reserve': new_reserve}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if 'round' in payload and 'player' in payload:
            current_phase = payload['round'].get('phase')
            dashboard['phase'] = current_phase or dashboard.get('phase', 'waiting')
            player_name = payload['player'].get('name', 'UnknownPlayer')
            dashboard['team'] = payload['player'].get('team', 'WAITING')
            
            map_round = payload.get('map', {}).get('round', 0)
            current_round = map_round + 1
            dashboard['round'] = current_round

            # 1. Ensure player exists in our roster memory
            if player_name not in dashboard['team_roster']:
                dashboard['team_roster'][player_name] = {
                    "money": 0,
                    "armor": 0,
                    "armor_status": "Waiting...",
                    "suggestion_buy": "Waiting...",
                    "suggestion_for": "",
                    "weapon": "None"
                }

            # 2. --- THE FIX: ALWAYS UPDATE LIVE STATS ---
            # This is now outside of the "freezetime" trigger, so it updates instantly in any phase!
            if 'state' in payload['player']:
                p_money = payload['player']['state'].get('money', 0)
                p_armor = payload['player']['state'].get('armor', 0)
                p_helmet = payload['player']['state'].get('helmet', False)
                p_kit = payload['player']['state'].get('defusekit', False)
                p_health = payload['player']['state'].get('health', 0)
                
                dashboard['team_roster'][player_name]['money'] = p_money
                dashboard['team_roster'][player_name]['armor'] = p_armor
                dashboard['team_roster'][player_name]['health'] = p_health
                dashboard['team_roster'][player_name]['has_kit'] = p_kit
                dashboard['team_roster'][player_name]['alive'] = p_health > 0
                dashboard['team_roster'][player_name]['helmet'] = p_helmet
                
                weapons = payload['player'].get('weapons', {})
                has_primary = False
                held_weapon = ""
                grenades = []
                for key, weapon in weapons.items():
                    # Look for any primary weapon category
                    if weapon.get('type') in ["Rifle", "SniperRifle", "SubMachineGun", "MachineGun", "Shotgun"]:
                        has_primary = True
                        held_weapon = weapon.get('name', '').replace('weapon_', '').upper()
                        break
                # detect grenades from weapons payload
                for key, weapon in weapons.items():
                    try:
                        wtype = weapon.get('type', '')
                        ammo = int(weapon.get('ammo_reserve', 0) or 0)
                    except:
                        wtype = weapon.get('type', '')
                        ammo = 0
                    if wtype == 'Grenade' and ammo > 0:
                        name = weapon.get('name', '').lower()
                        if 'smoke' in name:
                            grenades.append('Smoke')
                        elif 'flash' in name:
                            grenades.append('Flash')
                        elif 'hegrenade' in name or 'he' in name:
                            grenades.append('HE')
                        elif 'molotov' in name or 'incendiary' in name:
                            grenades.append('Molotov')
                        elif 'decoy' in name:
                            grenades.append('Decoy')

                dashboard['team_roster'][player_name]['grenades'] = grenades
                dashboard['team_roster'][player_name]['weapon'] = held_weapon if has_primary else "Pistol"

                # Recalculate Total Team Bank instantly
                dashboard['team_bank'] = sum(player['money'] for player in dashboard['team_roster'].values())

                current_health = payload['player']['state'].get('health', 0)
                if current_health == 0 and last_health > 0:
                    dashboard['alert'] = f"💀 {player_name} DIED!"
                    write_to_log("COMBAT", f"{player_name} died in Round {dashboard['round']}.")
                    draw_dashboard()
                last_health = current_health

                # Update round alive counters
                try:
                    current_alive = sum(1 for p in dashboard.get('team_roster', {}).values() if p.get('alive'))
                    # initialize if missing
                    if 'min_team_alive' not in dashboard or dashboard.get('min_team_alive') is None:
                        dashboard['min_team_alive'] = current_alive
                    dashboard['min_team_alive'] = min(dashboard.get('min_team_alive', current_alive), current_alive)
                    dashboard['end_team_alive'] = current_alive
                except Exception:
                    pass

            # 3. ROUND OVER TRIGGER (Enemy Math)
            if current_phase == "over" and last_round_phase != "over":
                win_team = payload['round'].get('win_team')
                my_team = payload['player'].get('team')
                enemy_won = (win_team != my_team)
                
                bomb_state = payload['round'].get('bomb', '')
                enemy_planted_but_lost = (my_team == "CT" and not enemy_won and bomb_state == "defused")
                
                record_round_history(dashboard, current_round, enemy_won, my_team)
                dashboard = eco_tracker.process_round_end(dashboard, enemy_won, enemy_planted_but_lost)
                draw_dashboard()
                
            # 4. FREEZETIME TRIGGER (Buy Logic & Suggestions ONLY)
            elif current_phase == "freezetime":
                # Armor Logic 
                if p_armor < 45:
                    dashboard['team_roster'][player_name]['armor_status'] = "⚠️ BUY ARMOR!"
                elif p_helmet == False:
                    # Avoid recommending helmets when unaffordable, on pistol round, or enemy is heavily kitted
                    enemy_sugg = dashboard.get('enemy_suggestion', '').upper()
                    enemy_heavy = is_enemy_force(enemy_sugg) or ('AK' in enemy_sugg or 'AWP' in enemy_sugg)
                    if current_round == 1 or enemy_heavy:
                        dashboard['team_roster'][player_name]['armor_status'] = "🛡️ SKIP HELMET (Not recommended)"
                    elif dashboard['team'] == "CT" and dashboard['enemy_money'] >= 4300:
                        dashboard['team_roster'][player_name]['armor_status'] = "🛡️ OK (Skip Helmet)"
                    elif p_money >= HELMET_COST and (dashboard.get('team_bank', 0) - HELMET_COST) >= (len(dashboard.get('team_roster', {})) * dashboard.get('suggestion_reserve_per_player', 800)):
                        dashboard['team_roster'][player_name]['armor_status'] = "🪖 BUY HELMET!"
                    else:
                        dashboard['team_roster'][player_name]['armor_status'] = "🛡️ SKIP HELMET (Cannot afford safely)"
                else:
                    dashboard['team_roster'][player_name]['armor_status'] = "🛡️ DO NOT REFRESH!"

                # Halftime Reset Check
                if current_round == 1 or current_round == 13 or current_round == 25:
                    if last_round_phase != "freezetime": 
                        dashboard = eco_tracker.reset_halftime(dashboard)
                    dashboard['alert'] = "Pistol Round! Enemy economy reset to $800."
                else:
                    dashboard['alert'] = "Buy Phase Started. Check team economy."

                # Personal Buy Logic
                team_plan_result = build_team_buy_plan(dashboard, current_round)
                dashboard['team_plan'] = team_plan_result['summary']
                dashboard['team_plan_breakdown'] = team_plan_result['breakdown']
                dashboard['team_plan_support'] = team_plan_result['support']
                for player_name_key, instruction in team_plan_result['player_suggestions'].items():
                    if player_name_key in dashboard['team_roster']:
                        # instruction is a dict with 'buy_yourself' and 'buy_for'
                        dashboard['team_roster'][player_name_key]['suggestion_buy'] = instruction.get('buy_yourself', '')
                        dashboard['team_roster'][player_name_key]['suggestion_for'] = instruction.get('buy_for', '')

                if last_round_phase != "freezetime":
                    capture_buy_phase_snapshot(dashboard, current_round)

                if last_round_phase != "freezetime":
                    write_to_log(f"ROUND {current_round} START", f"Team Bank: ${dashboard['team_bank']}")
                
                draw_dashboard()

            last_round_phase = current_phase

def run_server():
    server_address = ('0.0.0.0', 22222) 
    httpd = HTTPServer(server_address, GSIRequestHandler)
    write_to_log("SYSTEM", "\n================ NEW MULTIPLAYER SESSION STARTED ================\n")
    draw_dashboard()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run_server()