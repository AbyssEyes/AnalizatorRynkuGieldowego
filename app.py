import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, time, timedelta

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

    # Zaktualizowana metoda przyjmująca precyzyjny interwał
    def get_data(self, ticker: str, period: str = None, start: datetime = None, end: datetime = None, interval: str = "1d") -> pd.DataFrame:
        if not ticker:
            return pd.DataFrame()
        try:
            ticker_data = yf.Ticker(ticker)
            if start and end:
                hist = ticker_data.history(start=start, end=end, interval=interval)
            else:
                hist = ticker_data.history(period=period if period else "1y", interval=interval)
                
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
        
        # Dostosowanie do interwałów minutowych (ok. 252 dni * 390 minut sesyjnych = 98280 okresów w roku)
        annual_return = avg_daily * 252
        annual_volatility = volatility * np.sqrt(252)
        sharpe = (annual_return - 0.02) / annual_volatility if annual_volatility > 0 else 0
        
        return annual_return, annual_volatility, sharpe

st.set_page_config(page_title="Globalny Analizator ETF v11", layout="wide", page_icon="📈")

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
st.caption("Zaawansowane mapowanie rynkowe | Analiza portfelowa | Precyzja do 1 minuty")

if 'engine' not in st.session_state:
    st.session_state.engine = FinancialEngine()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", "SPY - SPDR S&P 500 ETF Trust (Rynek USA)", "ETF"),
        "QQQ": Asset("QQQ", "QQQ - Invesco QQQ Trust Nasdaq 100 (Rynek USA)", "ETF")
    }

with st.sidebar:
    st.header("🗂️ Zarządzanie Bazą")
    search_query = st.text_input("🔍 Wpisz firmę (np. tesla, microsoft):").lower().strip()
    if search_query:
        matched_key = next((key for key in st.session_state.engine.market_map.keys() if key in search_query), None)
        if matched_key:
            t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
            st.session_state.portfolio[t_usa] = Asset(t_usa, f"{t_usa} - {name_usa} (USA)", "Akcja")
            st.session_state.portfolio[t_eu] = Asset(t_eu, f"{t_eu} - {name_usa} (Europa)", "Akcja")
            for etf_ticker, weight in etfs:
                st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, f"{etf_ticker} - ETF (Udział: {weight})", "ETF")
            st.success(f"✅ Dodano powiązania dla: {name_usa}")

    st.divider()
    # Nowy panel do wyboru dokładności wykresu
    st.subheader("⏱️ Interwał Wykresu")
    st.markdown("<span style='font-size:0.8em; color:#94a3b8;'>Uwaga: 1 minuta działa tylko dla zakresu ostatnich 7 dni.</span>", unsafe_allow_html=True)
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

st.markdown("<h4 style='color: #3b82f6;'>⏳ Wybierz tryb zakresu analitycznego</h4>", unsafe_allow_html=True)
time_mode = st.radio(
    "Metoda wprowadzania:", 
    ["📅 Standardowe z rynku (styl XTB)", "🎚️ Szybki suwak", "⏱️ Własny (dokładny co do sekundy)"], 
    horizontal=True, 
    label_visibility="collapsed"
)

selected_period = None
start_date = None
end_date = None

if time_mode == "📅 Standardowe z rynku (styl XTB)":
    xtb_opts = {
        "1D (Dzisiaj)": "1d", "1W (Ostatni tydzień)": "5d", "1M (Ostatni miesiąc)": "1mo",
        "3M (Kwartał)": "3mo", "6M (Półrocze)": "6mo", "YTD (Od początku roku)": "ytd",
        "1Y (Ostatni rok)": "1y", "MAX (Pełna historia)": "max"
    }
    chosen_xtb = st.selectbox("Wybierz predefiniowany okres:", list(xtb_opts.keys()))
    selected_period = xtb_opts[chosen_xtb]

elif time_mode == "🎚️ Szybki suwak":
    selected_period = st.select_slider(
        "Szerokość okna czasowego:", 
        options=["1mo", "3mo", "6mo", "1y", "3y", "5y", "max"], 
        value="1y"
    )

