import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd  # yfinance returns DataFrames, we convert them

# -------------------------------------------------------------------
# Logging setup – so Railway logs show what is going on
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------
app = FastAPI(
    title="Yahoo Finance API",
    description="Simple API to fetch stock data using yfinance, deployed on Railway.",
    version="1.0.0",
)

# CORS – keep this so you can call it from GPT / browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Health / root
# -------------------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "Yahoo Finance API is running. Go to /docs for Swagger UI.",
        "status": "ok",
    }


# -------------------------------------------------------------------
# Helper: fetch & serialize history
# -------------------------------------------------------------------
def _get_history_records(ticker: str, period: str, interval: str):
    """
    Shared helper for history endpoints.
    Returns a list[dict] ready for JSON serialization.
    """
    t = ticker.strip().upper()
    logger.info(f"Fetching history for {t}, period={period}, interval={interval}")

    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period, interval=interval)

        if hist is None or hist.empty:
            logger.warning(f"No historical data for {t} (period={period}, interval={interval})")
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for ticker '{t}' with period='{period}', interval='{interval}'."
            )

        # Reset index so the timestamp becomes a column
        hist = hist.reset_index()

        # yfinance uses 'Date' for daily data, 'Datetime' for intraday.
        if "Date" in hist.columns:
            date_col = "Date"
        elif "Datetime" in hist.columns:
            date_col = "Datetime"
        else:
            # fallback – first column is usually the datetime
            date_col = hist.columns[0]

        # Convert timestamps to string for JSON
        hist[date_col] = hist[date_col].astype(str)

        records = hist.to_dict(orient="records")
        logger.info(f"History rows for {t}: {len(records)}")
        return t, records

    except HTTPException:
        # already has good status/message
        raise
    except Exception as e:
        logger.exception(f"Unexpected error fetching history for {t}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error fetching history for '{t}': {e}"
        )


# -------------------------------------------------------------------
# /quote/{ticker} – real-time (delayed) quote via fast_info
# -------------------------------------------------------------------
@app.get("/quote/{ticker}")
def get_quote(ticker: str):
    """
    Get quote data for a specific ticker (e.g., AAPL, TSLA).
    Uses fast_info, with a fallback to history() if needed.
    """
    t = ticker.strip().upper()
    logger.info(f"Fetching quote for {t}")

    try:
        stock = yf.Ticker(t)
        fi = stock.fast_info  # lazy-loading dict-like object

        last_price = getattr(fi, "last_price", None) if fi is not None else None
        previous_close = getattr(fi, "previous_close", None) if fi is not None else None
        currency = getattr(fi, "currency", None) if fi is not None else None

        # Fallback: if last_price is missing, pull from 1d/1m history
        if last_price is None:
            logger.info(f"fast_info.last_price missing for {t}, falling back to history()")
            hist = stock.history(period="1d", interval="1m")
            if hist is not None and not hist.empty:
                last_price = float(hist["Close"].iloc[-1])
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No recent price data available for '{t}'."
                )

        result = {
            "symbol": t,
            "price": last_price,
            "previous_close": previous_close,
            "currency": currency,
        }
        logger.info(f"Quote for {t}: {result}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in /quote for {t}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch quote for '{t}': {e}"
        )


# -------------------------------------------------------------------
# /history/{ticker} – historical OHLCV
# -------------------------------------------------------------------
@app.get("/history/{ticker}")
def get_history(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
):
    """
    Get historical OHLCV data.

    period:
      1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    interval:
      1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h,
      1d, 5d, 1wk, 1mo, 3mo
    """
    t, records = _get_history_records(ticker, period, interval)
    return {"symbol": t, "period": period, "interval": interval, "history": records}


# -------------------------------------------------------------------
# /prices – query-param version of history (backwards-compatible)
# -------------------------------------------------------------------
@app.get("/prices")
def get_prices(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
):
    """
    Convenience endpoint:
    /prices?ticker=AAPL&period=1y&interval=1d

    Same data as /history/{ticker}.
    """
    t, records = _get_history_records(ticker, period, interval)
    return records
