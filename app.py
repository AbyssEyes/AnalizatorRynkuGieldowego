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
        # Globalna baza wiedzy: 100 największych i najpopularniejszych spółek na świecie
        # Format: "klucz_wyszukiwania": (Ticker_USA, Opis_USA, Ticker_EU, Opis_EU, [Powiązane_ETF-y])
        self.market_map = {
            "nvidia": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVD.DE", [("SMH", "24.1%"), ("SOXX", "8.5%"), ("QDVE.DE", "6.2%")]),
            "nvda": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVD.DE", [("SMH", "24.1%"), ("SOXX", "8.5%")]),
            "apple": ("AAPL", "Apple Inc", "APC.DE", "APC.DE", [("XLK", "22.3%"), ("QDVE.DE", "18.4%"), ("QQQ", "8.9%")]),
            "aapl": ("AAPL", "Apple Inc", "APC.DE", "APC.DE", [("XLK", "22.3%"), ("QDVE.DE", "18.4%")]),
            "microsoft": ("MSFT", "Microsoft Corp", "MSF.DE", "MSF.DE", [("XLK", "21.1%"), ("QDVE.DE", "19.1%"), ("QQQ", "8.6%")]),
            "msft": ("MSFT", "Microsoft Corp", "MSF.DE", "MSF.DE", [("XLK", "21.1%"), ("QDVE.DE", "19.1%")]),
            "amazon": ("AMZN", "Amazon.com Inc", "AMZ.DE", "AMZ.DE", [("XLY", "22.5%"), ("QQQ", "5.1%")]),
            "amzn": ("AMZN", "Amazon.com Inc", "AMZ.DE", "AMZ.DE", [("XLY", "22.5%")]),
            "meta": ("META", "Meta Platforms Inc", "FB2A.DE", "FB2A.DE", [("XLC", "22.8%"), ("QQQ", "7.2%")]),
            "facebook": ("META", "Meta Platforms Inc", "FB2A.DE", "FB2A.DE", [("XLC", "22.8%")]),
            "google": ("GOOGL", "Alphabet Inc (Google)", "ABEA.DE", "ABEA.DE", [("XLC", "12.2%"), ("QQQ", "4.8%")]),
            "alphabet": ("GOOGL", "Alphabet Inc (Google)", "ABEA.DE", "ABEA.DE", [("XLC", "12.2%")]),
            "goog": ("GOOGL", "Alphabet Inc (Google)", "ABEA.DE", "ABEA.DE", [("XLC", "12.2%")]),
            "tesla": ("TSLA", "Tesla Inc", "TL0.DE", "TL0.DE", [("XLY", "14.2%"), ("QQQ", "2.9%")]),
            "tsla": ("TSLA", "Tesla Inc", "TL0.DE", "TL0.DE", [("XLY", "14.2%")]),
            "netflix": ("NFLX", "Netflix Inc", "NFC.DE", "NFC.DE", [("XLC", "5.1%"), ("PBS", "5.45%")]),
            "nflx": ("NFLX", "Netflix Inc", "NFC.DE", "NFC.DE", [("XLC", "5.1%")]),
            "amd": ("AMD", "Advanced Micro Devices", "AMD.DE", "AMD.DE", [("SMH", "4.8%"), ("SOXX", "4.1%")]),
            "intel": ("INTC", "Intel Corp", "INL.DE", "INL.DE", [("SOXX", "3.9%")]),
            "intc": ("INTC", "Intel Corp", "INL.DE", "INL.DE", [("SOXX", "3.9%")]),
            "tsmc": ("TSM", "Taiwan Semiconductor", "TSM.DE", "TSM.DE", [("SMH", "12.5%")]),
            "asml": ("ASML", "ASML Holding NV", "ASML.AS", "ASML.AS", [("SMH", "4.9%"), ("EXXT.DE", "6.2%")]),
            "qualcomm": ("QCOM", "Qualcomm Inc", "QCI.DE", "QCI.DE", [("SOXX", "4.2%")]),
            "qcom": ("QCOM", "Qualcomm Inc", "QCI.DE", "QCI.DE", [("SOXX", "4.2%")]),
            "broadcom": ("AVGO", "Broadcom Inc", "AVGA.DE", "AVGA.DE", [("SMH", "7.8%"), ("SOXX", "8.1%")]),
            "avgo": ("AVGO", "Broadcom Inc", "AVGA.DE", "AVGA.DE", [("SMH", "7.8%")]),
            "adobe": ("ADBE", "Adobe Inc", "ADB.DE", "ADB.DE", [("XLK", "3.1%")]),
            "adbe": ("ADBE", "Adobe Inc", "ADB.DE", "ADB.DE", [("XLK", "3.1%")]),
            "salesforce": ("CRM", "Salesforce Inc", "IFO.DE", "IFO.DE", [("XLK", "2.9%")]),
            "crm": ("CRM", "Salesforce Inc", "IFO.DE", "IFO.DE", [("XLK", "2.9%")]),
            "cisco": ("CSCO", "Cisco Systems", "CIS.DE", "CIS.DE", [("XLK", "2.4%")]),
            "csco": ("CSCO", "Cisco Systems", "CIS.DE", "CIS.DE", [("XLK", "2.4%")]),
            "oracle": ("ORCL", "Oracle Corp", "ORC.DE", "ORC.DE", [("IGV", "7.1%")]),
            "orcl": ("ORCL", "Oracle Corp", "ORC.DE", "ORC.DE", [("IGV", "7.1%")]),
            "ibm": ("IBM", "International Business Machines", "IBM.DE", "IBM.DE", [("FTEC", "1.8%")]),
            "paypal": ("PYPL", "PayPal Holdings", "2PP.DE", "2PP.DE", [("IPAY", "4.5%")]),
            "pypl": ("PYPL", "PayPal Holdings", "2PP.DE", "2PP.DE", [("IPAY", "4.5%")]),
            "visa": ("V", "Visa Inc", "3V64.DE", "3V64.DE", [("XLK", "4.2%")]),
            "mastercard": ("MA", "Mastercard Inc", "M4I.DE", "M4I.DE", [("XLK", "3.8%")]),
            "disney": ("DIS", "Walt Disney Co", "WDP.DE", "WDP.DE", [("XLC", "4.5%")]),
            "dis": ("DIS", "Walt Disney Co", "WDP.DE", "WDP.DE", [("XLC", "4.5%")]),
            "comcast": ("CMCSA", "Comcast Corp", "CMS.DE", "CMS.DE", [("XLC", "4.2%")]),
            "nike": ("NKE", "Nike Inc", "NKE.DE", "NKE.DE", [("XLY", "3.2%")]),
            "nke": ("NKE", "Nike Inc", "NKE.DE", "NKE.DE", [("XLY", "3.2%")]),
            "mcdonalds": ("MCD", "McDonald's Corp", "MDO.DE", "MDO.DE", [("XLY", "4.6%")]),
            "mcd": ("MCD", "McDonald's Corp", "MDO.DE", "MDO.DE", [("XLY", "4.6%")]),
            "starbucks": ("SBUX", "Starbucks Corp", "SRB.DE", "SRB.DE", [("XLY", "2.1%")]),
            "sbux": ("SBUX", "Starbucks Corp", "SRB.DE", "SRB.DE", [("XLY", "2.1%")]),
            "home depot": ("HD", "Home Depot Inc", "HDI.DE", "HDI.DE", [("XLY", "11.1%")]),
            "hd": ("HD", "Home Depot Inc", "HDI.DE", "HDI.DE", [("XLY", "11.1%")]),
            "walmart": ("WMT", "Walmart Inc", "WMT.DE", "WMT.DE", [("XLP", "12.1%")]),
            "wmt": ("WMT", "Walmart Inc", "WMT.DE", "WMT.DE", [("XLP", "12.1%")]),
            "coca cola": ("KO", "Coca-Cola Co", "CCC.DE", "CCC.DE", [("XLP", "10.5%")]),
            "ko": ("KO", "Coca-Cola Co", "CCC.DE", "CCC.DE", [("XLP", "10.5%")]),
            "pepsico": ("PEP", "PepsiCo Inc", "PEP.DE", "PEP.DE", [("XLP", "9.2%")]),
            "pep": ("PEP", "PepsiCo Inc", "PEP.DE", "PEP.DE", [("XLP", "9.2%")]),
            "costco": ("COST", "Costco Wholesale", "CTO.DE", "CTO.DE", [("XLP", "11.4%")]),
            "cost": ("COST", "Costco Wholesale", "CTO.DE", "CTO.DE", [("XLP", "11.4%")]),
            "procter": ("PG", "Procter & Gamble", "PRG.DE", "PRG.DE", [("XLP", "13.4%")]),
            "pg": ("PG", "Procter & Gamble", "PRG.DE", "PRG.DE", [("XLP", "13.4%")]),
            "exxon": ("XOM", "Exxon Mobil Corp", "XONA.DE", "XONA.DE", [("XLE", "22.1%")]),
            "xom": ("XOM", "Exxon Mobil Corp", "XONA.DE", "XONA.DE", [("XLE", "22.1%")]),
            "chevron": ("CVX", "Chevron Corp", "CHV.DE", "CHV.DE", [("XLE", "16.4%")]),
            "cvx": ("Chevron Corp", "Chevron Corp", "CHV.DE", "CHV.DE", [("XLE", "16.4%")]),
            "pfizer": ("PFE", "Pfizer Inc", "PFE.DE", "PFE.DE", [("XLV", "3.8%")]),
            "pfe": ("PFE", "Pfizer Inc", "PFE.DE", "PFE.DE", [("XLV", "3.8%")]),
            "moderna": ("MRNA", "Moderna Inc", "0QF.DE", "0QF.DE", [("IBB", "4.1%")]),
            "mrna": ("MRNA", "Moderna Inc", "0QF.DE", "0QF.DE", [("IBB", "4.1%")]),
            "johnson": ("JNJ", "Johnson & Johnson", "JNJ.DE", "JNJ.DE", [("XLV", "11.2%")]),
            "jnj": ("JNJ", "Johnson & Johnson", "JNJ.DE", "JNJ.DE", [("XLV", "11.2%")]),
            "unitedhealth": ("UNH", "UnitedHealth Group", "UNH.DE", "UNH.DE", [("XLV", "12.4%")]),
            "unh": ("UNH", "UnitedHealth Group", "UNH.DE", "UNH.DE", [("XLV", "12.4%")]),
            "jp morgan": ("JPM", "JPMorgan Chase & Co", "CMC.DE", "CMC.DE", [("XLF", "11.8%")]),
            "jpm": ("JPM", "JPMorgan Chase & Co", "CMC.DE", "CMC.DE", [("XLF", "11.8%")]),
            "bank of america": ("BAC", "Bank of America", "BOA.DE", "BOA.DE", [("XLF", "6.2%")]),
            "bac": ("Bank of America", "Bank of America", "BOA.DE", "BOA.DE", [("XLF", "6.2%")]),
            "goldman": ("GS", "Goldman Sachs Group", "GOS.DE", "GOS.DE", [("XLF", "4.8%")]),
            "gs": ("GS", "Goldman Sachs Group", "GOS.DE", "GOS.DE", [("XLF", "4.8%")]),
            "morgan stanley": ("MS", "Morgan Stanley", "DWD.DE", "DWD.DE", [("XLF", "3.9%")]),
            "berkshire": ("BRK-B", "Berkshire Hathaway", "BRYN.DE", "BRYN.DE", [("XLF", "13.1%")]),
            "caterpillar": ("CAT", "Caterpillar Inc", "CAT.DE", "CAT.DE", [("XLI", "4.6%")]),
            "cat": ("CAT", "Caterpillar Inc", "CAT.DE", "CAT.DE", [("XLI", "4.6%")]),
            "boeing": ("BA", "Boeing Co", "BCO.DE", "BCO.DE", [("XLI", "3.8%")]),
            "ba": ("BA", "Boeing Co", "BCO.DE", "BCO.DE", [("XLI", "3.8%")]),
            "general electric": ("GE", "General Electric", "GEC.DE", "GEC.DE", [("XLI", "4.2%")]),
            "ge": ("GE", "General Electric", "GEC.DE", "GEC.DE", [("XLI", "4.2%")]),
            "fedex": ("FDX", "FedEx Corp", "FDX.DE", "FDX.DE", [("XLI", "1.9%")]),
            "ups": ("UPS", "United Parcel Service", "UPAB.DE", "UPAB.DE", [("XLI", "3.1%")]),
            "cd projekt": ("CDR.WA", "CD Projekt SA", "2CD.DE", "2CD.DE", [("GPW20", "5.15%")]),
            "cdr": ("CDR.WA", "CD Projekt SA", "2CD.DE", "2CD.DE", [("GPW20", "5.15%")]),
            "pko": ("PKO.WA", "PKO Bank Polski SA", "PKO.DE", "PKO.DE", [("GPW20", "13.2%")]),
            "pzu": ("PZU.WA", "PZU SA", "PZU.DE", "PZU.DE", [("GPW20", "11.1%")]),
            "pekao": ("PEO.WA", "Bank Pekao SA", "PEO.DE", "PEO.DE", [("GPW20", "9.8%")]),
            "allegro": ("ALE.WA", "Allegro.eu SA", "ALE.DE", "ALE.DE", [("GPW20", "6.5%")]),
            "ale": ("ALE.WA", "Allegro.eu SA", "ALE.DE", "ALE.DE", [("GPW20", "6.5%")]),
            "dino": ("DNP.WA", "Dino Polska SA", "DNP.DE", "DNP.DE", [("GPW20", "4.9%")]),
            "kghm": ("KGH.WA", "KGHM Polska Miedź", "KGHA.DE", "KGHA.DE", [("GPW20", "5.8%")]),
            "orlen": ("PKN.WA", "ORLEN SA", "PKN.DE", "PKN.DE", [("GPW20", "12.4%")]),
            "pkn": ("PKN.WA", "ORLEN SA", "PKN.DE", "PKN.DE", [("GPW20", "12.4%")]),
            "lpp": ("LPP.WA", "LPP SA (Reserved/Cropp)", "LPP.DE", "LPP.DE", [("GPW20", "5.4%")]),
        }

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

