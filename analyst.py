"""Agent 2: Analyst. Technische Kennzahlen -> Empfehlung BUY / HOLD / SELL."""
import os

import config
from data import history


def _rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).rolling(n).mean()
    dn = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100 / (1 + up / dn)


def analyze(ticker):
    df = history(ticker)
    if len(df) < 60:
        return None
    c = df["Close"]
    price = float(c.iloc[-1])
    sma20 = float(c.rolling(20).mean().iloc[-1])
    sma50 = float(c.rolling(50).mean().iloc[-1])
    rsi = float(_rsi(c).iloc[-1])
    high20 = float(c.tail(20).max())
    drop = (price / high20 - 1) * 100
    mom5 = (price / float(c.iloc[-6]) - 1) * 100

    score, why = 0, []
    if price > sma50:
        score += 1; why.append("Kurs über SMA50 (Aufwärtstrend)")
    else:
        score -= 1; why.append("Kurs unter SMA50 (Abwärtstrend)")
    if sma20 > sma50:
        score += 1; why.append("SMA20 über SMA50")
    if rsi < 35:
        score += 1; why.append(f"RSI {rsi:.0f}: überverkauft")
    elif rsi > 70:
        score -= 2; why.append(f"RSI {rsi:.0f}: überkauft")
    if drop <= -config.ENTRY_DIP_PCT:
        score += 1; why.append(f"{drop:.1f} % unter 20-Tage-Hoch (Rücksetzer)")

    rec = "BUY" if score >= 2 else "SELL" if score <= -2 else "HOLD"
    downtrend = price < sma50 and sma20 < sma50
    return {"ticker": ticker, "price": price, "rsi": rsi, "drop20": drop,
            "mom5": mom5, "score": score, "rec": rec, "why": why, "high20": high20,
            "downtrend": downtrend}


def run(extra_tickers: list[str] | None = None):
    res = {}
    all_tickers = list(config.WATCHLIST) + (extra_tickers or [])
    for t in all_tickers:
        try:
            a = analyze(t)
            if a:
                a["from_news"] = t not in config.WATCHLIST
                res[t] = a
        except Exception as ex:
            print(f"Analyse-Fehler {t}: {ex}")
    return res


def summarize_news(news):
    """Optional: Kurzfassung per Claude, sonst einfache Schlagzeilenliste."""
    lines = [f"- {n['title']} ({n['source']})" for n in news["general"][:25]]
    for t, items in news["tickers"].items():
        lines += [f"- [{t}] {n['title']}" for n in items[:3]]
    text = "\n".join(lines)
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not lines:
        return text
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=config.CLAUDE_MODEL, max_tokens=700,
            messages=[{"role": "user", "content":
                       "Fasse diese Schlagzeilen auf Deutsch in max. 8 Stichpunkten zusammen: "
                       "die wichtigsten Startup- und Marktneuigkeiten, jeweils mit einem Satz "
                       "zur möglichen Relevanz für Anleger. Keine Kaufempfehlungen.\n\n" + text}])
        return msg.content[0].text
    except Exception as ex:
        return text + f"\n(Claude-Zusammenfassung fehlgeschlagen: {ex})"
