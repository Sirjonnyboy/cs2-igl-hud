from .logger import write_to_log

class CS2EconomyTracker:
    def __init__(self):
        self.loss_streak = 0

    def calculate_loss_bonus(self):
        return min(1400 + (self.loss_streak * 500), 3400)

    def process_round_end(self, dashboard, enemy_won, enemy_planted_but_lost):
        if dashboard['enemy_money'] >= 4500 and dashboard['round'] > 1:
            dashboard['enemy_money'] = max(0, dashboard['enemy_money'] - 4500)
            
        if enemy_won:
            dashboard['enemy_money'] += 3250
            self.loss_streak = max(0, self.loss_streak - 1)
            dashboard['alert'] = "💥 Enemy WON the last round."
            write_to_log(f"ROUND {dashboard['round']} END", "Enemy WON (+3250)")
        else:
            income = self.calculate_loss_bonus()
            if enemy_planted_but_lost:
                income += 800
                dashboard['alert'] = f"💀 Enemy LOST but planted bomb (+${income} total loss bonus)."
                write_to_log(f"ROUND {dashboard['round']} END", f"Enemy LOST & PLANTED (+{income})")
            else:
                dashboard['alert'] = f"💀 Enemy LOST the last round (+${income} loss bonus)."
                write_to_log(f"ROUND {dashboard['round']} END", f"Enemy LOST (+{income})")
                
            dashboard['enemy_money'] += income
            self.loss_streak += 1
            
        dashboard['enemy_money'] = min(dashboard['enemy_money'], 16000)
        
        if dashboard['enemy_money'] >= 4500:
            dashboard['enemy_suggestion'] = "🔴 FULL BUY (Rifles & Util)"
        elif dashboard['enemy_money'] >= 2000:
            dashboard['enemy_suggestion'] = "🟡 FORCE/HALF BUY (SMGs/Deagles)"
        else:
            dashboard['enemy_suggestion'] = "🟢 ECO ROUND (Pistols)"
            
        write_to_log("ENEMY PREDICTION", f"Est. Bank: ${dashboard['enemy_money']} -> {dashboard['enemy_suggestion']}")
        return dashboard

    def reset_halftime(self, dashboard):
        dashboard['enemy_money'] = 800
        self.loss_streak = 0
        dashboard['enemy_suggestion'] = "🟢 ECO EXPECTED"
        write_to_log("SYSTEM", "Halftime / Pistol Round detected. Enemy economy reset to $800.")
        return dashboard