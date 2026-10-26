"""Einstellungen. Hier passt du alles an."""

WATCHLIST = ["NVDA", "MSFT", "AAPL", "ASML", "SAP.DE", "URTH"]

FEEDS = [
    # Deutsch
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen",
    "https://www.manager-magazin.de/schlagzeilen/index.rss",
    "https://www.boerse.de/rss/boersennews.xml",
    "https://www.finanzen.net/rss/news",
    # International
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.instagram.com/traderepublic?utm_source=ig_web_button_share_sheet&dlrf=ZDNlZDc0MzIxNw==" 
]

# Simuliertes Depot (Paper Trading, kein echtes Geld)
START_CAPITAL = 10_000.0
POSITION_SIZE_PCT = 10        # Anteil des Gesamtdepots pro Kauf

# Alarm-Regeln (Agent 4)
ENTRY_DIP_PCT = 8             # Einstiegs-Alarm: Kurs X % unter dem 20-Tage-Hoch
TAKE_PROFIT_PCT = 15          # Gewinn-Alarm: ab +X % verkaufen
STOP_LOSS_PCT = 15            # harter Verlustdeckel: bei -X % wird verkauft (None = aus)
BREAK_EVEN_BUFFER_PCT = 0.5   # Position im Minus: beim ersten Plus ab +X % raus
MAX_UNDERWATER_DAYS = 30      # Position länger als X Tage im Minus: verkaufen (None = aus)
TREND_FILTER = True           # Einstieg nur, wenn die Aktie nicht klar im Abwärtstrend ist
                              # (klar im Abwärtstrend = Kurs UND SMA20 unter SMA50)

# Optional: Zusammenfassung per Claude (nur wenn ANTHROPIC_API_KEY gesetzt ist)
CLAUDE_MODEL = "claude-haiku-5-5"
