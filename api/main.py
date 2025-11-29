from fastapi import FastAPI, HTTPException
import yfinance as yf
import pandas as pd
import json

app = FastAPI(
    title="Yahoo Finance API",
    description="A simple API to fetch stock data using yfinance deployed on Railway.",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Yahoo Finance API is running. Go to /docs for the swagger UI."}

@app.get("/quote/{ticker}")
def get_quote(ticker: str):
    """
    Get real-time (delayed) quote data for a specific ticker (e.g., AAPL, TSLA).
    """
    try:
        stock = yf.Ticker(ticker)
        # fast_info often provides faster/more reliable access to current price than .info
        return {
            "symbol": ticker.upper(),
            "price": stock.fast_info.last_price,
            "previous_close": stock.fast_info.previous_close,
            "currency": stock.fast_info.currency
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/history/{ticker}")
def get_history(ticker: str, period: str = "1mo", interval: str = "1d"):
    """
    Get historical data.
    - **period**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    - **interval**: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        
        # Convert timestamp index to string for JSON serialization
        hist.reset_index(inplace=True)
        hist['Date'] = hist['Date'].astype(str)
        
        # Convert to dictionary format
        data = hist.to_dict(orient="records")
        return {"symbol": ticker.upper(), "history": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
