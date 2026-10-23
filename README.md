# Börsen-Agententeam (Simulation)

Vier Rollen, ein Koordinator (main.py):
1. researcher.py  - News Researcher (Feeds + Aktien-News)
2. analyst.py     - Analyse mit BUY/HOLD/SELL und Begründung
3. executive.py   - führt Käufe/Verkäufe im SIMULIERTEN Depot aus (kein echter Broker)
4. alerts.py      - Alarme: Einstieg bei Rücksetzer, Gewinnziel, Stop-Loss, Break-even-Ausstieg

Einstellungen: config.py (Watchlist, Ziele, Prozente).

## Einrichten (ca. 10 Minuten)
1. Neues privates GitHub-Repo anlegen und diesen Ordner hochladen (inkl. .github/).
2. Settings > Secrets and variables > Actions > New repository secret:
   SMTP_HOST (z. B. smtp.gmail.com), SMTP_USER, SMTP_PASS (bei Gmail ein App-Passwort),
   MAIL_TO, optional ANTHROPIC_API_KEY für die KI-Zusammenfassung.
3. Actions-Tab > stockteam > Run workflow zum Testen.

Zeitplan: Mo-Fr Morgenbericht um ca. 6:00 Uhr, Alarm-Check alle 30 Min. zur Börsenzeit.
Hinweis: GitHub-Cron kann einige Minuten Verspätung haben (UTC; im Winter 5:00 UTC für 6:00 MEZ anpassen).

Lokal testen: pip install -r requirements.txt && python main.py report

Simulation, keine Anlageberatung. Kein Backtest enthalten, Regeln erst testen, bevor echtes Geld im Spiel ist.
