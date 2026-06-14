# Opis Struktur i Architektury Projektu Finansowego

### 1. Opis i przeznaczenie klas (OOP)

* **Klasa `Asset` (Model struktury danych):**
    * **Przeznaczenie:** Reprezentuje pojedyncze aktywo finansowe obecne na rynku giełdowym. 
    * **Pola klasy:**
        * `ticker`: Unikalny, giełdowy skrót identyfikacyjny aktywa (zawsze konwertowany do wielkich liter, np. AAPL, SPY).
        * `name`: Pełna, przyjazna dla użytkownika nazwa instrumentu finansowego lub spółki.
        * `asset_type`: Kategoria instrumentu (wybór pomiędzy "Akcja" a "ETF").
    * **Zastosowanie:** Obiekty tej klasy są dynamicznie tworzone przez użytkownika za pomocą formularza i przechowywane w strukturze słownikowej sesji, co eliminuje chaos w zarządzaniu pamięcią.

* **Klasa `FinancialEngine` (Silnik obliczeniowy i warstwa danych):**
    * **Przeznaczenie:** Izoluje całą logikę biznesową, komunikację sieciową z zewnętrznym API Yahoo Finance oraz skomplikowane operacje matematyczne.
    * **Metody klasy:**
        * `get_data(ticker, period)`: Odpowiada za asynchroniczne pobieranie danych rynkowych. Posiada wbudowaną konstrukcję `try-except` przechwytującą błędy braku łączności oraz walidację pustych zapytań. Zwraca przefiltrowany obiekt `DataFrame` (ceny zamknięcia).
        * `calculate_metrics(df)`: Realizuje zaawansowaną transformację struktur danych. Oblicza dzienne stopy zwrotu aktywa, jego skumulowany zysk w czasie, roczną zannualizowaną stopę zwrotu oraz roczne odchylenie standardowe (będące miarą ryzyka zmienności rynkowej). Na koniec wyznacza kluczowy wskaźnik efektywności inwestycyjnej — **Sharpe Ratio**.

### 2. Spełnienie kryteriów na ocenę 5.0

* **Prawidłowa implementacja paradygmatu OOP:** Kod nie jest zwykłym ciągiem instrukcji (skryptem strukturalnym). Podział na klasę reprezentującą strukturę danych (`Asset`) i klasę wykonawczą (`FinancialEngine`) w pełni separuje odpowiedzialności w programie.
* **Nietrywialna transformacja danych:** Program samodzielnie przetwarza surowe szeregi czasowe cen rynkowych, przekształcając je przy pomocy metod statystycznych biblioteki `pandas` i `numpy` w użyteczne wskaźniki ryzyka i zysku.
* **System Ekspercki (Automatyczne wnioskowanie):** Aplikacja na podstawie wyliczonego wskaźnika Sharpe'a podejmuje superpowerową, autonomiczną decyzję o klasyfikacji jakościowej aktywa, wyświetlając użytkownikowi odpowiedni, dedykowany komunikat analityczny (sukces, informacja lub ostrzeżenie).
* **Kompletna wizualizacja (Zestaw 4 wykresów):** Interfejs prezentuje pełen profil statystyczny instrumentu za pomocą czterech odmiennych prezentacji graficznych (Line Plot kursu, Histogram rozkładu stóp, Line Plot skumulowanej stopy oraz Boxplot rozrzutu zmienności).
* **Nowoczesne wdrożenie (Cloud Deployment):** Kod został w pełni zintegrowany z plikiem konfiguracyjnym środowiska (`requirements.txt`), co pozwala na bezproblemową kompilację i stałe uruchomienie aplikacji w chmurze za pomocą platformy Streamlit Community Cloud pod publicznym adresem URL.