"""Agent 1: News Researcher. Sammelt Schlagzeilen aus Feeds und pro Aktie."""
import time

import feedparser
import yfinance as yf

import config


def _feed_items(url, max_age_h=36):
    out = []
    try:
        feed = feedparser.parse(url)
        for e in feed.entries[:25]:
            t = e.get("published_parsed") or e.get("updated_parsed")
            if t and time.time() - time.mktime(t) > max_age_h * 3600:
                continue
            out.append({"title": e.get("title", "").strip(), "link": e.get("link", ""),
                        "source": feed.feed.get("title", url)})
    except Exception as ex:
        print(f"Feed-Fehler {url}: {ex}")
    return out


def _ticker_news(ticker):
    out = []
    try:
        for n in (yf.Ticker(ticker).news or [])[:5]:
            c = n.get("content", n)
            title = c.get("title")
            link = (c.get("canonicalUrl") or {}).get("url") or c.get("link", "")
            if title:
                out.append({"title": title, "link": link, "source": ticker})
    except Exception as ex:
        print(f"News-Fehler {ticker}: {ex}")
    return out


def extract_tickers_from_news(headlines: list[str]) -> list[str]:
    """Nutzt Claude um aus Schlagzeilen neue Ticker zu extrahieren."""
    import os
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not headlines:
        return []
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        text = "\n".join(f"- {h}" for h in headlines[:40])
        msg = client.messages.create(
            model=config.CLAUDE_MODEL, max_tokens=200,
            messages=[{"role": "user", "content":
                       "Extrahiere aus diesen Schlagzeilen alle klar erkennbaren Börsen-Ticker "
                       "(US und DE). Gib NUR die Ticker zurück, kommagetrennt, keine Erklärung. "
                       "Wenn keine erkennbar sind, antworte mit: KEINE\n\n" + text}])
        raw = msg.content[0].text.strip()
        if raw.upper() == "KEINE" or not raw:
            return []
        tickers = [t.strip().upper() for t in raw.replace(" ", "").split(",") if t.strip()]
        # Nur neue Ticker zurückgeben (nicht schon in Watchlist)
        return [t for t in tickers if t not in config.WATCHLIST][:5]
    except Exception as ex:
        print(f"Ticker-Extraktion fehlgeschlagen: {ex}")
        return []


def run():
    general = []
    for url in config.FEEDS:
        general += _feed_items(url)
    # Neue Ticker aus News extrahieren
    headlines = [n["title"] for n in general]
    new_tickers = extract_tickers_from_news(headlines)
    if new_tickers:
        print(f"Neue Ticker aus News: {new_tickers}")
    all_tickers = list(config.WATCHLIST) + new_tickers
    per_ticker = {t: _ticker_news(t) for t in all_tickers}
    return {"general": general[:40], "tickers": per_ticker, "new_tickers": new_tickers}
