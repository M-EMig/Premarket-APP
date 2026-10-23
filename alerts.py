"""Agent 4: Alarm. Prüft Einstiegs-, Gewinn-, Verlust- und Break-even-Marken."""
from datetime import date

import config


def _days_held(pos):
    try:
        return (date.today() - date.fromisoformat(pos["opened"])).days
    except Exception:
        return 0


def check(pf, analyses, prices):
    alerts = []
    for t, pos in pf["positions"].items():
        price = prices.get(t)
        if not price:
            continue
        pnl = (price / pos["avg_price"] - 1) * 100
        if pnl < 0:
            pos["underwater"] = True
        if pnl >= config.TAKE_PROFIT_PCT:
            alerts.append({"ticker": t, "action": "sell", "type": "Gewinnziel",
                           "msg": f"{t}: {pnl:+.1f} % im Plus, Gewinnziel erreicht, aussteigen."})
        elif config.STOP_LOSS_PCT and pnl <= -config.STOP_LOSS_PCT:
            alerts.append({"ticker": t, "action": "sell", "type": "Stop-Loss",
                           "msg": f"{t}: {pnl:+.1f} %, Verlustgrenze erreicht, aussteigen."})
        elif pos.get("underwater") and pnl >= config.BREAK_EVEN_BUFFER_PCT:
            alerts.append({"ticker": t, "action": "sell", "type": "Break-even",
                           "msg": f"{t}: war im Minus, jetzt {pnl:+.1f} %. Ausstieg zum Ausgleich."})
        elif pnl < 0 and config.MAX_UNDERWATER_DAYS and _days_held(pos) > config.MAX_UNDERWATER_DAYS:
            alerts.append({"ticker": t, "action": "sell", "type": "Zeitlimit",
                           "msg": f"{t}: {pnl:+.1f} %, seit über {config.MAX_UNDERWATER_DAYS} Tagen "
                                  f"im Minus, aussteigen statt festhängen."})
        elif pnl < 0:
            alerts.append({"ticker": t, "action": "info", "type": "Im Minus",
                           "msg": f"{t}: {pnl:+.1f} %, warte auf nächstes Plus."})
    for t, a in analyses.items():
        if t in pf["positions"]:
            continue
        if config.TREND_FILTER and a.get("downtrend"):
            continue
        if a["drop20"] <= -config.ENTRY_DIP_PCT:
            alerts.append({"ticker": t, "action": "buy", "type": "Einstieg",
                           "msg": f"{t}: {a['drop20']:.1f} % unter 20-Tage-Hoch "
                                  f"(Kurs {a['price']:.2f}), möglicher Einstieg. Analyst: {a['rec']}."})
    return alerts