else:
    col_s, col_e = st.columns(2)
    with col_s:
        d_start = st.date_input("Od: Data początkowa", value=datetime.today() - timedelta(days=5))
        t_start = st.time_input("Od: Czas (godz:min:sek)", value=time(9, 0, 0), step=1)
    with col_e:
        d_end = st.date_input("Do: Data końcowa", value=datetime.today())
        t_end = st.time_input("Do: Czas (godz:min:sek)", value=time(17, 30, 0), step=1)
    
    start_date = datetime.combine(d_start, t_start)
    end_date = datetime.combine(d_end, t_end)

st.divider()

tab1, tab2 = st.tabs(["📊 Analiza Szczegółowa Aktywa", "⚖️ Porównywarka ETF / Akcji"])

with tab1:
    selected_ticker = st.selectbox("🎯 Wybierz instrument do analizy:", options=ticker_options, format_func=lambda x: display_options[x])
    
    if selected_ticker:
        asset = st.session_state.portfolio[selected_ticker]
        with st.spinner(f"Pobieranie interwału {selected_interval}..."):
            data = st.session_state.engine.get_data(
                asset.ticker, period=selected_period, start=start_date, end=end_date, interval=selected_interval
            )
            
        if data.empty or len(data) < 2:
            st.error(f"⚠️ Konflikt limitów API Yahoo Finance. Prawdopodobnie żądasz zbyt precyzyjnych danych (np. 1 minuta) dla zbyt długiego okresu (ponad 7 dni w tył) lub rynki były zamknięte w podanym czasie. Zmień interwał w panelu bocznym na '1 Dzień' lub zmniejsz zakres czasu.")
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
            axes[0, 0].set_title(f"Kurs Historyczny: {asset.ticker} (Interwał: {selected_interval})", color='#f8fafc')
            
            sns.histplot(ax=axes[0, 1], data=data['Daily_Return'].dropna(), kde=True, color="#8b5cf6", bins=30)
            axes[0, 1].set_title("Rozkład wahań w wybranym interwale", color='#f8fafc')
            
            axes[1, 0].plot(data.index, data['Cumulative_Return'] * 100, color='#10b981', linewidth=2)
            axes[1, 0].set_title("Skumulowany zysk (%)", color='#f8fafc')
            
            sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'].dropna(), color="#f59e0b")
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
                df = st.session_state.engine.get_data(
                    t, period=selected_period, start=start_date, end=end_date, interval=selected_interval
                )
                if not df.empty and len(df) >= 2:
                    ann_ret, ann_vol, sharpe = st.session_state.engine.calculate_metrics(df)
                    total_return = df['Cumulative_Return'].iloc[-1] * 100
                    
                    color = palette[idx % len(palette)]
                    ax_comp.plot(df.index, df['Cumulative_Return'] * 100, label=f"{t}", linewidth=2, color=color)
                    
                    comparison_rows.append({
                        "Ticker": t,
                        "Zysk (%)": round(total_return, 2),
                        "Punkty pomiarowe": len(df),
                        "Zmienność (%)": round(ann_vol * 100, 2)
                    })
                elif len(df) < 2:
                    st.warning(f"⚠️ Zignorowano '{t}'. Powód: limit dla interwału {selected_interval} przekroczony.")
            
            if comparison_rows:
                info_text = f"Interwał: {selected_interval}"
                ax_comp.set_title(f"Porównanie skumulowanego zysku (%) | {info_text}", fontsize=12, fontweight='bold', color='#f8fafc')
                ax_comp.set_ylabel("Zysk (%)", color='#94a3b8')
                ax_comp.set_xlabel("Czas", color='#94a3b8')
                ax_comp.tick_params(colors='#94a3b8')
                legend = ax_comp.legend(loc="upper left", facecolor='#111827', edgecolor='#1f2937')
                plt.setp(legend.get_texts(), color='#f8fafc')
                st.pyplot(fig_comp)
                
                comp_df = pd.DataFrame(comparison_rows).set_index("Ticker")
                st.markdown("#### 📊 Porównawcze zestawienie liczbowe")
                st.dataframe(comp_df, use_container_width=True)
            else:
                st.error("Brak danych do wyświetlenia na osi czasu z powodu restrykcji nałożonych na wybrany interwał giełdowy.")
