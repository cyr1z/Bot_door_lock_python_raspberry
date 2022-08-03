#!/usr/bin/python3
# chkconfig: - 98 02
# description:  Home telegram_bot
# processname: bot
import time
import telebot, json  # , logging
from settings import TOKEN, ADMIN #, AWAPIKEY, RP5CITY, LANGRP5, AWCITY, LANGAW, YRCITY
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import open_door, open_dog_door, old_message
# from weather_parsers import get_rp5_weather_summary

from lib import sticker, words

# forecast = Accuweather(AWCITY, AWAPIKEY, LANGAW)
# logging.basicConfig(filename="/home/pi/App/BotDoorLock/bot.log",
# level=logging.DEBUG)

bot = telebot.TeleBot(TOKEN)
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
keyboard1.row(" 🔑 Открывай", "🌈 Погода")
keyboard1.add("🐕 Выпустить собаку", "👁 Кто там")
try:
    with open("./data.json", "r") as read_file:
        data = json.load(read_file)
except FileNotFoundError:
    data = {"users": [], "rejected_users": []}


def main():
    @bot.message_handler(commands=["start"])
    def start_message(message):
        yes_no_kb = InlineKeyboardMarkup(row_width=2)
        yn_buttons = [
            InlineKeyboardButton(text="✅ Да", callback_data=message.chat.id),
            InlineKeyboardButton(text="❌ Нет", callback_data=11),
        ]
        yes_no_kb.add(*yn_buttons)

        if str(message.chat.id) in data["users"]:
            bot.send_sticker(message.chat.id, sticker["start"], reply_markup=keyboard1)

        else:
            if str(message.chat.id) not in data["rejected_users"]:
                bot.send_sticker(message.chat.id, sticker["what"])
                bot.send_message(
                    ADMIN,
                    f"Добавить пользователя "
                    f"{message.chat.first_name} "
                    f"{message.chat.last_name}?",
                    reply_markup=yes_no_kb,
                )

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if str(message.chat.id) in data["users"] and not old_message(message.date):
            if "открывай" in message.text.lower():
                open_door()
                bot.send_sticker(message.chat.id, sticker["hi"])

            elif "выпустить" in message.text.lower():
                open_dog_door()
                bot.send_sticker(message.chat.id, sticker["dog"])

            elif "кто" in message.text.lower():
                time_int = int(time.time())
                bot.send_photo(
                    message.chat.id,
                    f"https://cctv-frame.zolotarev.pp.ua/screen?img={time_int}.jpg",
                )
            #                bot.send_video(message.chat.id, 'https://cctv-frame.zolotarev.pp.ua/gif')

            elif "погода" in message.text.lower():
                # weather_message: str = get_rp5_weather_summary(RP5CITY, LANGRP5)
                # bot.send_message(message.chat.id, weather_message)
                time_int = int(time.time())
                bot.send_photo(
                    message.chat.id,
                    f"https://wttr.in/Kharkiv_pqQFn_lang=ru.png?t={time_int}",
                )
            else:
                print(message.text)

    @bot.message_handler(content_types=["sticker"])
    def sticker_id(message):
        print(message)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.data != "11":
            data["users"].append(call.data)
            try:
                with open("data.json", "w") as write_file:
                    json.dump(data, write_file)
                    bot.send_message(ADMIN, f"Добавил {call.data}")
                    bot.send_sticker(
                        call.data, sticker["start"], reply_markup=keyboard1
                    )
            except Exception as e:
                # logging.exception("Exception occurred")
                bot.send_message(ADMIN, str(e))

        else:
            data["rejected_users"].append(call.data)
            try:
                with open("data.json", "w") as write_file:
                    json.dump(data, write_file)
                    bot.send_message(ADMIN, "Отбой")

            except Exception as e:
                # logging.exception("Exception occurred")
                bot.send_message(ADMIN, str(e))

    bot.polling()


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        # logging.exception("Exception occurred")
        # logging.error(e)
        pass
