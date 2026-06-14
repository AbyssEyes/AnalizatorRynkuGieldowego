import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Asset:
    def __init__(self, ticker: str, name: str, asset_type: str):
        self.ticker = ticker.upper()
        self.name = name
        self.asset_type = asset_type

class FinancialEngine:
    def __init__(self):
        pass

    def get_data(self, ticker: str, period: str) -> pd.DataFrame:
        if not ticker:
            return pd.DataFrame()
        try:
            ticker_data = yf.Ticker(ticker)
            hist = ticker_data.history(period=period)
            if hist.empty:
                return pd.DataFrame()
            return pd.DataFrame(hist['Close'])
        except Exception:
            return pd.DataFrame()

    def calculate_metrics(self, df: pd.DataFrame):
        df['Daily_Return'] = df['Close'].pct_change()
        df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
        
        avg_daily = df['Daily_Return'].mean()
        volatility = df['Daily_Return'].std()
        
        annual_return = avg_daily * 252
        annual_volatility = volatility * np.sqrt(252)
        sharpe = (annual_return - 0.02) / annual_volatility if annual_volatility > 0 else 0
        
        return annual_return, annual_volatility, sharpe

    def scan_etfs_for_holding(self, stock_ticker: str) -> list:
        hardcoded_mapping = {
            "NVDA": [
                ("SMH", "VanEck Semiconductor ETF | Udział: 24.10%"), 
                ("SOXX", "iShares Semiconductor ETF | Udział: 8.50%"), 
                ("QDVE.DE", "iShares S&P 500 Tech Sector UCITS ETF | Udział: 6.20%"), 
                ("QQQ", "Invesco QQQ Trust (Nasdaq 100) | Udział: 5.40%")
            ],
            "AAPL": [
                ("XLK", "Technology Select Sector SPDR Fund | Udział: 22.30%"), 
                ("QDVE.DE", "iShares S&P 500 Tech Sector UCITS ETF | Udział: 18.40%"),
                ("QQQ", "Invesco QQQ Trust (Nasdaq 100) | Udział: 8.90%")
            ],
            "MSFT": [
                ("XLK", "Technology Select Sector SPDR Fund | Udział: 21.10%"), 
                ("QDVE.DE", "iShares S&P 500 Tech Sector UCITS ETF | Udział: 19.10%"),
                ("QQQ", "Invesco QQQ Trust (Nasdaq 100) | Udział: 8.60%")
            ],
            "CDR.WA": [
                ("GPW20", "WIG20 Index Fund | Udział: 5.15%")
            ]
        }
        return hardcoded_mapping.get(stock_ticker.upper(), [])

st.set_page_config(page_title="Globalny Analizator Ryzyka ETF v7.0", layout="wide")

st.title("📈 Interaktywny Dashboard Finansowy i Analiza Ryzyka")
st.caption("Projekt akademicki na ocenę 5.0 - Programowanie Obiektowe i Analityka Danych")

st.session_state.engine = FinancialEngine()

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", "SPDR S&P 500 ETF Trust", "ETF"),
        "QQQ": Asset("QQQ", "Invesco QQQ Trust (Nasdaq 100)", "ETF")
    }

st.sidebar.header("🗂️ Twój Portfel Obserwacyjny")
new_ticker = st.sidebar.text_input("Dodaj Ticker ręcznie:").upper().strip()
new_name = st.sidebar.text_input("Nazwa firmy:")
new_type = st.sidebar.selectbox("Typ aktywa:", ["Akcja", "ETF"])

if st.sidebar.button("Dodaj aktywo do bazy"):
    if new_ticker and new_name:
        st.session_state.portfolio[new_ticker] = Asset(new_ticker, new_name, new_type)
        st.sidebar.success(f"Dodano {new_ticker}!")

search_query = st.text_input("🔍 Wpisz nazwę spółki (np. nvidia, cd projekt, apple):").lower().strip()

if search_query:
    if "nvidia" in search_query or "nvda" in search_query:
        main_ticker = "NVDA"
        st.session_state.portfolio["NVDA"] = Asset("NVDA", "NVIDIA Corp (Rynek USA - NASDAQ)", "Akcja")
        st.session_state.portfolio["NVD.DE"] = Asset("NVD.DE", "NVIDIA Corp (Rynek Europejski - Xetra)", "Akcja")
        
        etfs = st.session_state.engine.scan_etfs_for_holding(main_ticker)
        for ticker, desc in etfs:
            st.session_state.portfolio[ticker] = Asset(ticker, desc, "ETF")
        st.success("✅ Zmapowano pomyślnie instrument NVDA (USA), NVD.DE (Europa) oraz fundusze ETF z udziałem powyżej 5%.")
        
    elif "cd projekt" in search_query or "cdr" in search_query:
        main_ticker = "CDR.WA"
        st.session_state.portfolio["CDR.WA"] = Asset("CDR.WA", "CD Projekt SA (Rynek Polski - GPW)", "Akcja")
        st.session_state.portfolio["2CD.DE"] = Asset("2CD.DE", "CD Projekt SA (Rynek Europejski - Borse Frankfurt)", "Akcja")
        
        etfs = st.session_state.engine.scan_etfs_for_holding(main_ticker)
        for ticker, desc in etfs:
            st.session_state.portfolio[ticker] = Asset(ticker, desc, "ETF")
        st.success("✅ Zmapowano pomyślnie instrument CDR.WA (Polska), 2CD.DE (Europa) oraz fundusze powiązane.")
        
    elif "apple
