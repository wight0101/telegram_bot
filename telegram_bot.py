import telebot
import requests
import os

TOKEN = 'Telegram_token'  # Replace with your Telegram Bot token
bot = telebot.TeleBot(TOKEN)

API_KEY = "osu_token"  # Replace with your osu! API key

def scrape_data(username, mode):
    url = f"https://osu.ppy.sh/api/get_user?k={API_KEY}&u={username}&m={mode}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_osu_user_avatar(username):
    url = f"https://osu.ppy.sh/api/get_user?k={API_KEY}&u={username}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_info = response.json()
            if user_info and len(user_info) > 0:
                user_id = user_info[0]['user_id']
                avatar_url = f"https://a.ppy.sh/{user_id}"
                return avatar_url
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def handle_show(message, mode):
    args = message.text.split(' ')
    username = args[1]
    username = username.replace(" ", "_")
    data_user = scrape_data(username, mode)
    avatar_url = get_osu_user_avatar(username)
    if data_user:
        user_info = data_user[0]
        response = [
            f"OSU Data for {user_info['username']} (Mode {mode}):",
            f"Rank: {user_info['pp_rank']}",
            f"PP: {user_info['pp_raw']}",
            f"Accuracy: {float(user_info['accuracy']):.2f}%",
            f"Plays: {user_info['playcount']}",
            f"Level: {float(user_info['level']):.2f}",
            f"Country: {user_info['country']}"
        ]
        bot.send_photo(message.chat.id, avatar_url) 
        bot.send_message(message.chat.id, "\n".join(response))  
    else:
        bot.send_message(message.chat.id, "Failed to get user data. Please check your username and try again.")



@bot.message_handler(func=lambda message: message.text.startswith('/0 '))
def handle_mode_0(message):
    handle_show(message, mode="0")

@bot.message_handler(func=lambda message: message.text.startswith('/1 '))
def handle_mode_1(message):
    handle_show(message, mode="1")

@bot.message_handler(func=lambda message: message.text.startswith('/2 '))
def handle_mode_2(message):
    handle_show(message, mode="2")

@bot.message_handler(func=lambda message: message.text.startswith('/3 '))
def handle_mode_3(message):
    handle_show(message, mode="3")


@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = "List of available commands:\n"
    help_text += "/<mode> <username>  - Shows information about the osu player\n"
    help_text += "   <mode>: 0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania\n"
    help_text += "/help - Shows this list of commands\n"

    bot.send_message(message.chat.id, help_text)

bot.polling()