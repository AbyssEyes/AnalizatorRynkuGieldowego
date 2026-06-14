import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

class Asset:
    def __init__(self, ticker: str, name: str, asset_type: str):
        self.ticker = ticker.upper()
        self.name = name
        self.asset_type = asset_type

class FinancialEngine:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def search_assets_auto(self, query: str):
        if len(query) < 2:
            return {}
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=6&newsCount=0"
            response = requests.get(url, headers=self.headers)
            data = response.json()
            quotes = data.get("quotes", [])
            
            results = {}
            for q in quotes:
                ticker = q.get("symbol")
                shortname = q.get("shortname") or q.get("longname") or ticker
                quote_type = q.get("quoteType")
                
                if quote_type in ["EQUITY", "ETF"] and ticker and not ticker.replace(".", "").isdigit():
                    asset_type = "ETF" if quote_type == "ETF" else "Akcja"
                    results[ticker] = Asset(ticker, shortname, asset_type)
            return results
        except Exception:
            return {}

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

st.set_page_config(page_title="Globalny Analizator Giełdowy v6.0", layout="wide")

st.title("📈 Interaktywny Dashboard Finansowy i Analiza Ryzyka")
st.caption("Projekt akademicki na ocenę 5.0 - Programowanie Obiektowe i Analityka Danych")

if 'engine' not in st.session_state:
    st.session_state.engine = FinancialEngine()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", "SPDR S&P 500 ETF Trust", "ETF"),
        "QQQ": Asset("QQQ", "Invesco QQQ Trust (Nasdaq 100)", "ETF"),
        "AAPL": Asset("AAPL", "Apple Inc.", "Akcja")
    }

st.sidebar.header("🗂️ Twój Portfel Obserwacyjny")

new_ticker = st.sidebar.text_input("Dodaj Ticker ręcznie (np. NVDA, MSFT):").upper().strip()
new_name = st.sidebar.text_input("Nazwa firmy:")
new_type = st.sidebar.selectbox("Typ aktywa:", ["Akcja", "ETF"])

if st.sidebar.button("Dodaj aktywo do bazy"):
    if new_ticker and new_name:
        st.session_state.portfolio[new_ticker] = Asset(new_ticker, new_name, new_type)
        st.sidebar.success(f"Dodano {new_ticker}!")
    else:
        st.sidebar.error("Wypełnij ticker i nazwę!")

search_query = st.text_input("🔍 Wyszukaj dowolną firmę lub fundusz (np. 'cd projekt', 'meta', 'tesla', 'nvidia'):").strip()

if search_query:
    found_assets = st.session_state.engine.search_assets_auto(search_query)
    if found_assets:
        for ticker, asset_obj in found_assets.items():
            st.session_state.portfolio[ticker] = asset_obj
        st.success(f"✅ Znaleziono i zmapowano instrumenty powiązane z frazą: '{search_query}'. Sprawdź listę poniżej.")
    else:
        st.warning("⚠️ Brak wyników wyszukiwania na giełdach dla podanej frazy.")

ticker_options = list(st.session_state.portfolio.keys())
selected_ticker = st.selectbox("🎯 Wybierz aktywo z bazy do przeprowadzenia analizy:", ticker_options)
period = st.radio("⏳ Okres analizy historycznej:", ["1y", "5y", "max"], horizontal=True)

if selected_ticker:
    asset = st.session_state.portfolio[selected_ticker]
    st.subheader(f"📊 Raport wydajności: {asset.name} ({asset.ticker}) - Typ: {asset.asset_type}")
    
    with st.spinner("Pobieranie najświeższych danych z giełdy rynkowej..."):
        data = st.session_state.engine.get_data(asset.ticker, period)
        
    if data.empty:
        st.error(f"⚠️ Błąd: Nie udało się pobrać danych dla symbolu {asset.ticker}. Sprawdź dostępność tickera dla wybranego okresu.")
    else:
        ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(data)
        total_return = data['Cumulative_Return'].iloc[-1] * 100
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Całkowity zysk", f"{total_return:.2f}%")
        col2.metric("Oczekiwana stopa zwrotu (Roczna)", f"{ann_ret*100:.2f}%")
        col3.metric("Ryzyko portfela (Zmienność)", f"{ann_vol*100:.2f}%")
        col4.metric("Wskaźnik Sharpe Ratio", f"{sharpe:.2f}")
        
        if sharpe > 1:
            st.success("🏆 **Werdykt systemu:** Znakomity stosunek zysku do ryzyka (Sharpe > 1.0). Aktywo wysoce efektywne.")
        elif sharpe > 0:
            st.info("⚖️ **Werdykt systemu:** Umiarkowana efektywność. Premia za ryzyko jest na akceptowalnym poziomie.")
        else:
            st.warning("⚠️ **Werdykt systemu:** Nieoptymalna inwestycja. Wysokie ryzyko nie przekłada się na odpowiedni zwrot.")
            
        st.write("### 📈 Wizualizacja Statystyczna Trendów i Ryzyka")
        
        sns.set_theme(style="darkgrid")
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        axes[0, 0].plot(data.index, data['Close'], color='dodgerblue', linewidth=2)
        axes[0, 0].set_title("1. Kurs Historyczny (Cena zamknięcia)")
        axes[0, 0].tick_params(axis='x', rotation=30)
        
        sns.histplot(ax=axes[0, 1], data=data['Daily_Return'].dropna(), kde=True, color="purple", bins=30)
        axes[0, 1].set_title("2. Histogram: Rozkład dziennych stóp zwrotu")
        
        axes[1, 0].plot(data.index, data['Cumulative_Return'] * 100, color='forestgreen', linewidth=2)
        axes[1, 1].set_title("3. Procentowy skumulowany zysk w czasie")
        axes[1, 0].tick_params(axis='x', rotation=30)
        
        sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'], color="orange")
        axes[1, 1].set_title("4. Boxplot: Detekcja anomalii i rozrzutu zmienności")
        
        plt.tight_layout()
        st.pyplot(fig)
