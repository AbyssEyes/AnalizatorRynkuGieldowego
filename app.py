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

# 🛠️ Funkcja formatująca nazwy w stylu terminala XTB
def format_xtb(ticker: str, base_name: str) -> str:
    ticker_upper = ticker.upper()
    if "." not in ticker_upper:
        # Akcje USA (np. AAPL -> AAPL.US)
        return f"{ticker_upper}.US - {base_name}"
    elif ticker_upper.endswith(".WA"):
        # Akcje GPW Polska (np. CDR.WA -> CDR.PL)
        return f"{ticker_upper.replace('.WA', '.PL')} - {base_name}"
    else:
        # Pozostałe (np. Niemcy Xetra .DE) pozostają bez zmian w prefiksie
        return f"{ticker_upper} - {base_name}"

class FinancialEngine:
    def __init__(self):
        # Baza zaktualizowana do czystych nazw dla formatowania XTB
        self.market_map = {
            "nvidia": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVIDIA Corp", [("SMH", "VanEck Semiconductor ETF"), ("QDVE.DE", "iShares S&P 500 Tech Sector")]),
            "nvda": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVIDIA Corp", [("SMH", "VanEck Semiconductor ETF"), ("QDVE.DE", "iShares S&P 500 Tech Sector")]),
            "apple": ("AAPL", "Apple Inc", "APC.DE", "Apple Inc", [("XLK", "Technology Select Sector SPDR"), ("QDVE.DE", "iShares S&P 500 Tech Sector")]),
            "aapl": ("AAPL", "Apple Inc", "APC.DE", "Apple Inc", [("XLK", "Technology Select Sector SPDR"), ("QDVE.DE", "iShares S&P 500 Tech Sector")]),
            "microsoft": ("MSFT", "Microsoft Corp", "MSF.DE", "Microsoft Corp", [("XLK", "Technology Select Sector SPDR"), ("QDVE.DE", "iShares S&P 500 Tech Sector")]),
            "msft": ("MSFT", "Microsoft Corp", "MSF.DE", "Microsoft Corp", [("XLK", "Technology Select Sector SPDR"), ("QDVE.DE", "iShares S&P 500 Tech Sector")]),
            "amazon": ("AMZN", "Amazon.com Inc", "AMZ.DE", "Amazon.com Inc", [("XLY", "Consumer Discretionary Select Sector")]),
            "amzn": ("AMZN", "Amazon.com Inc", "AMZ.DE", "Amazon.com Inc", [("XLY", "Consumer Discretionary Select Sector")]),
            "meta": ("META", "Meta Platforms Inc", "FB2A.DE", "Meta Platforms Inc", [("XLC", "Communication Services Select Sector")]),
            "facebook": ("META", "Meta Platforms Inc", "FB2A.DE", "Meta Platforms Inc", [("XLC", "Communication Services Select Sector")]),
            "google": ("GOOGL", "Alphabet Inc", "ABEA.DE", "Alphabet Inc", [("XLC", "Communication Services Select Sector")]),
            "alphabet": ("GOOGL", "Alphabet Inc", "ABEA.DE", "Alphabet Inc", [("XLC", "Communication Services Select Sector")]),
            "tesla": ("TSLA", "Tesla Inc", "TL0.DE", "Tesla Inc", [("XLY", "Consumer Discretionary Select Sector")]),
            "tsla": ("TSLA", "Tesla Inc", "TL0.DE", "Tesla Inc", [("XLY", "Consumer Discretionary Select Sector")]),
            "netflix": ("NFLX", "Netflix Inc", "NFC.DE", "Netflix Inc", [("XLC", "Communication Services Select Sector")]),
            "nflx": ("NFLX", "Netflix Inc", "NFC.DE", "Netflix Inc", [("XLC", "Communication Services Select Sector")]),
            "cd projekt": ("CDR.WA", "CD Projekt SA", "2CD.DE", "CD Projekt SA", [("ETFW20L.WA", "Beta ETF WIG20TR")]),
            "cdr": ("CDR.WA", "CD Projekt SA", "2CD.DE", "CD Projekt SA", [("ETFW20L.WA", "Beta ETF WIG20TR")]),
            "orlen": ("PKN.WA", "ORLEN SA", "PKN.DE", "ORLEN SA", [("ETFW20L.WA", "Beta ETF WIG20TR")]),
            "dino": ("DNP.WA", "Dino Polska SA", "DNP.DE", "Dino Polska SA", [("ETFW20L.WA", "Beta ETF WIG20TR")])
        }

    def get_data(self, ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
        if not ticker:
            return pd.DataFrame()
        try:
            ticker_data = yf.Ticker(ticker)
            hist = ticker_data.history(period=period, interval=interval)
            
            if hist.empty:
                return pd.DataFrame()
                
            df = pd.DataFrame(hist['Close'])
            df = df.dropna()
            df = df.sort_index()
            
            if df.index.tzinfo is not None:
                df.index = df.index.tz_localize(None)
                
            return df
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

st.set_page_config(page_title="Terminal XTB Pro v13", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f17; color: #e2e8f0; }
    .stApp [data-testid="stHeader"] { background-color: transparent; }
    .stMetric { background-color: #111827; padding: 15px; border-radius: 10px; border: 1px solid #1f2937; }
    div[data-testid="stMetricValue"] { color: #3b82f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #0b0f17; }
    .stTabs [data-baseweb="tab"] { height: 45px; color: #94a3b8; background-color: #111827; border-radius: 5px 5px 0px 0px; padding: 10px 20px; border: 1px solid #1f2937; }
    .stTabs [aria-selected="true"] { background-color: #1f2937; color: #f8fafc; font-weight: bold; border-bottom: 2px solid #3b82f6; }
    div[data-testid="stSidebar"] { background-color: #070a0f; border-right: 1px solid #1f2937; }
    .stDataFrame { background-color: #111827; border-radius: 10px; }
    h1, h2, h3, h4 { color: #f8fafc !important; }
    div[data-testid="stRadio"] > label { display: none; }
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
st.caption("Zaawansowane mapowanie rynkowe | Analiza portfelowa | Terminal Styl XTB")

st.session_state.engine = FinancialEngine()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", format_xtb("SPY", "SPDR S&P 500 ETF Trust"), "ETF"),
        "QQQ": Asset("QQQ", format_xtb("QQQ", "Invesco QQQ Trust Nasdaq 100"), "ETF"),
        "EUNL.DE": Asset("EUNL.DE", format_xtb("EUNL.DE", "iShares Core MSCI World"), "ETF")
    }

with st.sidebar:
    st.header("🗂️ Zarządzanie Bazą")
    search_query = st.text_input("🔍 Wpisz firmę (np. tesla, microsoft):").lower().strip()
    if search_query:
        matched_key = next((key for key in st.session_state.engine.market_map.keys() if key in search_query), None)
        if matched_key:
            t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
            
            st.session_state.portfolio[t_usa] = Asset(t_usa, format_xtb(t_usa, name_usa), "Akcja")
            st.session_state.portfolio[t_eu] = Asset(t_eu, format_xtb(t_eu, name_eu), "Akcja")
            for etf_ticker, etf_name in etfs:
                st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, format_xtb(etf_ticker, etf_name), "ETF")
                
            st.success(f"✅ Dodano powiązania dla: {name_usa}")

    st.divider()
    st.subheader("⏱️ Interwał Wykresu")
    interval_options = {
        "1 Dzień (Standard)": "1d",
        "1 Godzina (Max 730 dni)": "1h",
        "15 Minut (Max 60 dni)": "15m",
        "5 Minut (Max 60 dni)": "5m",
        "1 Minuta (Max 7 dni)": "1m"
    }
    selected_interval_label = st.selectbox("Dokładność punktów danych:", list(interval_options.keys()))
    selected_interval = interval_options[selected_interval_label]

ticker_options = list(st.session_state.portfolio.keys())
display_options = {t: st.session_state.portfolio[t].name for t in ticker_options}

st.markdown("<div style='margin-bottom: -15px; font-weight: bold; color: #94a3b8; font-size: 0.95rem;'>⏳ HORYZONT CZASOWY (ZAKRESY XTB):</div>", unsafe_allow_html=True)

xtb_opts = {
    "1D": "1d", "1W": "5d", "1M": "1mo", "3M": "3mo", "6M": "6mo",
    "YTD": "ytd", "1Y": "1y", "3Y": "3y", "5Y": "5y", "MAX": "max"
}

selected_period_label = st.radio("Okres:", options=list(xtb_opts.keys()), horizontal=True)
selected_period = xtb_opts[selected_period_label]

st.divider()

tab1, tab2 = st.tabs(["📊 Analiza Szczegółowa Aktywa", "⚖️ Porównywarka ETF / Akcji"])

with tab1:
    selected_ticker = st.selectbox("🎯 Wybierz instrument do analizy:", options=ticker_options, format_func=lambda x: display_options[x])
    
    if selected_ticker:
        asset = st.session_state.portfolio[selected_ticker]
        with st.spinner(f"Pobieranie interwału {selected_interval}..."):
            data = st.session_state.engine.get_data(
                asset.ticker, period=selected_period, interval=selected_interval
            )
            
        if data.empty or len(data) < 2:
            st.error(f"⚠️ Konflikt limitów API. Brak wystarczających danych dla interwału '{selected_interval_label}' w okresie '{selected_period_label}'. Zmień parametry w menu po lewej stronie.")
        else:
            ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(data)
            total_return = data['Cumulative_Return'].iloc[-1] * 100
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Całkowity zysk w okresie", f"{total_return:.2f}%")
            c2.metric("Liczba punktów danych", f"{len(data)}")
            c3.metric("Zmienność wykresu", f"{ann_vol*100:.2f}%")
            c4.metric("Wskaźnik Sharpe'a", f"{sharpe:.2f}")
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 9))
            fig.patch.set_facecolor('#0b0f17')
            
            axes[0, 0].plot(data.index, data['Close'], color='#3b82f6', linewidth=2)
            axes[0, 0].set_title(f"Kurs Historyczny: {asset.name} (Okres: {selected_period_label})", color='#f8fafc', fontsize=10)
            
            sns.histplot(ax=axes[0, 1], data=data['Daily_Return'].dropna(), kde=True, color="#8b5cf6", bins=30)
            axes[0, 1].set_title("Rozkład wahań w wybranym interwale", color='#f8fafc', fontsize=10)
            
            axes[1, 0].plot(data.index, data['Cumulative_Return'] * 100, color='#10b981', linewidth=2)
            axes[1, 0].set_title("Skumulowany zysk (%)", color='#f8fafc', fontsize=10)
            
            sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'].dropna(), color="#f59e0b")
            axes[1, 1].set_title("Boxplot zmienności", color='#f8fafc', fontsize=10)
            
            for ax in axes.flat:
                ax.set_facecolor('#111827')
                ax.xaxis.label.set_color('#94a3b8')
                ax.yaxis.label.set_color('#94a3b8')
                ax.tick_params(colors='#94a3b8', labelsize=8)
            
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
                df = st.session_state.engine.get_data(
                    t, period=selected_period, interval=selected_interval
                )
                if not df.empty and len(df) >= 2:
                    ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(df)
                    total_return = df['Cumulative_Return'].iloc[-1] * 100
                    
                    color = palette[idx % len(palette)]
                    asset_display_name = st.session_state.portfolio[t].name
                    ax_comp.plot(df.index, df['Cumulative_Return'] * 100, label=asset_display_name, linewidth=2, color=color)
                    
                    comparison_rows.append({
                        "Instrument (XTB Format)": asset_display_name,
                        "Zysk (%)": round(total_return, 2),
                        "Punkty pomiarowe": len(df),
                        "Zmienność (%)": round(ann_vol * 100, 2),
                        "Wskaźnik Sharpe'a": round(sharpe, 2)
                    })
                elif len(df) < 2:
                    st.warning(f"⚠️ Zignorowano '{st.session_state.portfolio[t].name}' z powodu limitów interwału.")
            
            if comparison_rows:
                ax_comp.set_title(f"Porównanie skumulowanego zysku (%) | Okres: {selected_period_label}", fontsize=12, fontweight='bold', color='#f8fafc')
                ax_comp.set_ylabel("Zysk (%)", color='#94a3b8')
                ax_comp.set_xlabel("Czas", color='#94a3b8')
                ax_comp.tick_params(colors='#94a3b8')
                legend = ax_comp.legend(loc="upper left", facecolor='#111827', edgecolor='#1f2937')
                plt.setp(legend.get_texts(), color='#f8fafc', fontsize=9)
                st.pyplot(fig_comp)
                
                comp_df = pd.DataFrame(comparison_rows).set_index("Instrument (XTB Format)")
                st.markdown("#### 📊 Porównawcze zestawienie liczbowe")
                st.dataframe(comp_df, use_container_width=True)
                
                st.markdown("#### 🧠 Teoretyczny werdykt inwestycyjny")
                best_by_sharpe = max(comparison_rows, key=lambda x: x["Wskaźnik Sharpe'a"])
                best_by_return = max(comparison_rows, key=lambda x: x["Zysk (%)"])
                
                if best_by_sharpe["Instrument (XTB Format)"] == best_by_return["Instrument (XTB Format)"]:
                    st.success(f"🏆 **Zdecydowany faworyt:** Najbardziej opłacalną inwestycją w okresie **{selected_period_label}** był instrument **{best_by_sharpe['Instrument (XTB Format)']}**. Osiągnął najwyższy zwrot ({best_by_sharpe['Zysk (%)']}%) przy najlepszym stosunku zysku do ryzyka (Sharpe: {best_by_sharpe['Wskaźnik Sharpe\'a']}).")
                else:
                    st.info(f"⚖️ **Werdykt zależny od profilu ryzyka:**\n\n"
                            f"* **Maksymalny zysk absolutny:** Najlepiej poradził sobie instrument **{best_by_return['Instrument (XTB Format)']}** ({best_by_return['Zysk (%)']}%).\n"
                            f"* **Optymalne bezpieczeństwo (Zysk/Ryzyko):** Najstabilniejszy okazał się **{best_by_sharpe['Instrument (XTB Format)']}** (Sharpe: **{best_by_sharpe['Wskaźnik Sharpe\'a']}**).")
            else:
                st.error("Brak danych do wyświetlenia po nałożeniu filtrów czasowych.")
