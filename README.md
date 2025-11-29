{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Simple Yahoo Finance API\
\
A fast, lightweight API wrapper for Yahoo Finance using [FastAPI](https://fastapi.tiangolo.com/) and [yfinance](https://pypi.org/project/yfinance/).\
\
## \uc0\u55357 \u56960  Quick Deploy\
\
Click the button below to deploy this API directly to Railway.\
\
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)\
\
*Note: When you click the button, select "Deploy from GitHub repo" and choose this repository.*\
\
## \uc0\u55357 \u56545  API Endpoints\
\
Once deployed, you can access the interactive documentation at `https://<YOUR-APP-URL>.up.railway.app/docs`.\
\
### 1. Get Stock Quote\
**Endpoint:** `GET /quote/\{ticker\}`\
**Example:** `/quote/AAPL`\
```json\
\{\
  "symbol": "AAPL",\
  "price": 185.92,\
  "previous_close": 184.80,\
  "currency": "USD"\
\}}