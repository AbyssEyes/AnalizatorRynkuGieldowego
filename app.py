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

# 🛠️ Formatyzacja w stylu XTB (np. AAPL.US, CDR.PL)
def format_xtb(ticker: str, base_name: str) -> str:
    ticker_upper = ticker.upper()
    if "." not in ticker_upper:
        return f"{ticker_upper}.US - {base_name}"
    elif ticker_upper.endswith(".WA"):
        return f"{ticker_upper.replace('.WA', '.PL')} - {base_name}"
    else:
        return f"{ticker_upper} - {base_name}"

class FinancialEngine:
    def __init__(self):
        # Baza z precyzyjnie opisanymi wagami (Helper dla Inwestora)
        self.market_map = {
            "nvidia": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVIDIA Corp", [("SMH", "VanEck Semiconductor ETF (Waga NVDA: 24.1%)"), ("QDVE.DE", "iShares S&P 500 Tech (Waga NVDA: 6.2%)")]),
            "nvda": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVIDIA Corp", [("SMH", "VanEck Semiconductor ETF (Waga NVDA: 24.1%)"), ("QDVE.DE", "iShares S&P 500 Tech (Waga NVDA: 6.2%)")]),
            "apple": ("AAPL", "Apple Inc", "APC.DE", "Apple Inc", [("XLK", "Technology Select Sector (Waga AAPL: 22.3%)"), ("QDVE.DE", "iShares Tech Sector (Waga AAPL: 18.4%)")]),
            "aapl": ("AAPL", "Apple Inc", "APC.DE", "Apple Inc", [("XLK", "Technology Select Sector (Waga AAPL: 22.3%)"), ("QDVE.DE", "iShares Tech Sector (Waga AAPL: 18.4%)")]),
            "microsoft": ("MSFT", "Microsoft Corp", "MSF.DE", "Microsoft Corp", [("XLK", "Tech Select Sector (Waga MSFT: 21.1%)"), ("QDVE.DE", "iShares Tech Sector (Waga MSFT: 19.1%)")]),
            "msft": ("MSFT", "Microsoft Corp", "MSF.DE", "Microsoft Corp", [("XLK", "Tech Select Sector (Waga MSFT: 21.1%)"), ("QDVE.DE", "iShares Tech Sector (Waga MSFT: 19.1%)")]),
            "amazon": ("AMZN", "Amazon.com Inc", "AMZ.DE", "Amazon.com Inc", [("XLY", "Consumer Discretionary (Waga AMZN: 22.5%)")]),
            "amzn": ("AMZN", "Amazon.com Inc", "AMZ.DE", "Amazon.com Inc", [("XLY", "Consumer Discretionary (Waga AMZN: 22.5%)")]),
            "meta": ("META", "Meta Platforms", "FB2A.DE", "Meta Platforms", [("XLC", "Communication Services (Waga META: 22.8%)")]),
            "facebook": ("META", "Meta Platforms", "FB2A.DE", "Meta Platforms", [("XLC", "Communication Services (Waga META: 22.8%)")]),
            "google": ("GOOGL", "Alphabet Inc", "ABEA.DE", "Alphabet Inc", [("XLC", "Communication Services (Waga GOOGL: 12.2%)")]),
            "alphabet": ("GOOGL", "Alphabet Inc", "ABEA.DE", "Alphabet Inc", [("XLC", "Communication Services (Waga GOOGL: 12.2%)")]),
            "tesla": ("TSLA", "Tesla Inc", "TL0.DE", "Tesla Inc", [("XLY", "Consumer Discretionary (Waga TSLA: 14.2%)")]),
            "tsla": ("TSLA", "Tesla Inc", "TL0.DE", "Tesla Inc", [("XLY", "Consumer Discretionary (Waga TSLA: 14.2%)")]),
            "netflix": ("NFLX", "Netflix Inc", "NFC.DE", "Netflix Inc", [("XLC", "Communication Services (Waga NFLX: 5.1%)"), ("PBS", "Invesco Media ETF (Waga NFLX: 5.4%)")]),
            "nflx": ("NFLX", "Netflix Inc", "NFC.DE", "Netflix Inc", [("XLC", "Communication Services (Waga NFLX: 5.1%)")]),
            "cd projekt": ("CDR.WA", "CD Projekt SA", "2CD.DE", "CD Projekt SA", [("ETFW20L.WA", "Beta ETF WIG20TR (Waga CDR: 5.1%)")]),
            "cdr": ("CDR.WA", "CD Projekt SA", "2CD.DE", "CD Projekt SA", [("ETFW20L.WA", "Beta ETF WIG20TR (Waga CDR: 5.1%)")]),
            "orlen": ("PKN.WA", "ORLEN SA", "PKN.DE", "ORLEN SA", [("ETFW20L.WA", "Beta ETF WIG20TR (Waga PKN: 12.4%)")]),
            "dino": ("DNP.WA", "Dino Polska SA", "DNP.DE", "Dino Polska SA", [("ETFW20L.WA", "Beta ETF WIG20TR (Waga DNP: 4.9%)")])
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

st.set_page_config(page_title="XTB Helper Pro", layout="wide", page_icon="📊")

# 🎨 KOLORYSTYKA XTB (xStation 5)
st.markdown("""
    <style>
    .stApp { background-color: #131722; color: #d1d4dc; }
    .stApp [data-testid="stHeader"] { background-color: transparent; }
    
    /* Kafelki metryk w stylu XTB */
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 8px; border: 1px solid #2a2e39; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    div[data-testid="stMetricValue"] { color: #ffffff; font-weight: 600; }
    div[data-testid="stMetricDelta"] svg { fill: currentColor; }
    
    /* Zakładki i nawigacja */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #131722; }
    .stTabs [data-baseweb="tab"] { height: 45px; color: #787b86; background-color: #1e222d; border-radius: 4px 4px 0px 0px; padding: 10px 20px; border: 1px solid #2a2e39; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #2a2e39; color: #ffffff; font-weight: bold; border-top: 2px solid #2962ff; }
    
    /* Panele boczne i tabele */
    div[data-testid="stSidebar"] { background-color: #1e222d; border-right: 1px solid #2a2e39; }
    .stDataFrame { background-color: #1e222d; border-radius: 8px; }
    h1, h2, h3, h4 { color: #ffffff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    div[data-testid="stRadio"] > label { display: none; }
    </style>
    """, unsafe_allow_html=True)

# Stylizacja wykresów pod ciemne tło platform tradingowych
sns.set_theme(style="darkgrid", rc={
    "axes.facecolor": "#1e222d",
    "figure.facecolor": "#131722",
    "text.color": "#d1d4dc",
    "axes.labelcolor": "#787b86",
    "xtick.color": "#787b86",
    "ytick.color": "#787b86",
    "grid.color": "#2a2e39",
    "grid.linestyle": "-"
})

st.title("📊 Terminal Analityczny (XTB Helper)")
st.caption("Ocena ekspozycji | Analiza portfelowa | Horyzonty inwestycyjne XTB")

st.session_state.engine = FinancialEngine()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", format_xtb("SPY", "SPDR S&P 500 ETF Trust"), "ETF"),
        "QQQ": Asset("QQQ", format_xtb("QQQ", "Invesco QQQ Trust Nasdaq 100"), "ETF")
    }

