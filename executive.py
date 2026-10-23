"""Agent 3: Executive. Führt Käufe/Verkäufe im SIMULIERTEN Depot aus.
Es wird bewusst kein echter Broker angebunden."""
import json
from datetime import datetime
from pathlib import Path

import config

STATE = Path("state/portfolio.json")


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"cash": config.START_CAPITAL, "positions": {}, "trades": []}


def save(pf):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(pf, indent=2, ensure_ascii=False))


def value(pf, prices):
    return pf["cash"] + sum(p["shares"] * prices.get(t, p["avg_price"])
                            for t, p in pf["positions"].items())


def _log(pf, side, t, shares, price, reason):
    pf["trades"].append({"time": datetime.utcnow().isoformat(timespec="seconds"),
                         "side": side, "ticker": t, "shares": round(shares, 4),
                         "price": round(price, 2), "reason": reason})


def buy(pf, t, price, prices, reason):
    if t in pf["positions"]:
        return None
    budget = min(pf["cash"], value(pf, prices) * config.POSITION_SIZE_PCT / 100)
    if budget < price:
        return None
    shares = budget / price
    pf["cash"] -= budget
    pf["positions"][t] = {"shares": shares, "avg_price": price, "underwater": False,
                          "opened": datetime.utcnow().date().isoformat()}
    _log(pf, "BUY", t, shares, price, reason)
    return f"KAUF {t}: {shares:.2f} Stk. zu {price:.2f} ({reason})"


def sell(pf, t, price, reason):
    pos = pf["positions"].pop(t, None)
    if not pos:
        return None
    pf["cash"] += pos["shares"] * price
    pnl = (price / pos["avg_price"] - 1) * 100
    _log(pf, "SELL", t, pos["shares"], price, reason)
    return f"VERKAUF {t}: {pos['shares']:.2f} Stk. zu {price:.2f}, {pnl:+.1f} % ({reason})"


def run(pf, analyses, alerts, prices, allow_signal_trades=True):
    done = []
    for al in alerts:
        t, p = al["ticker"], prices.get(al["ticker"])
        if not p:
            continue
        if al["action"] == "sell":
            r = sell(pf, t, p, al["type"])
        elif al["action"] == "buy" and analyses.get(t, {}).get("rec") != "SELL" \
                and not (config.TREND_FILTER and analyses.get(t, {}).get("downtrend")):
            r = buy(pf, t, p, prices, al["type"])
        else:
            r = None
        if r:
            done.append(r)
    if allow_signal_trades:
        for t, a in analyses.items():
            if a["rec"] == "BUY" and t not in pf["positions"] \
                    and not (config.TREND_FILTER and a.get("downtrend")):
                r = buy(pf, t, a["price"], prices, "Analyst: BUY")
            elif a["rec"] == "SELL" and t in pf["positions"] \
                    and a["price"] >= pf["positions"][t]["avg_price"]:
                # Im Minus wird nicht auf Signal verkauft, das regelt der Break-even-Alarm
                r = sell(pf, t, a["price"], "Analyst: SELL")
            else:
                r = None
            if r:
                done.append(r)
    return done
