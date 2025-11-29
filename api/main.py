from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/prices")
def get_price(
    ticker: str,
    period: str = "1y",
    interval: str = "1d"
):
    df = yf.download(ticker, period=period, interval=interval)
    return df.reset_index().to_dict(orient="records")

@app.post("/batch_prices")
def get_batch_prices(
    tickers: list[str],
    period: str = "1y",
    interval: str = "1d"
):
    df = yf.download(tickers, period=period, interval=interval, group_by="ticker")
    output = {}
    for t in tickers:
        output[t] = df[t].reset_index().to_dict(orient="records")
    return output
