import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '6304275110:AAH7Nh6sVcfouUjTKDuR8zYArrCcFDlv_EM'

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Function to scrape data from the URL
def scrape_data(username, mode="osu"):
    url = f"https://ameobea.me/osutrack/user/{username}/{mode}"
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td')

        data = {
            "Rank": None,
            "PP": None,
            "Accuracy": None,
            "Plays": None,
            "Level": None,
            "Country": None,
            "Flag": None,
        }

        for td in td_elements:
            text = td.get_text(strip=True)
            if text.startswith("Rank"):
                data["Rank"] = text.replace("Rank", "").strip()
            elif text.startswith("PP"):
                data["PP"] = text.replace("PP", "").strip()
            elif text.startswith("Accuracy"):
                data["Accuracy"] = text.replace("Accuracy", "").strip()
            elif text.startswith("Plays"):
                data["Plays"] = text.replace("Plays", "").strip()
            elif text.startswith("Level"):
                data["Level"] = text.replace("Level", "").strip()
            elif text.startswith("Country"):
                country = text.replace("Country", "").strip()
                data["Country"] = country
                # Find the country flag
                flag_img = td.find("img")
                if flag_img:
                    flag_url = flag_img["src"]
                    data["Flag"] = flag_url

        # Find the avatar image
        avatar_img = soup.find("div", class_="useravatar").find("img")
        avatar_url = avatar_img["src"] if avatar_img else "Avatar not found"

        return data, avatar_url
    else:
        return None, None

# Function to convert ISO country code to flag emoji
def iso_country_code_to_flag_emoji(country_code):
    # Mapping of country codes to flag emojis
    flag_emojis = {
        "US": "🇺🇸",
        "CA": "🇨🇦",
        "GB": "🇬🇧",
        "UA": "🇺🇦",  # Ukraine
        "RU": "🇷🇺",  # Russia
        # Add more country codes and emojis as needed
    }
    return flag_emojis.get(country_code, "🏳️")

# Handler for the /show command
@bot.message_handler(commands=['show'])
def handle_show(message):
    # Check if the command has the expected format
    if len(message.text.split()) == 2:
        _, username = message.text.split()
        data, avatar_url = scrape_data(username, "osu")
        if data:
            if data["Flag"]:
                country_emoji = iso_country_code_to_flag_emoji(data["Country"])
                country_info = f"Country: {country_emoji} {data['Country']}"
            else:
                country_info = "Country: Not available"
                
            bot.send_photo(message.chat.id, avatar_url, caption=f"Avatar for {username}")
            response = f"OSU Data for {username}:\n"
            for key, value in data.items():
                if key not in ("Country", "Flag"):
                    response += f"{key}: {value}\n"
            response += f"{country_info}"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Failed to retrieve the web page. Please check the username and try again.")
    else:
        bot.send_message(message.chat.id, "Invalid command format. Please use /show \"username\".")


@bot.message_handler(commands=['show_mania'])
def handle_show_mania(message):
    # Check if the command has the expected format
    if len(message.text.split()) == 2:
        _, username = message.text.split()
        data, avatar_url = scrape_data(username, "mania")  # Викликаємо нову функцію scrape_mania_data
        if data:
            if data["Flag"]:
                country_emoji = iso_country_code_to_flag_emoji(data["Country"])
                country_info = f"Country: {country_emoji} {data['Country']}"
            else:
                country_info = "Country: Not available"
                
            bot.send_photo(message.chat.id, avatar_url, caption=f"Avatar for {username}")
            response = f" Mania Data for {username}:\n"
            for key, value in data.items():
                if key not in ("Country", "Flag"):
                    response += f"{key}: {value}\n"
            response += f"{country_info}"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Failed to retrieve the web page. Please check the username and try again.")
    else:
        bot.send_message(message.chat.id, "Invalid command format. Please use /show_mania \"username\".")

# Function to scrape data from the Mania URL


@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = "List of available commands:\n"
    help_text += "/show username - Shows information about the osu player!\n"
    help_text += "/show_mania username - Shows information about the mania player!\n"
    help_text += "/help - Shows this list of commands"
    
    bot.send_message(message.chat.id, help_text)

# Start the bot and listen for updates
bot.polling(timeout=60)
