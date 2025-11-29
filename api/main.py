import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

# Enable full logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
def get_prices(
    ticker: str,
    period: str = "1y",
    interval: str = "1d"
):
    try:
        logger.info(f"Fetching data for: {ticker}, period={period}, interval={interval}")
        df = yf.download(ticker, period=period, interval=interval)

        # Handle empty DataFrame
        if df is None or df.empty:
            logger.error(f"No data returned for ticker: {ticker}")
            raise HTTPException(
                status_code=404,
                detail=f"No price data found for ticker '{ticker}'."
            )

        logger.info(f"Downloaded {df.shape[0]} rows for {ticker}")
        return df.reset_index().to_dict(orient="records")

    except Exception as e:
        logger.exception(f"Error in /prices endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error fetching data for {ticker}. Error: {str(e)}"
        )

@app.post("/batch_prices")
def get_batch_prices(
    tickers: list[str],
    period: str = "1y",
    interval: str = "1d"
):
    try:
        logger.info(f"Fetching batch data: {tickers}")

        df = yf.download(tickers, period=period, interval=interval, group_by="ticker")
        output = {}

        for t in tickers:
            if t in df:
                df_t = df[t].reset_index()
                output[t] = df_t.to_dict(orient="records")
                logger.info(f"{t}: {len(df_t)} rows")
            else:
                logger.error(f"No data for ticker in batch: {t}")
                output[t] = {"error": f"No data found for ticker '{t}'"}

        return output

    except Exception as e:
        logger.exception(f"Error in /batch_prices endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal batch processing error: {str(e)}"
        )