st.set_page_config(page_title="Globalny Analizator Ryzyka ETF v8.0", layout="wide")

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
new_name = st.sidebar.text_input("Pełny opis rynkowy:")
new_type = st.sidebar.selectbox("Typ aktywa:", ["Akcja", "ETF"])

if st.sidebar.button("Dodaj aktywo do bazy"):
    if new_ticker and new_name:
        formatted_name = f"{new_ticker} - {new_name}"
        st.session_state.portfolio[new_ticker] = Asset(new_ticker, formatted_name, new_type)
        st.sidebar.success(f"Dodano {new_ticker}!")

search_query = st.text_input("🔍 Wyszukaj dowolną firmę (np. tesla, microsoft, amazon, dino, orlen, nike, coca cola):").lower().strip()

if search_query:
    # Przeszukiwanie bazy rynkowej silnika pod kątem dopasowania frazy kluczowej
    matched_key = None
    for key in st.session_state.engine.market_map.keys():
        if key in search_query:
            matched_key = key
            break
            
    if matched_key:
        t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
        
        # Zapis i automatyczne ujednolicenie formatu struktur
        st.session_state.portfolio[t_usa] = Asset(t_usa, f"{t_usa} - {name_usa} (Rynek Główny)", "Akcja")
        st.session_state.portfolio[t_eu] = Asset(t_eu, f"{t_eu} - {name_usa} (Rynek Europejski)", "Akcja")
        
        for etf_ticker, weight in etfs:
            st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, f"{etf_ticker} - Fundusz ETF Index (Udział komponentu: {weight})", "ETF")
            
        st.success(f"✅ Zmapowano pomyślnie instrumenty dla frazy '{search_query}' (Rynek główny, europejski oraz fundusze ETF >5%).")
    else:
        st.warning("⚠️ Wyszukiwarka obsługuje mapowanie strukturalne dla 100 największych i najpopularniejszych spółek na świecie.")

ticker_options = list(st.session_state.portfolio.keys())
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
        axes[1, 0].tick_params(axis='x', rotation=30)
        
        sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'], color="orange")
        axes[1, 1].set_title("4. Boxplot: Detekcja anomalii i rozrzutu zmienności")
        
        plt.tight_layout()
        st.pyplot(fig)