with st.sidebar:
    st.header("🗂️ Zarządzanie Bazą")
    search_query = st.text_input("🔍 Wpisz spółkę docelową (np. tesla, cd projekt):").lower().strip()
    if search_query:
        matched_key = next((key for key in st.session_state.engine.market_map.keys() if key in search_query), None)
        if matched_key:
            t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
            
            st.session_state.portfolio[t_usa] = Asset(t_usa, format_xtb(t_usa, name_usa), "Akcja")
            st.session_state.portfolio[t_eu] = Asset(t_eu, format_xtb(t_eu, name_eu), "Akcja")
            for etf_ticker, etf_name in etfs:
                st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, format_xtb(etf_ticker, etf_name), "ETF")
                
            st.success(f"✅ Zmapowano instrument bazowy oraz fundusze oparte o {t_usa}.")

    st.divider()
    st.subheader("⏱️ Interwał Wykresu")
    interval_options = {
        "1 Dzień (Standard)": "1d",
        "1 Godzina (Max 730 dni)": "1h",
        "15 Minut (Max 60 dni)": "15m",
        "5 Minut (Max 60 dni)": "5m",
        "1 Minuta (Max 7 dni)": "1m"
    }
    selected_interval_label = st.selectbox("Rozdzielczość danych:", list(interval_options.keys()))
    selected_interval = interval_options[selected_interval_label]

