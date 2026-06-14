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
            "tesla": ("TSLA", "Tesla Inc", "TL0.DE", "TL0.DE", [("XLY", "14.2%"), ("QQQ", "2.9%")]),
            "tsla": ("TSLA", "Tesla Inc", "TL0.DE", "TL0.DE", [("XLY", "14.2%")]),
            "netflix": ("NFLX", "Netflix Inc", "NFC.DE", "NFC.DE", [("XLC", "5.1%"), ("PBS", "5.45%")]),
            "nflx": ("NFLX", "Netflix Inc", "NFC.DE", "NFC.DE", [("XLC", "5.1%")]),
            "cd projekt": ("CDR.WA", "CD Projekt SA", "2CD.DE", "2CD.DE", [("GPW20", "5.15%")]),
            "cdr": ("CDR.WA", "CD Projekt SA", "2CD.DE", "2CD.DE", [("GPW20", "5.15%")]),
            "orlen": ("PKN.WA", "ORLEN SA", "PKN.DE", "PKN.DE", [("GPW20", "12.4%")]),
            "dino": ("DNP.WA", "Dino Polska SA", "DNP.DE", "DNP.DE", [("GPW20", "4.9%")])
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

st.set_page_config(page_title="Globalny Analizator ETF v9.5", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f17; color: #e2e8f0; }
    .stMetric { background-color: #111827; padding: 15px; border-radius: 10px; border: 1px solid #1f2937; }
    div[data-testid="stMetricValue"] { color: #3b82f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #0b0f17; }
    .stTabs [data-baseweb="tab"] { height: 45px; color: #94a3b8; background-color: #111827; border-radius: 5px 5px 0px 0px; padding: 10px 20px; border: 1px solid #1f2937; }
    .stTabs [aria-selected="true"] { background-color: #1f2937; color: #f8fafc; font-weight: bold; border-bottom: 2px solid #3b82f6; }
    div[data-testid="stSidebar"] { background-color: #070a0f; border-right: 1px solid #1f2937; }
    .stDataFrame { background-color: #111827; border-radius: 10px; }
    h1, h2, h3 { color: #f8fafc !important; }
    </style>
    """, unsafe_allow_html=True)

sns.set_theme(style="darkgrid", rc={
    "axes.facecolor": "#111827",
    "figure.facecolor": "#0b0f17",
    "text.color": "#f8fafc",
    "axes.labelcolor": "#94a3b8",
    "xtick.color": "#94a3b8",
    "ytick.color": "#94a3b8",
    "grid.color": "#1f2937",
    "grid.linestyle": "--"
})

st.title("📈 Interaktywny Dashboard Finansowy i Analiza Ryzyka")
st.caption("Zaawansowane mapowanie rynkowe | Analiza portfelowa | Porównywarka ETF")

if 'engine' not in st.session_state:
    st.session_state.engine = FinancialEngine()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", "SPY - SPDR S&P 500 ETF Trust (Rynek USA)", "ETF"),
        "QQQ": Asset("QQQ", "QQQ - Invesco QQQ Trust Nasdaq 100 (Rynek USA)", "ETF"),
        "EUNL.DE": Asset("EUNL.DE", "EUNL.DE - iShares Core MSCI World (Europa)", "ETF")
    }

with st.sidebar:
    st.header("🗂️ Zarządzanie Bazą Danych")
    st.subheader("1. Inteligentne Wyszukiwanie")
    search_query = st.text_input("🔍 Wpisz firmę (np. tesla, microsoft, dino):").lower().strip()
    if search_query:
        matched_key = next((key for key in st.session_state.engine.market_map.keys() if key in search_query), None)
        if matched_key:
            t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
            st.session_state.portfolio[t_usa] = Asset(t_usa, f"{t_usa} - {name_usa} (USA)", "Akcja")
            st.session_state.portfolio[t_eu] = Asset(t_eu, f"{t_eu} - {name_usa} (Europa)", "Akcja")
            for etf_ticker, weight in etfs:
                st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, f"{etf_ticker} - Fundusz ETF (Udział: {weight})", "ETF")
            st.success(f"✅ Dodano powiązania dla: {name_usa}")
        else:
            st.warning("⚠️ Brak firmy w bazie demonstracyjnej.")

    st.divider()
    st.subheader("2. Dodawanie Ręczne")
    new_ticker = st.text_input("Ticker (np. TSLA):").upper().strip()
    new_name = st.text_input("Opis:")
    new_type = st.selectbox("Typ:", ["Akcja", "ETF"])
    if st.button("Dodaj do bazy"):
        if new_ticker and new_name:
            st.session_state.portfolio[new_ticker] = Asset(new_ticker, f"{new_ticker} - {new_name}", new_type)
            st.success(f"Dodano {new_ticker}")

ticker_options = list(st.session_state.portfolio.keys())
display_options = {t: st.session_state.portfolio[t].name for t in ticker_options}

col_time1, col_time2 = st.columns([1, 4])
with col_time1:
    st.markdown("<div style='padding-top:15px; font-weight:bold;'>⏳ Okres analizy:</div>", unsafe_allow_html=True)
with col_time2:
    period = st.select_slider("", options=["1mo", "3mo", "6mo", "1y", "3y", "5y", "10y", "max"], value="1y")

tab1, tab2, tab3 = st.tabs(["📊 Analiza Szczegółowa Aktywa", "⚖️ Porównywarka ETF / Akcji", "ℹ️ Instrukcja"])

with tab1:
    selected_ticker = st.selectbox("🎯 Wybierz instrument do analizy:", options=ticker_options, format_func=lambda x: display_options[x])
    
    if selected_ticker:
        asset = st.session_state.portfolio[selected_ticker]
        with st.spinner("Przetwarzanie danych..."):
            data = st.session_state.engine.get_data(asset.ticker, period)
            
        if data.empty:
            st.error(f"⚠️ Brak danych dla symbolu {asset.ticker} w okresie {period}.")
        else:
            ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(data)
            total_return = data['Cumulative_Return'].iloc[-1] * 100
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Całkowity zysk", f"{total_return:.2f}%")
            c2.metric("Oczekiwana stopa zwrotu", f"{ann_ret*100:.2f}%")
            c3.metric("Ryzyko (Zmienność)", f"{ann_vol*100:.2f}%")
            c4.metric("Wskaźnik Sharpe'a", f"{sharpe:.2f}")
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 9))
            fig.patch.set_facecolor('#0b0f17')
            
            axes[0, 0].plot(data.index, data['Close'], color='#3b82f6', linewidth=2)
            axes[0, 0].set_title(f"Kurs Historyczny: {asset.ticker}", color='#f8fafc')
            
            sns.histplot(ax=axes[0, 1], data=data['Daily_Return'].dropna(), kde=True, color="#8b5cf6", bins=30)
            axes[0, 1].set_title("Rozkład stóp zwrotu", color='#f8fafc')
            
            axes[1, 0].plot(data.index, data['Cumulative_Return'] * 100, color='#10b981', linewidth=2)
            axes[1, 0].set_title("Skumulowany zysk (%)", color='#f8fafc')
            
            sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'], color="#f59e0b")
            axes[1, 1].set_title("Boxplot zmienności", color='#f8fafc')
            
            for ax in axes.flat:
                ax.set_facecolor('#111827')
                ax.xaxis.label.set_color('#94a3b8')
                ax.yaxis.label.set_color('#94a3b8')
                ax.tick_params(colors='#94a3b8')
            
            plt.tight_layout()
            st.pyplot(fig)

with tab2:
    st.markdown("### ⚖️ Zestawienie wydajności aktywów")
    
    selected_to_compare = st.multiselect(
        "Wybierz aktywa do porównania:", 
        options=ticker_options, 
        format_func=lambda x: display_options[x],
        default=["SPY", "QQQ"] if "SPY" in ticker_options and "QQQ" in ticker_options else []
    )
    
    if len(selected_to_compare) > 0:
        with st.spinner("Pobieranie i normalizacja danych..."):
            fig_comp, ax_comp = plt.subplots(figsize=(14, 6))
            fig_comp.patch.set_facecolor('#0b0f17')
            ax_comp.set_facecolor('#111827')
            
            comparison_rows = []
            palette = ["#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]
            
            for idx, t in enumerate(selected_to_compare):
                df = st.session_state.engine.get_data(t, period)
                if not df.empty:
                    ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(df)
                    total_return = df['Cumulative_Return'].iloc[-1] * 100
                    
                    color = palette[idx % len(palette)]
                    ax_comp.plot(df.index, df['Cumulative_Return'] * 100, label=f"{t}", linewidth=2, color=color)
                    
                    comparison_rows.append({
                        "Ticker": t,
                        "Typ": st.session_state.portfolio[t].asset_type,
                        "Całkowity zysk (%)": round(total_return, 2),
                        "Roczny zwrot (%)": round(ann_ret * 100, 2),
                        "Ryzyko / Zmienność (%)": round(ann_vol * 100, 2),
                        "Wskaźnik Sharpe'a": round(sharpe, 2)
                    })
            
            if comparison_rows:
                ax_comp.set_title(f"Porównanie skumulowanego zysku (%) w okresie: {period}", fontsize=12, fontweight='bold', color='#f8fafc')
                ax_comp.set_ylabel("Zysk (%)", color='#94a3b8')
                ax_comp.set_xlabel("Data", color='#94a3b8')
                ax_comp.tick_params(colors='#94a3b8')
                legend = ax_comp.legend(loc="upper left", facecolor='#111827', edgecolor='#1f2937')
                plt.setp(legend.get_texts(), color='#f8fafc')
                st.pyplot(fig_comp)
                
                comp_df = pd.DataFrame(comparison_rows).set_index("Ticker")
                st.markdown("#### 📊 Porównawcze zestawienie liczbowe")
                st.dataframe(comp_df, use_container_width=True)
                
                st.markdown("#### 🧠 Teoretyczny werdykt inwestycyjny (Analiza Ryzyka i Efektywności)")
                
                best_by_sharpe = max(comparison_rows, key=lambda x: x["Wskaźnik Sharpe'a"])
                best_by_return = max(comparison_rows, key=lambda x: x["Całkowity zysk (%)"])
                
                if best_by_sharpe["Ticker"] == best_by_return["Ticker"]:
                    st.success(f"🏆 **Zdecydowany faworyt:** Teoretycznie najbardziej opłacalną inwestycją w okresie **{period}** jest **{best_by_sharpe['Ticker']}**. Instrument ten osiągnął zarówno najwyższy całkowity zwrot ({best_by_sharpe['Całkowity zysk (%)']}%), jak i najwyższą efektywność skorygowaną o ryzyko (Wskaźnik Sharpe'a: {best_by_sharpe['Wskaźnik Sharpe\'a']}).")
                else:
                    st.info(f"⚖️ **Werdykt zależny od strategii:**\n\n"
                            f"* **Dla zwrotu absolutnego:** Najbardziej opłacił się **{best_by_return['Ticker']}** z zyskiem na poziomie **{best_by_return['Całkowity zysk (%)']}%**.\n"
                            f"* **Dla optymalnego ryzyka:** Najbardziej efektywny jest **{best_by_sharpe['Ticker']}** (Wskaźnik Sharpe'a: **{best_by_sharpe['Wskaźnik Sharpe\'a']}**), ponieważ generuje najlepszy stosunek zysku do wahań kursu (zmienność wyniosła tylko {best_by_sharpe['Ryzyko / Zmienność (%)']}% w porównaniu do {best_by_return['Ryzyko / Zmienność (%)']}% u konkurenta).")
            else:
                st.error("Brak danych historycznych do porównania.")
    else:
        st.info("👆 Wybierz aktywa z listy wielokrotnego wyboru, aby wygenerować analizę porównawczą.")

with tab3:
    st.markdown("""
    ### 👋 Witaj w Analizatorze Finansowym!
    Ten system pozwala na profesjonalną analizę instrumentów giełdowych.
    
    **Jak korzystać z aplikacji?**
    1. **Dodaj aktywa:** Rozwiń menu po lewej stronie. Wpisz nazwę firmy (np. *Apple*), aby inteligentny silnik znalazł powiązane akcje i fundusze ETF.
    2. **Wybierz okres:** Użyj suwaka powyżej, aby zmienić ramy czasowe (od 1 miesiąca do maksimum).
    3. **Analiza Szczegółowa:** W pierwszej zakładce przeanalizujesz ryzyko (Wskaźnik Sharpe'a) oraz rozkład statystyczny pojedynczej spółki.
    4. **Porównywarka:** W drugiej zakładce nałożysz na siebie kilka funduszy ETF lub akcji, aby zobaczyć, który z nich wygenerował najwyższy zysk procentowy w danym czasie.
    """)
