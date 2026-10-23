"""Koordinator. Aufruf: python main.py report | python main.py alerts"""
import json
import os
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText

import alerts as alert_agent
import analyst
import config
import executive
import researcher
from data import last_price


def send_mail(subject, body):
    host, user, pw, to = (os.environ.get(k) for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_TO"))
    if not all([host, user, pw, to]):
        print("Keine Mail-Zugangsdaten gesetzt, Bericht nur lokal.")
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"], msg["From"], msg["To"] = subject, user, to
    with smtplib.SMTP_SSL(host, int(os.environ.get("SMTP_PORT", 465))) as s:
        s.login(user, pw)
        s.send_message(msg)


def main(mode):
    pf = executive.load()
    analyses = analyst.run()
    prices = {t: (last_price(t) or a["price"]) for t, a in analyses.items()}
    for t in pf["positions"]:
        prices.setdefault(t, last_price(t) or pf["positions"][t]["avg_price"])

    al = alert_agent.check(pf, analyses, prices)
    trades = executive.run(pf, analyses, al, prices, allow_signal_trades=(mode == "report"))
    executive.save(pf)

    triggered = [a for a in al if a["action"] != "info"]
    if mode == "alerts" and not triggered and not trades:
        print("Keine Alarme.")
        return

    lines = [f"Börsen-Team, {datetime.now():%d.%m.%Y %H:%M}", ""]
    if mode == "report":
        news = researcher.run()
        lines += ["== NEWS ==", analyst.summarize_news(news), ""]
    lines.append("== ANALYSE ==")
    for a in sorted(analyses.values(), key=lambda x: -x["score"]):
        lines.append(f"{a['ticker']:8} {a['rec']:5} Kurs {a['price']:.2f}  RSI {a['rsi']:.0f}  "
                     f"vs 20T-Hoch {a['drop20']:+.1f}%  | " + "; ".join(a["why"]))
    lines += ["", "== ALARME =="] + ([f"[{a['type']}] {a['msg']}" for a in al] or ["keine"])
    lines += ["", "== AUSGEFÜHRT (Simulation) =="] + (trades or ["keine Trades"])
    lines += ["", f"Depotwert: {executive.value(pf, prices):.2f} "
                  f"(Start {config.START_CAPITAL:.2f}), Cash {pf['cash']:.2f}",
              "Hinweis: Simulation, keine Anlageberatung."]
    body = "\n".join(lines)
    print(body)
    open("report.md", "w").write(body)

    # JSON für Web-Dashboard
    report_data = {
        "generated": datetime.now().isoformat(),
        "mode": mode,
        "depot": {
            "value": executive.value(pf, prices),
            "start": config.START_CAPITAL,
            "cash": pf["cash"],
            "positions": pf["positions"],
        },
        "analyses": [
            {k: v for k, v in a.items()} for a in
            sorted(analyses.values(), key=lambda x: -x["score"])
        ],
        "alerts": al,
        "trades": trades,
        "news": (researcher.run() if mode == "report" else {"general": [], "tickers": {}}),
    }
    open("report.json", "w").write(json.dumps(report_data, indent=2, ensure_ascii=False))

    subject = "Börsen-Morgenbericht" if mode == "report" else "Börsen-ALARM"
    send_mail(subject, body)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "report")
