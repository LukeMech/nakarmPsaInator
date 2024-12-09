import time
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions


# --- OPCJE ---

first_load_time = 3                                     # Czas potrzebny na pierwsze załadowanie strony [sek] (domyślnie: 3)
load_time = 0.5                                         # Czas między kolejnymi kliknięciami na stronie [sek] (domyślnie: 2)
url = "https://nakarmpsa.olx.pl"                        # URL strony
element_to_find = "div.single-pet-control-feed_button"  # Element do kliknięcia jaki ma znaleźć przeglądarka (domyślnie: div.single-pet-control-feed_button)
headless = True                                         # Czy uruchomić przeglądarke w trybie ducha (*True/False)
mute = True                                             # Czy wyciszyć dźwięki strony (*True/False)
use_chrome = False                                      # Użyj Chrome zamiast Firefoxa (True/*False)

# -------------


first_init_time = time.perf_counter() # Licznik czasu 1. uruchomienia
start_time = 0 # Licznik czasu
i = 0 # Counter
crashed = False # Czy przeglądarka się wysypała

print("\n[Ctrl+C by wyjść] Pierwsze uruchomienie może chwilę potrwać. Pobieram przeglądarkę i sterownik automatyzujący.")

# Funkcja do stworzenia okna
def create_browser():
    # Firefox
    if not use_chrome:
        options = FirefoxOptions()
    # Chrome
    else:
        options = ChromeOptions()
    options.add_argument("--start-maximized")  # Pełny ekran  
    options.add_argument("--log-level=3")      # Usunięcie logów  
    if headless:                               # Ukryty
        options.add_argument("--headless")  
    # Firefox
    if not use_chrome:                             
        options.add_argument("--private")          # Tryb incognito 
        if mute:                                   # Wyciszenie przeglądarki 
            options.set_preference("media.volume_scale", "0.0")
        driver = webdriver.Firefox(options=options)
    # Chrome
    else: 
        options.add_argument("--incognito")        # Tryb incognito
        if mute:
            options.add_argument("--mute-audio")   # Wyciszenie przeglądarki
        driver = webdriver.Chrome(options=options)
    return driver

# Start pętli
try:
    while True:
        try:
            if(i==0 or crashed):
                browser = create_browser()

            # Otwieranie strony
            browser.delete_all_cookies()
            browser.get(url)

            # Czekanie na załadowanie strony
            if(i==0 or crashed):
                time.sleep(first_load_time)  
                # Uruchomienie licznika po pobraniu i pierwszym wczytaniu przeglądarki
                if(i==0):
                    start_time = time.perf_counter()
                    init_time = start_time - first_init_time
                    formatted_time_init = str(timedelta(seconds=int(init_time)))
                    print(f"\nCzas inicjalizacji: {formatted_time_init}.\n")
                if(crashed):
                    crashed = False
            else:
                time.sleep(load_time)

            # Znajdź przycisk na stronie
            feed_button = browser.find_element(By.CSS_SELECTOR, element_to_find)
            browser.execute_script("arguments[0].scrollIntoView();", feed_button)
            time.sleep(0.1)

            # Przesuń kursor i kliknij
            try:
                actions = ActionChains(browser)
                actions.move_to_element(feed_button).click().perform()
            except:
                print(f"[{i+1}] Niepowodzenie, ponawiam próbę...")
                continue

            i += 1
            print(f"[{i}] Nakarmiono!")
            
        except Exception as e:
            print(f"Większy błąd: {e}\nRestartuję przeglądarkę.\n")
            crashed = True
            # Zamknięcie przeglądarki
            try:
                browser.quit()  
            except Exception:
                print("Nie udało się zamknąć przeglądarki.")

except KeyboardInterrupt:
    # Podliczenie czasów
    elapsed_time = time.perf_counter() - start_time
    formatted_time_elapsed = str(timedelta(seconds=int(elapsed_time)))
    avg_speed = elapsed_time/i
    print(f"\nZatrzymano po {i} przejściach. Wykonywano przez: {formatted_time_elapsed}. Średnio klikano co {avg_speed:.2f} sekund.")
    print("Pobrane pliki są w katalogu ~/.cache/selenium/, możesz go bezpiecznie usunąć.")
