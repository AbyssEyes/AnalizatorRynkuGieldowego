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
                ("SMH", "SMH - VanEck Semiconductor ETF (Udział NVDA: 24.10%)"), 
                ("SOXX", "SOXX - iShares Semiconductor ETF (Udział NVDA: 8.50%)"), 
                ("QDVE.DE", "QDVE.DE - iShares S&P 500 Tech Sector UCITS ETF (Udział NVDA: 6.20%)"), 
                ("QQQ", "QQQ - Invesco QQQ Trust Nasdaq 100 (Udział NVDA: 5.40%)")
            ],
            "AAPL": [
                ("XLK", "XLK - Technology Select Sector SPDR Fund (Udział AAPL: 22.30%)"), 
                ("QDVE.DE", "QDVE.DE - iShares S&P 500 Tech Sector UCITS ETF (Udział AAPL: 18.40%)"),
                ("QQQ", "QQQ - Invesco QQQ Trust Nasdaq 100 (Udział AAPL: 8.90%)")
            ],
            "MSFT": [
                ("XLK", "XLK - Technology Select Sector SPDR Fund (Udział MSFT: 21.10%)"), 
                ("QDVE.DE", "QDVE.DE - iShares S&P 500 Tech Sector UCITS ETF (Udział MSFT: 19.10%)"),
                ("QQQ", "QQQ - Invesco QQQ Trust Nasdaq 100 (Udział MSFT: 8.60%)")
            ],
            "CDR.WA": [
                ("GPW20", "GPW20 - WIG20 Index Fund (Udział CDR: 5.15%)")
            ]
        }
        return hardcoded_mapping.get(stock_ticker.upper(), [])

st.set_page_config(page_title="Globalny Analizator Ryzyka ETF v7.5", layout="wide")

st.title("📈 Interaktywny Dashboard Finansowy i Analiza Ryzyka")
st.caption("Projekt akademicki na ocenę 5.0 - Programowanie Obiektowe i Analityka Danych")

st.session_state.engine = FinancialEngine()

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", "SPY - SPDR S&P 500 ETF Trust (Rynek USA - NYSE)", "ETF"),
        "QQQ": Asset("QQQ", "QQQ - Invesco QQQ Trust Nasdaq 100 (Rynek USA - NASDAQ)", "ETF")
    }

st.sidebar.header("🗂️ Twój Portfel Obserwacyjny")
new_ticker = st.sidebar.text_input("Dodaj Ticker ręcznie (np. TSLA):").upper().strip()
new_name = st.sidebar.text_input("Pełny opis rynkowy (np. Tesla Corp na rynku USA):")
new_type = st.sidebar.selectbox("Typ aktywa:", ["Akcja", "ETF"])

if st.sidebar.button("Dodaj aktywo do bazy"):
    if new_ticker and new_name:
        formatted_name = f"{new_ticker} - {new_name}"
        st.session_state.portfolio[new_ticker] = Asset(new_ticker, formatted_name, new_type)
        st.sidebar.success(f"Dodano {new_ticker}!")

search_query = st.text_input("🔍 Wpisz nazwę spółki (np. nvidia, cd projekt, apple):").lower().strip()

if search_query:
    if "nvidia" in search_query or "nvda" in search_query:
        main_ticker = "NVDA"
        st.session_state.portfolio["NVDA"] = Asset("NVDA", "NVDA - NVIDIA Corp (Rynek USA - NASDAQ)", "Akcja")
        st.session_state.portfolio["NVD.DE"] = Asset("NVD.DE", "NVD.DE - NVIDIA Corp (Rynek Europejski - Xetra)", "Akcja")
        
        etfs = st.session_state.engine.scan_etfs_for_holding(main_ticker)
        for ticker, desc in etfs:
            st.session_state.portfolio[ticker] = Asset(ticker, desc, "ETF")
        st.success("✅ Zmapowano pomyślnie instrumenty spółki NVIDIA oraz fundusze ETF z udziałem powyżej 5%.")
        
    elif "cd projekt" in search_query or "cdr" in search_query:
        main_ticker = "CDR.WA"
        st.session_state.portfolio["CDR.WA"] = Asset("CDR.WA", "CDR.WA - CD Projekt SA (Rynek Polski - GPW)", "Akcja")
        st.session_state.portfolio["2CD.DE"] = Asset("2CD.DE", "2CD.DE - CD Projekt SA (Rynek Europejski - Borse Frankfurt)", "Akcja")
        
        etfs = st.session_state.engine.scan_etfs_for_holding(main_ticker)
        for ticker, desc in etfs:
            st.session_state.portfolio[ticker] = Asset(ticker, desc, "ETF")
        st.success("✅ Zmapowano pomyślnie instrumenty spółki CD Projekt oraz fundusze powiązane.")
        
    elif "apple" in search_query or "aapl" in search_query:
        main_ticker = "AAPL"
        st.session_state.portfolio["AAPL"] = Asset("AAPL", "AAPL - Apple Inc (Rynek USA - NASDAQ)", "Akcja")
        st.session_state.portfolio["APC.DE"] = Asset("APC.DE", "APC.DE - Apple Inc (Rynek Europejski - Xetra)", "Akcja")
        
        etfs = st.session_state.engine.scan_etfs_for_holding(main_ticker)
        for ticker, desc in etfs:
            st.session_state.portfolio[ticker] = Asset(ticker, desc, "ETF")
        st.success("✅ Zmapowano pomyślnie instrumenty spółki Apple oraz fundusze ETF z udziałem powyżej 5%.")
        
    else:
        st.warning("⚠️ Wyszukiwarka demonstracyjna obsługuje zaawansowane mapowanie powiązań i ETF >5% dla głównych spółek giełdowych.")

ticker_options = list(st.session_state.portfolio.keys())

# Dynamiczne mapowanie nazw do wyświetlenia w selektorze: "TICKER - Opis"
display_options = {ticker: st.session_state.portfolio[ticker].name for ticker in ticker_options}
selected_ticker = st.selectbox(
    "🎯 Wybierz instrument z bazy do wygenerowania raportu i wykresów:", 
    options=ticker_options, 
    format_func=lambda x: display_options[x]
)

period = st.radio("⏳ Okres analizy historycznej:", ["1y", "5y", "max"], horizontal=True)

if selected_ticker:
    asset = st.session_state.portfolio[selected_ticker]
    st.subheader(f"📊 Raport wydajności dla: {asset.name}")
    
    with st.spinner("Pobieranie najświeższych danych z giełdy rynkowej..."):
        data = st.session_state.engine.get_data(asset.ticker, period)
        
    if data.empty:
        st.error(f"⚠️ Brak danych historycznych dla symbolu {asset.ticker} w wybranym okresie.")
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
        axes[1, 0].set_title("3. Procentowy skumulowany zysk w czasie")
        axes[1, 1].tick_params(axis='x', rotation=30)
        
        sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'], color="orange")
        axes[1, 1].set_title("4. Boxplot: Detekcja anomalii i rozrzutu zmienności")
        
        plt.tight_layout()
        st.pyplot(fig)
