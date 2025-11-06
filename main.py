from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout
import sys
from api_key import API_KEY  # Importujemo API ključ
import requests  # Biblioteka za slanje HTTP zahtjeva

class Home(QWidget):
    """Glavna klasa za Weather aplikaciju koja nasljeđuje QWidget"""
    
    def __init__(self):
        """Konstruktor klase - poziva se kada se kreira novi objekat"""
        super().__init__()  # Pozivamo konstruktor roditeljske klase (QWidget)
        self.settings()  # Postavljamo osnovne postavke prozora
        self.initUI()  # Inicijalizujemo korisničko 

    def settings(self):
        """Postavlja osnovne parametre prozora"""
        self.setWindowTitle("Weather App")  # Postavlja naslov prozora
        self.setGeometry(250, 250, 500, 400)  # Pozicija (x, y) i dimenzije (širina, visina) - povećao visinu

    def initUI(self):
        """Kreira i postavlja sve elemente"""
        
        # Kreiramo label (tekst) za naslov aplikacije
        self.title = QLabel("🌍 Weather App")
        self.title.setObjectName("title")  # Dodajemo ID za CSS stilizovanje
        
        # Kreiramo polje za unos teksta (input box)
        self.input_box = QLineEdit()
        # Postavljamo placeholder tekst koji se prikazuje kad je polje prazno
        self.input_box.setPlaceholderText("Enter a city name (e.g., London, Paris, New York)...")
        
        # Povezujemo Enter tipku sa pretragom - kada korisnik pritisne Enter, poziva se search_click
        self.input_box.returnPressed.connect(self.search_click)

        # Kreiramo label gdje će se prikazivati rezultati vremenske prognoze
        self.output = QLabel("Enter a city name and press Search or Enter")
        self.output.setObjectName("output")  # ID za CSS
        self.output.setWordWrap(True)  # Omogućava prelazak teksta u novi red ako je predug
        
        # Kreiramo dugme za pretragu
        self.submit = QPushButton("🔍 Search")

        # Kreiramo vertikalni layout (raspored elemenata odozgo prema dolje)
        self.master = QVBoxLayout()
        self.master.setSpacing(15)  # Razmak između elemenata
        self.master.setContentsMargins(20, 20, 20, 20)  # Margine oko layouta
        
        # Dodajemo sve elemente u layout redom kako želimo da se prikazuju
        self.master.addWidget(self.title)
        self.master.addWidget(self.input_box)
        self.master.addWidget(self.submit)
        self.master.addWidget(self.output)

        # Postavljamo kreirani layout kao glavni layout prozora
        self.setLayout(self.master)

        # Povezujemo klik na dugme sa funkcijom search_click
        # Kada korisnik klikne dugme, poziva se search_click funkcija
        self.submit.clicked.connect(self.search_click)
        
        # Dodajemo CSS stilove za ljepši izgled aplikacije
        self.apply_styles()

    def apply_styles(self):
        """Primjenjuje CSS stilove na elemente aplikacije"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2c3e50, stop:1 #34495e);
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                padding: 15px;
                color: #ecf0f1;
            }
            QLabel#output {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 20px;
                font-size: 15px;
                min-height: 150px;
            }
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #2ecc71;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    def search_click(self):
        """Funkcija koja se izvršava kada korisnik klikne na dugme Search ili pritisne Enter"""
        
        # Uzimamo tekst koji je korisnik unio u input box i uklanjamo prazne razmake
        location = self.input_box.text().strip()
        
        # Provjeravamo da li je korisnik uopšte unio nešto
        if not location:
            self.output.setText("⚠️ Please enter a city name!")
            return
        
        # Prikazujemo loading poruku dok čekamo odgovor od API-ja
        self.output.setText("🔄 Loading weather data...")
        
        # Pozivamo funkciju get_weather sa API ključem i lokacijom
        weather_info = self.get_weather(API_KEY, location)
        
        # Prikazujemo dobijene informacije o vremenu u output labelu
        self.output.setText(weather_info)

    def get_weather_emoji(self, description):
        """
        Vraća odgovarajući emoji za opis vremena
        
        Parametri:
        - description: Tekstualni opis vremena (npr. "clear sky", "light rain")
        """
        # Pretvaramo opis u mala slova da olakšamo poređenje
        description = description.lower()
        
        # Provjeravamo ključne riječi u opisu i vraćamo odgovarajući emoji
        if "clear" in description:
            return "☀️"
        elif "cloud" in description:
            return "☁️"
        elif "rain" in description or "drizzle" in description:
            return "🌧️"
        elif "snow" in description:
            return "❄️"
        elif "thunder" in description or "storm" in description:
            return "⛈️"
        elif "mist" in description or "fog" in description:
            return "🌫️"
        else:
            return "🌤️"

    def get_weather(self, api_key, city, country=""):
        """
        Funkcija koja šalje zahtjev API servisu i vraća informacije o vremenu
        
        Parametri:
        - api_key: Ključ za pristup OpenWeatherMap API-ju
        - city: Naziv grada za koji tražimo vremensku prognozu
        - country: Kod države (opciono, default je prazan string)
        """
        
        # Bazni URL za OpenWeatherMap API
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        # Parametri koji se šalju u API zahtjevu
        # 'q' je query parametar (lokacija), 'appid' je API ključ
        params = {'q': f'{city},{country}', 'appid': api_key}

        try:
            # Šaljemo GET zahtjev API servisu sa parametrima
            res = requests.get(base_url, params=params)
            
            # Konvertujemo odgovor iz JSON formata u Python dictionary
            data = res.json()
            
            # Provjeravamo da li je zahtjev uspješan (status code 200 znači OK)
            if res.status_code == 200:
                # Izvlačimo naziv grada iz odgovora
                city_name = data['name']
                
                # Izvlačimo kod države iz sekcije 'sys'
                country_code = data['sys']['country']
                
                # Izvlačimo temperaturu u Kelvinima iz sekcije 'main'
                temperature_kelvin = data['main']['temp']
                
                # Konvertujemo Kelvine u Celzijuse (oduzimamo 273.15)
                temperature_celsius = temperature_kelvin - 273.15
                
                # Izvlačimo "feels like" temperaturu i konvertujemo u Celzijuse
                feels_like_kelvin = data['main']['feels_like']
                feels_like_celsius = feels_like_kelvin - 273.15
                
                # Izvlačimo opis vremena iz prve stavke u listi 'weather'
                weather_description = data['weather'][0]['description']
                
                # Dobijamo odgovarajući emoji za opis vremena
                emoji = self.get_weather_emoji(weather_description)
                
                # Izvlačimo vlažnost vazduha (u procentima)
                humidity = data['main']['humidity']
                
                # Izvlačimo brzinu vjetra (u metrima po sekundi)
                wind_speed = data['wind']['speed']
                
                # Izvlačimo pravac vjetra (u stepenima)
                wind_direction = data['wind']['deg']
                
                # Izvlačimo atmosferski pritisak
                pressure = data['main']['pressure']
                
                # Formatiramo sve informacije u jedan string sa novim linijama
                # f"..." je f-string koji omogućava umetanje varijabli direktno u tekst
                # :.2f znači da temperatura treba biti formatirana sa 2 decimale
                weather_info = (
                    f"{emoji} Weather in {city_name}, {country_code}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🌡️ Temperature: {temperature_celsius:.1f}°C\n"
                    f"🤔 Feels like: {feels_like_celsius:.1f}°C\n"
                    f"📝 Description: {weather_description.capitalize()}\n"
                    f"💧 Humidity: {humidity}%\n"
                    f"💨 Wind Speed: {wind_speed} m/s\n"
                    f"🧭 Wind Direction: {wind_direction}°\n"
                    f"🔽 Pressure: {pressure} hPa"
                )
                
                # Vraćamo formatirani string sa informacijama
                return weather_info
            else:
                # Ako status code nije 200, vraćamo poruku o grešci
                return f"❌ Error: {data.get('message', 'City not found')}\n\nPlease check the city name and try again."
                
        except requests.exceptions.ConnectionError:
            # Greška ako nema internet konekcije
            return "❌ Connection Error\n\nPlease check your internet connection and try again."
        except requests.exceptions.Timeout:
            # Greška ako zahtjev traje predugo
            return "❌ Timeout Error\n\nThe request took too long. Please try again."
        except Exception as e:
            # Ako dođe do bilo kakve druge greške,
            # hvatamo tu grešku i vraćamo poruku korisniku
            return f"❌ Error: {str(e)}\n\nSomething went wrong. Please try again."


# Pokretanje aplikacije
if __name__ == "__main__":
    # Provjeravamo da li se skripta pokreće direktno (ne kao modul)
    
    # Kreiramo QApplication objekat (potreban za svaku PyQt aplikaciju)
    app = QApplication(sys.argv)
    
    # Kreiramo instancu našeg Home prozora
    window = Home()
    
    # Prikazujemo prozor na ekranu
    window.show()
    
    # Pokrećemo glavnu petlju aplikacije i čekamo dok korisnik ne zatvori prozor

    sys.exit(app.exec_())

