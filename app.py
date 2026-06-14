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
        self.market_map = {
            "nvidia": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVIDIA Corp", [("SMH", "VanEck Semiconductor ETF"), ("QDVE.DE", "iShares S&P 500 Tech")]),
            "nvda": ("NVDA", "NVIDIA Corp", "NVD.DE", "NVIDIA Corp", [("SMH", "VanEck Semiconductor ETF"), ("QDVE.DE", "iShares S&P 500 Tech")]),
            "apple": ("AAPL", "Apple Inc", "APC.DE", "Apple Inc", [("XLK", "Technology Select Sector"), ("QDVE.DE", "iShares Tech Sector")]),
            "aapl": ("AAPL", "Apple Inc", "APC.DE", "Apple Inc", [("XLK", "Technology Select Sector"), ("QDVE.DE", "iShares Tech Sector")]),
            "microsoft": ("MSFT", "Microsoft Corp", "MSF.DE", "Microsoft Corp", [("XLK", "Tech Select Sector"), ("QDVE.DE", "iShares Tech Sector")]),
            "msft": ("MSFT", "Microsoft Corp", "MSF.DE", "Microsoft Corp", [("XLK", "Tech Select Sector"), ("QDVE.DE", "iShares Tech Sector")]),
            "amazon": ("AMZN", "Amazon.com Inc", "AMZ.DE", "Amazon.com Inc", [("XLY", "Consumer Discretionary")]),
            "amzn": ("AMZN", "Amazon.com Inc", "AMZ.DE", "Amazon.com Inc", [("XLY", "Consumer Discretionary")]),
            "meta": ("META", "Meta Platforms", "FB2A.DE", "Meta Platforms", [("XLC", "Communication Services")]),
            "facebook": ("META", "Meta Platforms", "FB2A.DE", "Meta Platforms", [("XLC", "Communication Services")]),
            "google": ("GOOGL", "Alphabet Inc", "ABEA.DE", "Alphabet Inc", [("XLC", "Communication Services")]),
            "alphabet": ("GOOGL", "Alphabet Inc", "ABEA.DE", "Alphabet Inc", [("XLC", "Communication Services")]),
            "tesla": ("TSLA", "Tesla Inc", "TL0.DE", "Tesla Inc", [("XLY", "Consumer Discretionary")]),
            "tsla": ("TSLA", "Tesla Inc", "TL0.DE", "Tesla Inc", [("XLY", "Consumer Discretionary")]),
            "netflix": ("NFLX", "Netflix Inc", "NFC.DE", "Netflix Inc", [("XLC", "Communication Services"), ("PBS", "Invesco Media ETF")]),
            "nflx": ("NFLX", "Netflix Inc", "NFC.DE", "Netflix Inc", [("XLC", "Communication Services")]),
            "cd projekt": ("CDR.WA", "CD Projekt SA", "2CD.DE", "CD Projekt SA", [("ETFW20L.WA", "Beta ETF WIG20TR")]),
            "cdr": ("CDR.WA", "CD Projekt SA", "2CD.DE", "CD Projekt SA", [("ETFW20L.WA", "Beta ETF WIG20TR")]),
            "orlen": ("PKN.WA", "ORLEN SA", "PKN.DE", "ORLEN SA", [("ETFW20L.WA", "Beta ETF WIG20TR")]),
            "dino": ("DNP.WA", "Dino Polska SA", "DNP.DE", "Dino Polska SA", [("ETFW20L.WA", "Beta ETF WIG20TR")])
        }

        self.ai_profiles = {
            "NVDA": "Lider na rynku procesorów graficznych (GPU) i układów sztucznej inteligencji.",
            "NVD.DE": "Europejski odpowiednik notowań NVIDIA Corp., wyceniany w walucie Euro na giełdzie Xetra.",
            "AAPL": "Globalny gigant technologiczny produkujący elektronikę użytkową (iPhone, Mac).",
            "APC.DE": "Europejski odpowiednik notowań Apple Inc., wyceniany w walucie Euro na giełdzie Xetra.",
            "MSFT": "Dominuje w sektorze oprogramowania, chmury obliczeniowej (Azure) oraz integracji AI z biznesem.",
            "AMZN": "Lider branży e-commerce oraz największy na świecie dostawca usług w chmurze (AWS).",
            "META": "Właściciel platform Facebook, Instagram, WhatsApp. Lider rynku reklamy cyfrowej.",
            "GOOGL": "Dominator rynku wyszukiwarek internetowych i cyfrowej reklamy oraz innowator AI.",
            "TSLA": "Pionier rynku samochodów elektrycznych (EV) oraz technologii autonomicznego prowadzenia.",
            "NFLX": "Największa na świecie platforma streamingowa. Rewolucjonizuje dystrybucję wideo.",
            "CDR.WA": "Największe polskie studio produkujące gry wideo (Wiedźmin, Cyberpunk 2077).",
            "PKN.WA": "Największy polski koncern multienergetyczny, posiadający rafinerie w regionie CEE.",
            "DNP.WA": "Polska sieć supermarketów, najszybciej rozwijająca się firma handlu detalicznego na rodzimym rynku.",
            "SPY": "Najpopularniejszy fundusz ETF śledzący indeks S&P 500.",
            "QQQ": "Fundusz ETF oparty na indeksie Nasdaq-100. Skupia się na Big Tech.",
            "SMH": "VanEck Semiconductor ETF. Inwestuje w układ scalone.",
            "QDVE.DE": "iShares S&P 500 Information Technology. Zdywersyfikowane amerykańskie technologie.",
            "XLK": "Technology Select Sector SPDR Fund.",
            "XLY": "Consumer Discretionary Select Sector SPDR Fund.",
            "XLC": "Communication Services Select Sector SPDR Fund.",
            "PBS": "Invesco Dynamic Media ETF.",
            "ETFW20L.WA": "Beta ETF WIG20TR. Polski fundusz śledzący indeks 20 największych spółek GPW."
        }

    def get_data(self, ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
        if not ticker:
            return pd.DataFrame()
        try:
            ticker_data = yf.Ticker(ticker)
            # Pobieramy również dywidendy
            hist = ticker_data.history(period=period, interval=interval)
            
            if hist.empty:
                return pd.DataFrame()
                
            # Wyciągamy Zamknięcie i Dywidendy
            df = pd.DataFrame(hist[['Close', 'Dividends']])
            df = df.dropna(subset=['Close'])
            
            df.index = pd.to_datetime(df.index, utc=True)
            df = df[~df.index.duplicated(keep='last')]
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
        
        total_dividends = df['Dividends'].sum() if 'Dividends' in df.columns else 0
        
        return annual_return, annual_volatility, sharpe, total_dividends

    def generate_ai_report(self, ticker: str, df: pd.DataFrame, sharpe: float, total_return: float) -> str:
        description = self.ai_profiles.get(ticker.upper(), "Instrument finansowy notowany na globalnych rynkach.")
        
        momentum = "neutralne"
        if len(df) > 5:
            last_price = df['Close'].iloc[-1]
            old_price = df['Close'].iloc[-5]
            short_trend = ((last_price - old_price) / old_price) * 100
            if short_trend > 2:
                momentum = f"silne wzrostowe (+{short_trend:.1f}%)"
            elif short_trend < -2:
                momentum = f"spadkowe (korekta {short_trend:.1f}%)"
            else:
                momentum = f"konsolidacyjne"

        verdict = ""
        if sharpe >= 1.0 and total_return > 0:
            verdict = "🟢 <b>Ocena AI:</b> BARDZO WYSOKA ZDOLNOŚĆ. Rewelacyjny stosunek zysku do ryzyka."
        elif sharpe > 0 and total_return > 0:
            verdict = "🟡 <b>Ocena AI:</b> UMIARKOWANA ZDOLNOŚĆ. Stabilne zyski przy standardowym ryzyku."
        else:
            verdict = "🔴 <b>Ocena AI:</b> NISKA ZDOLNOŚĆ. Zmienność/straty przewyższają bezpieczną stopę zwrotu."

        return f"<b>Profil:</b> {description}<br><br><b>Ostatnie akcje (Momentum):</b> Trend <b>{momentum}</b>.<br><br>{verdict}"

st.set_page_config(page_title="XTB Helper Pro Max", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .stApp { background-color: #131722; color: #d1d4dc; }
    .stApp [data-testid="stHeader"] { background-color: transparent; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 8px; border: 1px solid #2a2e39; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    div[data-testid="stMetricValue"] { color: #ffffff; font-weight: 600; }
    div[data-testid="stMetricDelta"] svg { fill: currentColor; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #131722; }
    .stTabs [data-baseweb="tab"] { height: 45px; color: #787b86; background-color: #1e222d; border-radius: 4px 4px 0px 0px; padding: 10px 20px; border: 1px solid #2a2e39; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #2a2e39; color: #ffffff; font-weight: bold; border-top: 2px solid #2962ff; }
    div[data-testid="stSidebar"] { background-color: #1e222d; border-right: 1px solid #2a2e39; }
    .stDataFrame { background-color: #1e222d; border-radius: 8px; }
    h1, h2, h3, h4 { color: #ffffff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    div[data-testid="stRadio"] > label { display: none; }
    
    .ai-box { background-color: #1a233a; border-left: 5px solid #2962ff; padding: 15px 20px; border-radius: 4px; margin-top: 20px; margin-bottom: 20px;}
    .ai-header { color: #3b82f6; font-weight: 600; font-size: 1.1rem; margin-bottom: 10px; display: flex; align-items: center; gap: 10px;}
    .xtb-period-label { font-weight: bold; color: #787b86; font-size: 0.85rem; text-transform: uppercase; margin-bottom: -35px; z-index: 10; position: relative; }
    </style>
    """, unsafe_allow_html=True)

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
st.caption("Ocena ekspozycji | Raport AI | Analiza Wskaźnikowa | Symulacja DCA")

st.session_state.engine = FinancialEngine()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "SPY": Asset("SPY", format_xtb("SPY", "SPDR S&P 500 ETF Trust"), "ETF"),
        "QQQ": Asset("QQQ", format_xtb("QQQ", "Invesco QQQ Trust Nasdaq 100"), "ETF")
    }

with st.sidebar:
    st.header("🗂️ Zarządzanie Bazą")
    search_query = st.text_input("🔍 Wpisz spółkę (np. tesla, orlen):").lower().strip()
    if search_query:
        matched_key = next((key for key in st.session_state.engine.market_map.keys() if key in search_query), None)
        if matched_key:
            t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
            st.session_state.portfolio[t_usa] = Asset(t_usa, format_xtb(t_usa, name_usa), "Akcja")
            st.session_state.portfolio[t_eu] = Asset(t_eu, format_xtb(t_eu, name_eu), "Akcja")
            for etf_ticker, etf_name in etfs:
                st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, format_xtb(etf_ticker, etf_name), "ETF")
            st.success(f"✅ Zmapowano rynki dla {t_usa}.")

    st.divider()
    st.subheader("⏱️ Interwał Wykresu")
    interval_options = {"1 Dzień (Standard)": "1d", "1 Godzina (Max 730 dni)": "1h", "15 Minut (Max 60 dni)": "15m", "5 Minut (Max 60 dni)": "5m"}
    selected_interval = interval_options[st.selectbox("Rozdzielczość:", list(interval_options.keys()))]

ticker_options = list(st.session_state.portfolio.keys())
display_options = {t: st.session_state.portfolio[t].name for t in ticker_options}

xtb_opts = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "YTD": "ytd", "1Y": "1y", "3Y": "3y", "5Y": "5y", "MAX": "max"}

tab1, tab2, tab3 = st.tabs(["🏠 Strona Główna", "📈 Analiza i DCA", "⚖️ Porównywarka i Korelacja"])

with tab1:
    st.markdown("""
    ## 📖 XTB Helper Pro Max (Terminal Analityczny)
    
    Aplikacja stanowi profesjonalne narzędzie wspomagające decyzje giełdowe, zbudowane na architekturze OOP.
    
    ### 🎯 Funkcjonalności Premium (Skala 5.0)
    1. **System Hybrydowego Mapowania:** Odejście od ręcznego wpisywania tickerów. Inteligentne łączenie rynków (USA/EU) i ETF-ów.
    2. **Algorytm GenAI (Momentum):** Moduł AI automatycznie analizujący rentowność (Sharpe Ratio) i wydający rekomendacje.
    3. **Nietrywialna Transformacja Osi Czasu:** Wdrożenie filtra Anty-Gap ujednolicającego sekwencję czasu na wykresach intraday.
    4. **Zaawansowana Analiza Techniczna & Fundamentalna:** Implementacja średnich kroczących (SMA 50/200) oraz ekstrakcja dywidend.
    5. **Symulator Inwestycyjny DCA:** Wyliczanie stopy zwrotu dla regularnych, comiesięcznych dopłat do portfela (Dollar Cost Averaging).
    6. **Heatmapa Korelacji (Dywersyfikacja):** Matematyczne obliczanie współczynnika korelacji w koszyku w celu bezpiecznej dywersyfikacji.
    """)

with tab2:
    st.markdown("<div class='xtb-period-label'>HORYZONT CZASOWY:</div>", unsafe_allow_html=True)
    selected_period_t2 = xtb_opts[st.radio("Okres T2:", options=list(xtb_opts.keys()), horizontal=True, label_visibility="collapsed", key="rt2")]
    
    col_sel, col_tech = st.columns([3, 1])
    with col_sel:
        selected_ticker = st.selectbox("🎯 Wybierz instrument:", options=ticker_options, format_func=lambda x: display_options[x])
    with col_tech:
        # NOWOŚĆ 1: Przełącznik Analizy Technicznej
        st.write("")
        st.write("")
        show_sma = st.toggle("Włącz wskaźniki SMA (50/200)")

    if selected_ticker:
        asset = st.session_state.portfolio[selected_ticker]
        with st.spinner(f"Analiza wolumenu..."):
            data = st.session_state.engine.get_data(asset.ticker, period=selected_period_t2, interval=selected_interval)
            
        if data.empty or len(data) < 2:
            st.error(f"⚠️ Zbyt mała płynność danych dla wybranych parametrów.")
        else:
            ann_ret, ann_vol, sharpe, total_divs = st.session_state.engine.calculate_metrics(data)
            total_return = data['Cumulative_Return'].iloc[-1] * 100
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Zwrot (Okres)", f"{total_return:.2f}%", delta=f"{total_return:.2f}%")
            c2.metric("Oczekiwany Roczny", f"{ann_ret*100:.2f}%", delta=f"{ann_ret*100:.2f}%")
            c3.metric("Zmienność", f"{ann_vol*100:.2f}%", delta=f"Ryzyko", delta_color="off")
            c4.metric("Sharpe Ratio", f"{sharpe:.2f}", delta="Reward/Risk", delta_color="off")
            # NOWOŚĆ 2: Wskaźnik Dywidendy
            c5.metric("Wypłacone Dywidendy", f"{total_divs:.2f}", delta="Pasywny Dochód", delta_color="normal" if total_divs > 0 else "off")
            
            ai_text = st.session_state.engine.generate_ai_report(asset.ticker, data, sharpe, total_return)
            st.markdown(f"""
<div class="ai-box">
    <div class="ai-header">🤖 AI Analiza Fundamentalna i Momentum</div>
    <div style="color: #d1d4dc; font-size: 0.95rem; line-height: 1.6;">{ai_text}</div>
</div>
""", unsafe_allow_html=True)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 9))
            fig.patch.set_facecolor('#131722')
            
            x_seq = np.arange(len(data))
            step = max(1, len(data) // 6)
            tick_positions = x_seq[::step]
            tick_labels = [data.index[i].strftime('%Y-%m-%d') for i in tick_positions]
            
            axes[0, 0].plot(x_seq, data['Close'], color='#2962ff', linewidth=1.5, label='Cena Rynkowa')
            axes[0, 0].fill_between(x_seq, data['Close'], data['Close'].min(), color='#2962ff', alpha=0.1)
            
            # Dodanie Wskaźników Technicznych (SMA)
            if show_sma and len(data) > 50:
                sma50 = data['Close'].rolling(window=50).mean()
                axes[0, 0].plot(x_seq, sma50, color='#ff9800', linewidth=1.5, linestyle='--', label='SMA 50')
                if len(data) > 200:
                    sma200 = data['Close'].rolling(window=200).mean()
                    axes[0, 0].plot(x_seq, sma200, color='#e91e63', linewidth=1.5, linestyle='--', label='SMA 200')
                axes[0, 0].legend(facecolor='#1e222d', edgecolor='#2a2e39', labelcolor='#ffffff')
                
            axes[0, 0].set_title(f"Kurs: {asset.name}", color='#ffffff', fontsize=11)
            axes[0, 0].set_xticks(tick_positions)
            axes[0, 0].set_xticklabels(tick_labels, rotation=15)
            
            sns.histplot(ax=axes[0, 1], data=data['Daily_Return'].dropna(), kde=True, color="#26a69a", bins=30)
            axes[0, 1].set_title("Rozkład odchyleń cenowych", color='#ffffff', fontsize=11)
            
            profit_color = '#26a69a' if total_return >= 0 else '#ef5350'
            axes[1, 0].plot(x_seq, data['Cumulative_Return'] * 100, color=profit_color, linewidth=2)
            axes[1, 0].set_title("Skumulowana krzywa kapitału (%)", color='#ffffff', fontsize=11)
            axes[1, 0].set_xticks(tick_positions)
            axes[1, 0].set_xticklabels(tick_labels, rotation=15)
            
            sns.boxplot(ax=axes[1, 1], x=data['Daily_Return'].dropna(), color="#b2b5be")
            axes[1, 1].set_title("Oceny skrajności (Boxplot)", color='#ffffff', fontsize=11)
            
            for ax in axes.flat:
                ax.set_facecolor('#1e222d')
                ax.tick_params(colors='#787b86', labelsize=9)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # NOWOŚĆ 3: Export CSV
            csv = data.to_csv().encode('utf-8')
            st.download_button(label="📥 Pobierz dane do pliku CSV", data=csv, file_name=f'{asset.ticker}_data.csv', mime='text/csv')

            # NOWOŚĆ 4: Symulator Inwestycyjny DCA (Dollar Cost Averaging)
            st.markdown("---")
            with st.expander("💸 SYMULATOR INWESTYCYJNY (Dollar Cost Averaging)"):
                st.write("Sprawdź, ile byś zarobił, inwestując w to aktywo stałą kwotę co miesiąc w wybranym okresie.")
                monthly_inv = st.number_input("Miesięczna kwota inwestycji (Waluta natywna):", min_value=50, value=500, step=50)
                
                # Algorytm DCA (pobieramy pierwszy dzień z każdego miesiąca w danych)
                monthly_data = data.resample('ME').first().dropna(subset=['Close'])
                if len(monthly_data) > 1:
                    total_invested = len(monthly_data) * monthly_inv
                    shares_accumulated = (monthly_inv / monthly_data['Close']).cumsum()
                    final_portfolio_value = shares_accumulated.iloc[-1] * data['Close'].iloc[-1]
                    dca_profit_pct = ((final_portfolio_value - total_invested) / total_invested) * 100
                    
                    dc1, dc2, dc3 = st.columns(3)
                    dc1.metric("Suma wpłaconego kapitału", f"{total_invested:.2f}")
                    dc2.metric("Wartość końcowa portfela", f"{final_portfolio_value:.2f}")
                    dc3.metric("Zysk z inwestycji DCA (%)", f"{dca_profit_pct:.2f}%", delta=f"{dca_profit_pct:.2f}%")
                else:
                    st.warning("Zbyt krótki okres analizy, aby zasymulować inwestycje comiesięczne. Wybierz okres min. 3M.")

with tab3:
    st.markdown("<div class='xtb-period-label'>HORYZONT CZASOWY PORÓWNANIA:</div>", unsafe_allow_html=True)
    selected_period_t3 = xtb_opts[st.radio("Okres T3:", options=list(xtb_opts.keys()), horizontal=True, label_visibility="collapsed", key="rt3")]
    
    st.divider()
    selected_to_compare = st.multiselect(
        "Wybierz koszyk instrumentów (Min. 2):", 
        options=ticker_options, 
        format_func=lambda x: display_options[x],
        default=["SPY", "QQQ"] if "SPY" in ticker_options else []
    )
    
    if len(selected_to_compare) >= 2:
        with st.spinner("Przeliczanie koszyka i korelacji..."):
            comparison_rows = []
            returns_dict = {}
            palette = ["#2962ff", "#26a69a", "#ff9800", "#ef5350", "#9c27b0", "#00bcd4", "#cddc39"]
            
            fig_comp, ax_comp = plt.subplots(figsize=(14, 6))
            fig_comp.patch.set_facecolor('#131722')
            ax_comp.set_facecolor('#1e222d')
            
            longest_index = None
            
            for idx, t in enumerate(selected_to_compare):
                df = st.session_state.engine.get_data(t, period=selected_period_t3, interval=selected_interval)
                if not df.empty and len(df) >= 2:
                    ann_ret, ann_vol, sharpe, _ = st.session_state.engine.calculate_metrics(df)
                    total_return = df['Cumulative_Return'].iloc[-1] * 100
                    
                    returns_dict[st.session_state.portfolio[t].name] = df['Daily_Return']
                    
                    if longest_index is None or len(df) > len(longest_index):
                        longest_index = df.index
                    
                    x_seq = np.arange(len(df))
                    color = palette[idx % len(palette)]
                    asset_display_name = st.session_state.portfolio[t].name
                    ax_comp.plot(x_seq, df['Cumulative_Return'] * 100, label=asset_display_name, linewidth=2, color=color)
                    
                    comparison_rows.append({
                        "Instrument (Ekspozycja)": asset_display_name,
                        "Zwrot (%)": round(total_return, 2),
                        "Zmienność / Ryzyko (%)": round(ann_vol * 100, 2),
                        "Sharpe Ratio": round(sharpe, 2)
                    })
            
            if comparison_rows and longest_index is not None:
                step = max(1, len(longest_index) // 8)
                tick_positions = np.arange(len(longest_index))[::step]
                tick_labels = [longest_index[i].strftime('%Y-%m-%d') for i in tick_positions]
                
                ax_comp.set_xticks(tick_positions)
                ax_comp.set_xticklabels(tick_labels, rotation=15)
                
                best_by_sharpe = max(comparison_rows, key=lambda x: x["Sharpe Ratio"])
                best_by_return = max(comparison_rows, key=lambda x: x["Zwrot (%)"])
                
                ai_compare_text = ""
                if best_by_sharpe["Instrument (Ekspozycja)"] == best_by_return["Instrument (Ekspozycja)"]:
                    ai_compare_text = f"🟢 <b>Sygnał Optymalny:</b> Instrument <b>{best_by_sharpe['Instrument (Ekspozycja)']}</b> bezapelacyjnie wygrywa. Osiągnął największy skok kapitału (+{best_by_sharpe['Zwrot (%)']}%) przy świetnej odporności na wstrząsy (Sharpe: {best_by_sharpe['Sharpe Ratio']})."
                else:
                    ai_compare_text = f"🟡 <b>Dylemat Inwestora:</b><br>👉 <b>Największy Zysk:</b> <b>{best_by_return['Instrument (Ekspozycja)']}</b> (+{best_by_return['Zwrot (%)']}%).<br>👉 <b>Najbezpieczniejszy Profil (Zysk/Ryzyko):</b> <b>{best_by_sharpe['Instrument (Ekspozycja)']}</b> (Sharpe: {best_by_sharpe['Sharpe Ratio']})."

                st.markdown(f"""
<div class="ai-box">
    <div class="ai-header">🤖 AI Analiza Porównawcza Koszyka</div>
    <div style="color: #d1d4dc; font-size: 0.95rem; line-height: 1.6;">{ai_compare_text}</div>
</div>
""", unsafe_allow_html=True)

                ax_comp.set_title(f"Dynamika zysku koszyka | Okres: {selected_period_t2}", fontsize=13, fontweight='bold', color='#ffffff')
                ax_comp.set_ylabel("Stopa zwrotu (%)", color='#787b86')
                ax_comp.tick_params(colors='#787b86', labelsize=9)
                legend = ax_comp.legend(loc="upper left", facecolor='#1e222d', edgecolor='#2a2e39')
                plt.setp(legend.get_texts(), color='#d1d4dc', fontsize=9)
                st.pyplot(fig_comp)
                
                st.markdown("#### 📊 Tabela Parametrów Portfelowych")
                st.dataframe(pd.DataFrame(comparison_rows).set_index("Instrument (Ekspozycja)"), use_container_width=True)

                # NOWOŚĆ 5: Heatmapa Korelacji (Wymaga wyrównania danych)
                st.markdown("---")
                st.markdown("#### 🔥 Heatmapa Korelacji Koszyka (Dywersyfikacja)")
                st.write("Współczynnik 1.0 oznacza, że aktywa poruszają się identycznie. Niższy współczynnik (lub ujemny) oznacza lepszą dywersyfikację portfela i mniejsze ryzyko.")
                
                returns_df = pd.DataFrame(returns_dict).dropna()
                if not returns_df.empty:
                    corr_matrix = returns_df.corr()
                    fig_corr, ax_corr = plt.subplots(figsize=(10, 6))
                    fig_corr.patch.set_facecolor('#131722')
                    ax_corr.set_facecolor('#1e222d')
                    
                    # Rysowanie heatmapy w ciemnych kolorach (vlag - niebieski/czerwony)
                    sns.heatmap(corr_matrix, annot=True, cmap="vlag", ax=ax_corr, cbar=False, 
                                annot_kws={"color": "white", "weight": "bold"}, 
                                linewidths=.5, linecolor='#131722')
                    
                    ax_corr.tick_params(colors='#d1d4dc', labelsize=9)
                    st.pyplot(fig_corr)
                else:
                    st.warning("Brak wystarczających danych do wyliczenia korelacji w tym okresie.")
            else:
                st.error("Brak poprawnych danych rynkowych.")
    else:
        st.info("👆 Wybierz co najmniej 2 instrumenty z listy, aby wygenerować analizę korelacji i porównania.")