ticker_options = list(st.session_state.portfolio.keys())
display_options = {t: st.session_state.portfolio[t].name for t in ticker_options}

st.markdown("<div style='margin-bottom: -15px; font-weight: bold; color: #787b86; font-size: 0.85rem; text-transform: uppercase;'>Horyzont czasowy analizy:</div>", unsafe_allow_html=True)

xtb_opts = {
    "1D": "1d", "1W": "5d", "1M": "1mo", "3M": "3mo", "6M": "6mo",
    "YTD": "ytd", "1Y": "1y", "3Y": "3y", "5Y": "5y", "MAX": "max"
}

selected_period_label = st.radio("Okres:", options=list(xtb_opts.keys()), horizontal=True)
selected_period = xtb_opts[selected_period_label]

st.divider()

tab1, tab2 = st.tabs(["📈 Panel Głównego Instrumentu", "⚖️ Porównywarka i Ekspozycja"])

with tab1:
    selected_ticker = st.selectbox("🎯 Wybierz instrument bazowy / ETF:", options=ticker_options, format_func=lambda x: display_options[x])
    
    if selected_ticker:
        asset = st.session_state.portfolio[selected_ticker]
        with st.spinner(f"Ładowanie danych rynkowych..."):
            data = st.session_state.engine.get_data(
                asset.ticker, period=selected_period, interval=selected_interval
            )
            
        if data.empty or len(data) < 2:
            st.error(f"⚠️ Zbyt mała płynność danych dla interwału '{selected_interval_label}' w tym oknie czasowym. Dostosuj parametry.")
        else:
            ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(data)
            total_return = data['Cumulative_Return'].iloc[-1] * 100
            
            c1, c2, c3, c4 = st.columns(4)
            # Delta w Streamlit automatycznie koloruje na zielono/czerwono
            c1.metric("Zwrot (Okres Analizy)", f"{total_return:.2f}%", delta=f"{total_return:.2f}%")
            c2.metric("Oczekiwany Roczny Zwrot", f"{ann_ret*100:.2f}%", delta=f"{ann_ret*100:.2f}%")
            c3.metric("Zmienność (Ryzyko)", f"{ann_vol*100:.2f}%", delta=f"Ochylenie", delta_color="off")
            
            # Kolorowanie Sharpe'a zależnie od progu
            sharpe_color = "normal" if sharpe > 0 else "inverse"
            c4.metric("Wskaźnik Sharpe'a", f"{sharpe:.2f}", delta="Risk/Reward", delta_color="off")
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 9))
            fig.patch.set_facecolor('#131722')
            
            # Główny wykres cenowy - niebieski XTB
            axes[0, 0].plot(data.index, data['Close'], color='#2962ff', linewidth=1.5)
            axes[0, 0].fill_between(data.index, data['Close'], data['Close'].min(), color='#2962ff', alpha=0.1)
            axes[0, 0].set_title(f"Kurs: {asset.name}", color='#ffffff', fontsize=11)
            
            sns.histplot(ax=axes[0, 1], data=data['Daily_Return'].dropna(), kde=True, color="#26a69a", bins=30)
            axes[0, 1].set_title("Rozkład odchyleń cenowych", color='#ffffff', fontsize=11)
            
            # Kolor skumulowanego zysku zależny od tego czy zarabiamy czy tracimy
            profit_color = '#26a69a' if total_return >= 0 else '#ef5350'
            axes[1, 0].plot(data.index, data['Cumulative_Return'] * 100, color=profit_color, linewidth=2)
            axes[1, 0].set_title("Skumulowana krzywa kapitału (%)", color='#ffffff', fontsize=11)
            
            sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'].dropna(), color="#b2b5be")
            axes[1, 1].set_title("Oceny skrajności (Boxplot)", color='#ffffff', fontsize=11)
            
            for ax in axes.flat:
                ax.set_facecolor('#1e222d')
                ax.tick_params(colors='#787b86', labelsize=9)
            
            plt.tight_layout()
            st.pyplot(fig)

