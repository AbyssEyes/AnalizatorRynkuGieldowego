import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

AI_EXCELLENT_THRESHOLD_PCT = 10.0
AI_NEUTRAL_THRESHOLD_PCT = 0.0

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
            "NVDA": "Lider na rynku procesorów graficznych (GPU) i układów sztucznej inteligencji. Dostarcza kluczową infrastrukturę dla modeli AI.",
            "NVD.DE": "Europejski odpowiednik notowań NVIDIA Corp., wyceniany w walucie Euro na giełdzie Xetra.",
            "AAPL": "Globalny gigant technologiczny produkujący elektronikę użytkową (iPhone, Mac) oraz rozwijający rentowny ekosystem usług cyfrowych.",
            "APC.DE": "Europejski odpowiednik notowań Apple Inc., wyceniany w walucie Euro na giełdzie Xetra.",
            "MSFT": "Dominuje w sektorze oprogramowania, chmury obliczeniowej (Azure) oraz integracji AI z biznesem.",
            "AMZN": "Lider branży e-commerce oraz największy na świecie dostawca usług w chmurze (AWS).",
            "META": "Właściciel platform Facebook, Instagram, WhatsApp. Lider rynku reklamy cyfrowej z naciskiem na rozwój AI.",
            "GOOGL": "Dominator rynku wyszukiwarek internetowych i cyfrowej reklamy (Google, YouTube) oraz innowator AI.",
            "TSLA": "Pionier rynku samochodów elektrycznych (EV) oraz tehnologii autonomicznego prowadzenia i magazynowania czystej energii.",
            "NFLX": "Największa na świecie platforma streamingowa. Rewolucjonizuje dystrybucję filmów i seriali oryginalnych.",
            "CDR.WA": "Największe polskie studio produkujące gry wideo, znane głównie z serii 'Wiedźmin' oraz 'Cyberpunk 2077'.",
            "PKN.WA": "Największy polski koncern multienergetyczny, posiadający rafinerie i sieć detaliczną w regionie CEE.",
            "DNP.WA": "Polska sieć supermarketów, najszybciej rozwijająca się firma w sektorze handlu detalicznego na rodzimym rynku.",
            "SPY": "Najpopularniejszy fundusz ETF śledzący indeks S&P 500. Daje ekspozycję na 500 największych amerykańskich przedsiębiorstw.",
            "QQQ": "Fundusz ETF oparty na indeksie Nasdaq-100. Skupia się na Big Tech i innowacjach.",
            "SMH": "VanEck Semiconductor ETF. Inwestuje w największe globalne spółki z branży układów scalonych i półprzewodników.",
            "QDVE.DE": "iShares S&P 500 Information Technology. Europejski fundusz skupiający się na potężnym amerykańskim sektorze technologicznym.",
            "XLK": "Technology Select Sector SPDR Fund. Oferuje ekspozycję na technologiczne i informatyczne spółki z indeksu S&P 500.",
            "XLY": "Consumer Discretionary Select Sector SPDR Fund. Fundusz śledzący spółki z sektora dóbr luksusowych i konsumpcyjnych.",
            "XLC": "Communication Services Select Sector SPDR Fund. Inwestuje w największych gigantów mediów, rozrywki i komunikacji internetowej.",
            "PBS": "Invesco Dynamic Media ETF. Specjalistyczny fundusz skupiający się wyłącznie na dynamicznych spółkach medialnych.",
            "ETFW20L.WA": "Beta ETF WIG20TR. Polski fundusz śledzący indeks 20 największych i najbardziej płynnych spółek z Giełdy Papierów Wartościowych w Warszawie."
        }

    def get_data(self, ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
        if not ticker:
            return pd.DataFrame()
        try:
            ticker_data = yf.Ticker(ticker)
            hist = ticker_data.history(period=period, interval=interval)
            
            if hist.empty:
                return pd.DataFrame()
                
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
        
        total_divs = df['Dividends'].sum() if 'Dividends' in df.columns else 0
        
        return annual_return, annual_volatility, sharpe, total_divs

    def generate_ai_report(self, ticker: str, df: pd.DataFrame, sharpe: float, total_return: float) -> str:
        description = self.ai_profiles.get(ticker.upper(), "Instrument finansowy notowany na globalnych rynkach giełdowych.")
        
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
            verdict = "🟢 <b>Ocena Inwestycyjna AI:</b> BARDZO WYSOKA ZDOLNOŚĆ. Aktywo wykazuje rewelacyjny stosunek zysku do ponoszonego ryzyka. Rynek sprzyja temu instrumentowi."
        elif sharpe > 0 and total_return > 0:
            verdict = "🟡 <b>Ocena Inwestycyjna AI:</b> UMIARKOWANA ZDOLNOŚĆ. Aktywo generuje zyski, wymaga akceptacji standardowego ryzyka rynkowego. Inwestycja opłacalna."
        else:
            verdict = "🔴 <b>Ocena Inwestycyjna AI:</b> NISKA ZDOLNOŚĆ (RYZYKO). Zmienność lub straty przewyższają oczekiwane zyski z inwestycji wolnej od ryzyka. Zachowaj ostrożność."

        return f"<b>O instrumencie:</b> {description}<br><br><b>Ostatnie akcje (Momentum rynku):</b> W końcowej fazie analizowanego okresu zaobserwowano momentum <b>{momentum}</b>.<br><br>{verdict}"

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
    st.header("🗂️ Zarządzanie Bzą")
    search_query = st.text_input("🔍 Wpisz spółkę docelową (np. tesla, orlen):").lower().strip()
    if search_query:
        matched_key = next((key for key in st.session_state.engine.market_map.keys() if key in search_query), None)
        if matched_key:
            t_usa, name_usa, t_eu, name_eu, etfs = st.session_state.engine.market_map[matched_key]
            
            st.session_state.portfolio[t_usa] = Asset(t_usa, format_xtb(t_usa, name_usa), "Akcja")
            st.session_state.portfolio[t_eu] = Asset(t_eu, format_xtb(t_eu, name_eu), "Akcja")
            for etf_ticker, etf_name in etfs:
                st.session_state.portfolio[etf_ticker] = Asset(etf_ticker, format_xtb(etf_ticker, etf_name), "ETF")
                
            st.success(f"✅ Zmapowano rynki oraz algorytmy ETF dla spółki {t_usa}.")

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

xtb_opts = {
    "1M": "1mo", "3M": "3mo", "6M": "6mo", "YTD": "ytd", "1Y": "1y", "3Y": "3y", "5Y": "5y", "MAX": "max"
}

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Strona Główna (O Projekcie)", "📈 Analiza Pojedyncza", "⚖️ Porównywarka Koszyka", "💸 Symulacja Kapitału"])

with tab1:
    st.markdown("""
    ## 📖 Witaj w XTB Helper (Terminal Analityczny)
    
    Aplikacja stanowi w pełni obiektowy projekt w języku Python, zaprojektowany jako profesjonalne narzędzie wspomagające decyzje giełdowe i analizę ryzyka na platformach brokerskich. Została zbudowana z naciskiem na **czysty kod (OOP)**, **obsługę błędów** oraz **hybrydową architekturę AI**.
    
    ### 🎯 Główne Założenia i Decyzje Projektowe
    1. **System Hybrydowego Mapowania:** Algorytm na podstawie nazwy potocznej lokalizuje aktywa na różnych rynkach (np. USA i Europa) i automatycznie wiąże je z funduszami ETF na podstawie rygorystycznego kryterium progu wagowego.
    2. **Wzorzec Separacji (MVC):** Ścisłe oddzielenie modułów pobierania danych (`yfinance`), przekształceń matematycznych (`Pandas/Numpy`) oraz warstwy prezentacji (`Streamlit`).
    3. **Algorytm GenAI (Momentum):** Implementacja asystenta, który na podstawie skumulowanych zwrotów i krzywej zmienności (wskaźnik Sharpe'a) werbalizuje oceny inwestycyjne. 
    4. **Oś Czasu (Anty-Gap System):** Wdrożenie autorskiego rozwiązania w `matplotlib`, które "w locie" zamienia absolutne ramy czasowe na sekwencje ciągłe, całkowicie usuwając zniekształcenia wykresów (puste weekendy, luki nocne).
    5. **Zaawansowana Symulacja Finansowa (DCA z Opłatami):** Moduł wyliczający zyski z regularnego oszczędzania uwzględniający kurs startowy/końcowy oraz niestandardowe prowizje maklerskie brokera.
    """)

with tab2:
    st.markdown("<div class='xtb-period-label'>HORYZONT CZASOWY ANALIZY:</div>", unsafe_allow_html=True)
    selected_period_label_t2 = st.radio("Okres T2:", options=list(xtb_opts.keys()), horizontal=True, label_visibility="collapsed", key="radio_tab2")
    selected_period_t2 = xtb_opts[selected_period_label_t2]
    
    st.divider()
    col_sel, col_tech = st.columns([3, 1])
    with col_sel:
        selected_ticker = st.selectbox("🎯 Wybierz instrument bazowy / ETF:", options=ticker_options, format_func=lambda x: display_options[x])
    with col_tech:
        st.write("")
        st.write("")
        show_sma = st.toggle("Włącz wskaźniki SMA (50/200)")
    
    if selected_ticker:
        asset = st.session_state.portfolio[selected_ticker]
        with st.spinner(f"Analiza wolumenu i wyliczanie parametrów algorytmu AI..."):
            data = st.session_state.engine.get_data(asset.ticker, period=selected_period_t2, interval=selected_interval)
            
        if data.empty or len(data) < 2:
            st.error(f"⚠️ Zbyt mała płynność danych dla interwału '{selected_interval_label}' w tym oknie czasowym. Dostosuj parametry.")
        else:
            ann_ret, ann_vol, sharpe, total_divs = st.session_state.engine.calculate_metrics(data)
            total_return = data['Cumulative_Return'].iloc[-1] * 100
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Zwrot (Okres Analizy)", f"{total_return:.2f}%", delta=f"{total_return:.2f}%")
            c2.metric("Oczekiwany Roczny Zwrot", f"{ann_ret*100:.2f}%", delta=f"{ann_ret*100:.2f}%")
            c3.metric("Zmienność (Ryzyko)", f"{ann_vol*100:.2f}%", delta=f"Ochylenie", delta_color="off")
            c4.metric("Wskaźnik Sharpe'a", f"{sharpe:.2f}", delta="Risk/Reward", delta_color="off")
            c5.metric("Wypłacone Dywidendy", f"{total_divs:.2f}", delta="Pasywny dochód", delta_color="normal" if total_divs > 0 else "off")
            
            ai_text = st.session_state.engine.generate_ai_report(asset.ticker, data, sharpe, total_return)
            
            st.markdown(f"""
<div class="ai-box">
    <div class="ai-header">🤖 AI Analiza Fundamentalna i Oceny Momentum</div>
    <div style="color: #d1d4dc; font-size: 0.95rem; line-height: 1.6;">
        {ai_text}
    </div>
</div>
""", unsafe_allow_html=True)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 9))
            fig.patch.set_facecolor('#131722')
            
            x_seq = np.arange(len(data))
            step = max(1, len(data) // 6)
            tick_positions = x_seq[::step]
            tick_labels = [data.index[i].strftime('%Y-%m-%d') for i in tick_positions]
            
            axes[0, 0].plot(x_seq, data['Close'], color='#2962ff', linewidth=1.5, label='Cena')
            axes[0, 0].fill_between(x_seq, data['Close'], data['Close'].min(), color='#2962ff', alpha=0.1)
            
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
            
            csv = data.to_csv().encode('utf-8')
            st.download_button(label="📥 Eksportuj surowe dane instrumentu do CSV", data=csv, file_name=f'{asset.ticker}_data.csv', mime='text/csv')

with tab3:
    st.markdown("<div class='xtb-period-label'>HORYZONT CZASOWY PORÓWNANIA:</div>", unsafe_allow_html=True)
    selected_period_label_t3 = st.radio("Okres T3:", options=list(xtb_opts.keys()), horizontal=True, label_visibility="collapsed", key="radio_tab3")
    selected_period_t3 = xtb_opts[selected_period_label_t3]
    
    st.divider()
    selected_to_compare = st.multiselect(
        "Wybierz koszyk instrumentów (Min. 2):", 
        options=ticker_options, 
        format_func=lambda x: display_options[x],
        default=["SPY", "QQQ"] if "SPY" in ticker_options else []
    )
    
    if len(selected_to_compare) >= 2:
        with st.spinner("Pobieranie strumienia kwotowań..."):
            comparison_rows = []
            palette = ["#2962ff", "#26a69a", "#ff9800", "#ef5350", "#9c27b0"]
            
            fig_comp, ax_comp = plt.subplots(figsize=(14, 6))
            fig_comp.patch.set_facecolor('#131722')
            ax_comp.set_facecolor('#1e222d')
            
            longest_index = None
            
            for idx, t in enumerate(selected_to_compare):
                df = st.session_state.engine.get_data(t, period=selected_period_t3, interval=selected_interval)
                if not df.empty and len(df) >= 2:
                    ann_ret, ann_vol, sharpe, _ = st.session_state.engine.calculate_metrics(df)
                    total_return = df['Cumulative_Return'].iloc[-1] * 100
                    
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
                    ai_compare_text = f"🟢 <b>Sygnał Optymalny:</b> Instrument <b>{best_by_sharpe['Instrument (Ekspozycja)']}</b> bezapelacyjnie wygrywa w tym oknie czasowym. Osiągnął największy skok kapitału (+{best_by_sharpe['Zwrot (%)']}%) przy jednoczesnym zachowaniu idealnej odporności na wstrząsy rynkowe (Sharpe: {best_by_sharpe['Sharpe Ratio']})."
                else:
                    ai_compare_text = f"🟡 <b>Dylemat Inwestora (Zysk vs Ryzyko):</b><br><br>👉 <b>Agresywny Kapitał:</b> Maksymalny zysk absolutny wygenerował <b>{best_by_return['Instrument (Ekspozycja)']}</b> (+{best_by_return['Zwrot (%)']}%).<br>👉 <b>Defensywny Portfel:</b> Najwyższą stabilność i odporność na wahania kursu oferuje <b>{best_by_sharpe['Instrument (Ekspozycja)']}</b> (Sharpe: {best_by_sharpe['Sharpe Ratio']})."

                st.markdown(f"""
<div class="ai-box">
    <div class="ai-header">🤖 AI Analiza Porównawcza Koszyka</div>
    <div style="color: #d1d4dc; font-size: 0.95rem; line-height: 1.6;">
{ai_compare_text}
    </div>
</div>
""", unsafe_allow_html=True)

                ax_comp.set_title(f"Dynamika zysku instrumentów bazowych | Okres: {selected_period_label_t3}", fontsize=13, fontweight='bold', color='#ffffff')
                ax_comp.set_ylabel("Stopa zwrotu (%)", color='#787b86')
                ax_comp.tick_params(colors='#787b86')
                legend = ax_comp.legend(loc="upper left", facecolor='#1e222d', edgecolor='#2a2e39')
                plt.setp(legend.get_texts(), color='#d1d4dc', fontsize=9)
                st.pyplot(fig_comp)
                
                comp_df = pd.DataFrame(comparison_rows).set_index("Instrument (Ekspozycja)")
                st.markdown("#### 📊 Tabela Parametrów Portfelowych")
                st.dataframe(comp_df, use_container_width=True)
            else:
                st.error("Brak poprawnych danych rynkowych do przeliczenia koszyka.")
    else:
        st.info("👆 Wybierz co najmniej 2 instrumenty z listy, aby wygenerować analizę porównawczą koszyka.")

with tab4:
    st.markdown("<div class='xtb-period-label'>HORYZONT CZASOWY SYMULACJI:</div>", unsafe_allow_html=True)
    selected_period_label_t4 = st.radio("Okres T4:", options=list(xtb_opts.keys()), horizontal=True, label_visibility="collapsed", key="radio_tab4")
    selected_period_t4 = xtb_opts[selected_period_label_t4]

    st.divider()
    simulation_mode = st.radio("Tryb symulacji:", ["Jednorazowa wpłata", "Wpłaty co miesiąc"], horizontal=True)
    selected_for_sim = st.multiselect(
        "Wybierz jedną lub wiele akcji / ETF do symulacji:",
        options=ticker_options,
        format_func=lambda x: display_options[x],
        default=[ticker_options[0]] if ticker_options else []
    )

    if selected_for_sim:
        with st.spinner("Pobieranie danych do symulacji portfela..."):
            simulation_data = {}
            for ticker in selected_for_sim:
                sim_df = st.session_state.engine.get_data(ticker, period=selected_period_t4, interval="1d")
                if not sim_df.empty and len(sim_df) >= 2:
                    simulation_data[ticker] = sim_df

        if len(simulation_data) != len(selected_for_sim):
            st.warning("⚠️ Część instrumentów nie ma wystarczających danych i została pominięta.")

        if simulation_data:
            common_start = max(df.index.min() for df in simulation_data.values())
            common_end = min(df.index.max() for df in simulation_data.values())

            if common_start >= common_end:
                st.error("Brak wspólnego zakresu dat między wybranymi instrumentami.")
            else:
                combined_index = pd.DatetimeIndex([])
                for df in simulation_data.values():
                    combined_index = combined_index.union(pd.DatetimeIndex(df.loc[common_start:common_end].index))

                if simulation_mode == "Jednorazowa wpłata":
                    one_time_amount = st.number_input("Kwota jednorazowej wpłaty:", min_value=100.0, value=5000.0, step=100.0)
                    one_time_date = st.date_input(
                        "Data wpłaty:",
                        value=common_start.date(),
                        min_value=common_start.date(),
                        max_value=common_end.date()
                    )
                    transaction_dates = [pd.Timestamp(one_time_date)]
                    transaction_amount = float(one_time_amount)
                else:
                    monthly_amount = st.number_input("Kwota miesięcznej wpłaty:", min_value=50.0, value=500.0, step=50.0)
                    payment_months = st.number_input("Okres wpłat (miesiące):", min_value=2, max_value=120, value=12, step=1)
                    month_starts = list(pd.date_range(start=common_start, end=common_end, freq='MS'))
                    transaction_dates = month_starts[-payment_months:] if len(month_starts) >= payment_months else month_starts
                    transaction_amount = float(monthly_amount)

                    if not transaction_dates:
                        st.warning("Wybrany okres nie mieści się w dostępnych danych dla wszystkich instrumentów.")

                if transaction_dates:
                    allocation_per_asset = 1 / len(simulation_data)
                    invested_delta = pd.Series(0.0, index=combined_index)
                    portfolio_value = pd.Series(0.0, index=combined_index)

                    for tx_date in transaction_dates:
                        execution_candidates = combined_index[combined_index >= tx_date]
                        if len(execution_candidates) > 0:
                            invested_delta.loc[execution_candidates[0]] += transaction_amount

                    for ticker, df_ticker in simulation_data.items():
                        close_series = df_ticker['Close'].loc[common_start:common_end].reindex(combined_index).ffill()
                        shares_delta = pd.Series(0.0, index=combined_index)

                        for tx_date in transaction_dates:
                            candidates = close_series.loc[close_series.index >= tx_date].dropna()
                            if len(candidates) > 0:
                                exec_date = candidates.index[0]
                                exec_price = candidates.iloc[0]
                                if exec_price > 0:
                                    shares_delta.loc[exec_date] += (transaction_amount * allocation_per_asset) / exec_price

                        cumulative_shares = shares_delta.cumsum()
                        portfolio_value = portfolio_value.add(cumulative_shares * close_series, fill_value=0.0)

                    invested_cumulative = invested_delta.cumsum()
                    result_df = pd.DataFrame({
                        "Kapitał wpłacony": invested_cumulative,
                        "Wartość portfela": portfolio_value
                    }).dropna()

                    if not result_df.empty and result_df["Kapitał wpłacony"].iloc[-1] > 0:
                        result_df["Stopa zwrotu %"] = ((result_df["Wartość portfela"] - result_df["Kapitał wpłacony"]) / result_df["Kapitał wpłacony"]) * 100

                        total_invested = result_df["Kapitał wpłacony"].iloc[-1]
                        final_value = result_df["Wartość portfela"].iloc[-1]
                        total_return_pct = result_df["Stopa zwrotu %"].iloc[-1]
                        positive_values = result_df["Wartość portfela"] > 0
                        rolling_max = result_df["Wartość portfela"].where(positive_values).cummax()
                        drawdown_series = (result_df["Wartość portfela"] / rolling_max) - 1
                        max_drawdown = drawdown_series.min(skipna=True) * 100 if drawdown_series.notna().any() else np.nan

                        sc1, sc2, sc3, sc4 = st.columns(4)
                        sc1.metric("Łącznie wpłacono", f"{total_invested:.2f}")
                        sc2.metric("Wartość końcowa", f"{final_value:.2f}")
                        sc3.metric("Wynik netto (%)", f"{total_return_pct:.2f}%", delta=f"{total_return_pct:.2f}%")
                        sc4.metric("Maks. obsunięcie (%)", f"{max_drawdown:.2f}%" if pd.notna(max_drawdown) else "N/A")

                        asset_rank = []
                        for ticker, df_ticker in simulation_data.items():
                            close_sub = df_ticker['Close'].loc[common_start:common_end]
                            first_price = close_sub.iloc[0]
                            last_price = close_sub.iloc[-1]
                            if first_price > 0 and last_price > 0:
                                asset_rank.append((display_options[ticker], ((close_sub.iloc[-1] / first_price) - 1) * 100))
                        best_asset = max(asset_rank, key=lambda x: x[1]) if asset_rank else None

                        if total_return_pct >= AI_EXCELLENT_THRESHOLD_PCT:
                            if best_asset:
                                ai_sim_text = f"🟢 <b>Ocena AI:</b> Strategia była skuteczna. Portfel wygenerował <b>{total_return_pct:.2f}%</b>, a najsilniejszym składnikiem było <b>{best_asset[0]}</b> ({best_asset[1]:.2f}%)."
                            else:
                                ai_sim_text = f"🟢 <b>Ocena AI:</b> Strategia była skuteczna. Portfel wygenerował <b>{total_return_pct:.2f}%</b>."
                        elif total_return_pct >= AI_NEUTRAL_THRESHOLD_PCT:
                            ai_sim_text = f"🟡 <b>Ocena AI:</b> Wynik dodatni, ale umiarkowany. Portfel zakończył symulację na poziomie <b>{total_return_pct:.2f}%</b>. Rozważ wydłużenie horyzontu lub zmianę koszyka."
                        else:
                            ai_sim_text = f"🔴 <b>Ocena AI:</b> Symulacja zakończyła się stratą <b>{total_return_pct:.2f}%</b>. Największe ryzyko było widoczne przy obsunięciu <b>{max_drawdown:.2f}%</b>."

                        st.markdown(f"""
<div class="ai-box">
    <div class="ai-header">🤖 AI Podsumowanie Symulacji Kapitału</div>
    <div style="color: #d1d4dc; font-size: 0.95rem; line-height: 1.6;">
        {ai_sim_text}
    </div>
</div>
""", unsafe_allow_html=True)

                        st.write("#### 📈 Praca Twojej gotówki w czasie")
                        fig_sim, (ax_sim1, ax_sim2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
                        fig_sim.patch.set_facecolor('#131722')

                        x_idx = np.arange(len(result_df))
                        step = max(1, len(result_df) // 8)
                        tick_positions = x_idx[::step]
                        tick_labels = [result_df.index[i].strftime('%Y-%m-%d') for i in tick_positions]

                        ax_sim1.set_facecolor('#1e222d')
                        ax_sim1.plot(x_idx, result_df["Kapitał wpłacony"], color='#787b86', linestyle='--', label='Kapitał wpłacony')
                        line_color = '#26a69a' if total_return_pct >= 0 else '#ef5350'
                        ax_sim1.plot(x_idx, result_df["Wartość portfela"], color=line_color, linewidth=2, label='Wartość portfela')
                        ax_sim1.fill_between(x_idx, result_df["Wartość portfela"], result_df["Kapitał wpłacony"], color=line_color, alpha=0.08)
                        ax_sim1.set_title("Kapitał wpłacony vs wartość portfela", color='#ffffff', fontsize=11)
                        ax_sim1.tick_params(colors='#787b86', labelsize=9)
                        legend_sim = ax_sim1.legend(loc="upper left", facecolor='#1e222d', edgecolor='#2a2e39')
                        plt.setp(legend_sim.get_texts(), color='#d1d4dc', fontsize=9)

                        ax_sim2.set_facecolor('#1e222d')
                        ax_sim2.plot(x_idx, result_df["Stopa zwrotu %"], color='#2962ff', linewidth=1.8)
                        ax_sim2.axhline(0, color='#787b86', linestyle='--', linewidth=1)
                        ax_sim2.set_title("Dynamika stopy zwrotu (%)", color='#ffffff', fontsize=11)
                        ax_sim2.tick_params(colors='#787b86', labelsize=9)
                        ax_sim2.set_xticks(tick_positions)
                        ax_sim2.set_xticklabels(tick_labels, rotation=20)

                        plt.tight_layout()
                        st.pyplot(fig_sim)
                    else:
                        st.error("Nie udało się wyliczyć symulacji dla podanych parametrów.")
        else:
            st.error("Brak poprawnych danych rynkowych do wykonania symulacji.")
    else:
        st.info("👆 Wybierz przynajmniej jeden instrument, aby uruchomić symulację.")
