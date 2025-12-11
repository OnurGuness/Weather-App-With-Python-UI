import customtkinter as ctk
import requests
from PIL import Image
from io import BytesIO  # Resim verisini hafızada işlemek için

# --- AYARLAR ---
API_KEY = "YOUR_OPENWEATHER_API_KEY" # OpenWeatherMap API Anahtarı 
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- UI AYARLARI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("400x550") # Pencereyi biraz uzattık (ikon sığsın diye)
        self.title("Görsel Hava Durumu")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Başlık
        self.title_label = ctk.CTkLabel(self, text="Hava Durumu", font=("Roboto", 24, "bold"))
        self.title_label.pack(pady=20)

        # Giriş Alanı
        self.city_entry = ctk.CTkEntry(self, placeholder_text="Şehir (Örn: Ankara)", width=250, height=40)
        self.city_entry.pack(pady=10)
        self.city_entry.bind('<Return>', lambda event: self.get_weather()) # Enter tuşu ile arama

        # Buton
        self.search_button = ctk.CTkButton(self, text="Sorgula", command=self.get_weather, width=250, height=40)
        self.search_button.pack(pady=10)

        # Sonuç Kartı
        self.result_frame = ctk.CTkFrame(self, width=300, height=250)
        self.result_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Lokasyon Yazısı
        self.location_label = ctk.CTkLabel(self.result_frame, text="-", font=("Arial", 20))
        self.location_label.pack(pady=(20, 5))

        # --- İKON ALANI (Yeni Eklendi) ---
        # Başlangıçta boş bir label, resim gelince dolacak
        self.icon_label = ctk.CTkLabel(self.result_frame, text="") 
        self.icon_label.pack(pady=5)

        # Derece
        self.temp_label = ctk.CTkLabel(self.result_frame, text="- °C", font=("Arial", 40, "bold"), text_color="#FFCC00")
        self.temp_label.pack(pady=5)

        # Açıklama
        self.desc_label = ctk.CTkLabel(self.result_frame, text="-", font=("Arial", 16))
        self.desc_label.pack(pady=10)

    def get_weather(self):
        city = self.city_entry.get()
        if not city:
            return

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "tr"
        }

        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if response.status_code == 200:
                # 1. Metin verilerini al
                city_name = data["name"]
                country = data["sys"]["country"]
                temp = int(data["main"]["temp"])
                desc = data["weather"][0]["description"].title()
                
                # 2. İkon Kodunu Al (Örn: "10d")
                icon_code = data["weather"][0]["icon"]
                
                # 3. İkonu URL'den İndir ve İşle
                icon_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png" # @4x daha net görüntü için
                icon_response = requests.get(icon_url)
                
                # Byte verisini Resme çevir
                img_data = BytesIO(icon_response.content)
                pil_image = Image.open(img_data)
                
                # CustomTkinter formatına çevir (Size: boyut ayarı)
                ctk_icon = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(100, 100))

                # 4. UI Güncelle
                self.location_label.configure(text=f"{city_name}, {country}")
                self.temp_label.configure(text=f"{temp}°C")
                self.desc_label.configure(text=desc)
                self.icon_label.configure(image=ctk_icon) # Resmi etikete ata
                self.icon_label.image = ctk_icon # Referansı hafızada tutmak için (Bug önleyici)
                
            else:
                self.location_label.configure(text="Şehir Bulunamadı")
                self.icon_label.configure(image=None) # Resmi temizle
                self.temp_label.configure(text="-")
                self.desc_label.configure(text="Tekrar deneyin")
                
        except Exception as e:
            self.location_label.configure(text="Bağlantı Hatası")
            print(f"Hata: {e}")

if __name__ == "__main__":
    app = WeatherApp()

    app.mainloop()
