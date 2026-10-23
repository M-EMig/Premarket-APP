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


def run():
    general = []
    for url in config.FEEDS:
        general += _feed_items(url)
    per_ticker = {t: _ticker_news(t) for t in config.WATCHLIST}
    return {"general": general[:40], "tickers": per_ticker}
