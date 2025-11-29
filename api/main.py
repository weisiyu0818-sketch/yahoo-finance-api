from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
def debug_prices(
    ticker: str,
    period: str = "1y",
    interval: str = "1d"
):
    # No yfinance here yet – just echo input
    return {
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "message": "debug endpoint is working"
    }