with tab2:
    st.markdown("### ⚖️ Kalkulator Opłacalności Inwestycji")
    st.write("Skonfrontuj spółkę matkę z dedykowanymi funduszami ETF, aby zoptymalizować ryzyko.")
    
    selected_to_compare = st.multiselect(
        "Wybierz koszyk instrumentów:", 
        options=ticker_options, 
        format_func=lambda x: display_options[x],
        default=["SPY", "QQQ"] if "SPY" in ticker_options else []
    )
    
    if len(selected_to_compare) > 0:
        with st.spinner("Pobieranie strumienia kwotowań..."):
            fig_comp, ax_comp = plt.subplots(figsize=(14, 6))
            fig_comp.patch.set_facecolor('#131722')
            ax_comp.set_facecolor('#1e222d')
            
            comparison_rows = []
            # Paleta inspirowana tradingowymi neonami
            palette = ["#2962ff", "#26a69a", "#ff9800", "#ef5350", "#9c27b0"]
            
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
                        "Instrument (Ekspozycja)": asset_display_name,
                        "Zwrot (%)": round(total_return, 2),
                        "Zmienność / Ryzyko (%)": round(ann_vol * 100, 2),
                        "Sharpe Ratio": round(sharpe, 2)
                    })
            
            if comparison_rows:
                ax_comp.set_title(f"Dynamika zysku instrumentów bazowych | Okres: {selected_period_label}", fontsize=13, fontweight='bold', color='#ffffff')
                ax_comp.set_ylabel("Stopa zwrotu (%)", color='#787b86')
                ax_comp.tick_params(colors='#787b86')
                legend = ax_comp.legend(loc="upper left", facecolor='#1e222d', edgecolor='#2a2e39')
                plt.setp(legend.get_texts(), color='#d1d4dc', fontsize=9)
                st.pyplot(fig_comp)
                
                comp_df = pd.DataFrame(comparison_rows).set_index("Instrument (Ekspozycja)")
                st.markdown("#### 📊 Tabela Parametrów Portfelowych")
                st.dataframe(comp_df, use_container_width=True)
                
                st.markdown("#### 💡 Wnioski Analityczne Helpera")
                best_by_sharpe = max(comparison_rows, key=lambda x: x["Sharpe Ratio"])
                best_by_return = max(comparison_rows, key=lambda x: x["Zwrot (%)"])
                
                if best_by_sharpe["Instrument (Ekspozycja)"] == best_by_return["Instrument (Ekspozycja)"]:
                    st.success(f"🎯 **Sygnał Optymalny:** Instrument **{best_by_sharpe['Instrument (Ekspozycja)']}** bezapelacyjnie wygrywa w tym oknie czasowym. Osiągnął największy skok kapitału ({best_by_sharpe['Zwrot (%)']}%) przy jednoczesnym zachowaniu idealnej odporności na wstrząsy rynkowe (Sharpe: {best_by_sharpe['Sharpe Ratio']}).")
                else:
                    st.info(f"⚖️ **Dylemat Inwestora (Zysk vs Ryzyko):**\n\n"
                            f"* **Agresywny Kapitał:** Jeśli interesuje Cię czysty, maksymalny zysk, liderem w tym okresie był **{best_by_return['Instrument (Ekspozycja)']}** ({best_by_return['Zwrot (%)']}%).\n"
                            f"* **Defensywny Portfel:** Jeśli zależy Ci na stabilności i mniejszych spadkach podczas korekt, bezpieczniejszym wyborem jest **{best_by_sharpe['Instrument (Ekspozycja)']}**. Generuje on znacznie wyższą efektywność skorygowaną o ryzyko rynkowe (Sharpe: {best_by_sharpe['Sharpe Ratio']}).")
            else:
                st.error("Brak poprawnych danych rynkowych do przeliczenia koszyka.")
