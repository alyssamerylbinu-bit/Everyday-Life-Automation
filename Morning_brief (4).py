# Date & Time
import requests
from datetime import datetime

now = datetime.now()
today_date = now.strftime("%A,%d %B %Y")
time_now = now.strftime("%I:%M %p")

print("🌄 Good Morning!")
print()
print("📆 Date:", today_date)
print("🕔Time:", time_now)

# Weather
print()
print('⛅Weather')

city_name = input('Enter the city: ')
API_Key = '453c98ac0e8d9eed051b7a3fa7b7fbb7'
url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_Key}&units=metric"

response = requests.get(url)
weather_data = requests.get(url).json()

if weather_data.get("cod") != 200:
    print("City not found! Please check spelling.")
    pass

else:
    temperature = weather_data['main']['temp']
    condition = weather_data['weather'][0]['description'].title()
    main_condition = weather_data["weather"][0]["main"]

weather_emojis = {
    "Few Clouds": "🌤️",
    "Clear": "☀️",
    "Clear Sky": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌁",
    "Haze": "🌫️",
    "Smog": "💨"
}

emoji = weather_emojis.get(condition, "🌍")

print("Temperature:", temperature, "°C")
print(f"Condition: {condition} {emoji}")

# Live News
print()
print('📰Live News')

news_API_Key = 'pub_a1274ad39afc4a69a455cf2e6e65c15b'
url = f"https://newsdata.io/api/1/news?apikey=pub_a1274ad39afc4a69a455cf2e6e65c15b&q=india%20AND%20(politics%20OR%20technology%20OR%20sports%20OR%20cricket)&language=en&country=in"

response = requests.get(url)
news_data = response.json()
articles = news_data["results"][:5]

print()
print("🗞️ Top News Headlines:",)
for i, article in enumerate(articles, 1):
    print(f"{i}. {article['title']}")
