#!/usr/bin/python3
# chkconfig: - 98 02                        
# description:  Home telegram_bot
# processname: bot
import telebot, json #, logging
from settings import TOKEN, ADMIN, AWAPIKEY, RP5CITY, LANGRP5, AWCITY, LANGAW, YRCITY
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import open_door, pin_clean, open_dog_door, old_message
from weather_parsers import get_rp5_weather_summary, get_own_measure, YrNow #, Accuweather
from lib import sticker, words

#forecast = Accuweather(AWCITY, AWAPIKEY, LANGAW)
#logging.basicConfig(filename="/home/pi/App/BotDoorLock/bot.log", level=logging.DEBUG)

bot = telebot.TeleBot(TOKEN)
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
keyboard1.row(' 🔑 Открывай', '🌈 Погода')
keyboard1.add('🐕 Выпустить собаку', '👁 Кто там')
try:
    with open("/home/pi/App/BotDoorLock/data.json", "r") as read_file:
        data = json.load(read_file)
except FileNotFoundError:
    data = {'users': [], 'rejected_users': []}
    #logging.error('no open data.json')


def main():
    
    @bot.message_handler(commands=['start'])
    def start_message(message):
        #logging.debug(f'start from {message.chat.first_name} {message.chat.last_name}')
        yes_no_kb = InlineKeyboardMarkup(row_width=2)
        yn_buttons = [InlineKeyboardButton(text='✅ Да', callback_data=message.chat.id),
                      InlineKeyboardButton(text='❌ Нет', callback_data=11)]
        yes_no_kb.add(*yn_buttons)

        if str(message.chat.id) in data['users']:
            bot.send_sticker(message.chat.id, sticker['start'], reply_markup=keyboard1)

        else:
            if str(message.chat.id) not in data['rejected_users']:
                bot.send_sticker(message.chat.id, sticker['what'])
                bot.send_message(ADMIN,
                                 f'Добавить пользователя {message.chat.first_name}'\
                                 f'{message.chat.last_name}?',
                                 reply_markup=yes_no_kb)

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if str(message.chat.id) in data['users'] and not old_message(message.date):
            if 'открывай' in message.text.lower():
                open_door()
                bot.send_sticker(message.chat.id, sticker['hi'])
                pin_clean()

            elif 'выпустить' in message.text.lower():
                open_dog_door()
                bot.send_sticker(message.chat.id, sticker['dog'])
                pin_clean()

            elif 'кто' in message.text.lower():
                bot.send_message(message.chat.id, 'пока не вижу')

            elif 'погода' in message.text.lower():
                yr_now = YrNow(YRCITY)
                #forecast.refresh()
                weather_message: str = get_rp5_weather_summary(RP5CITY, LANGRP5)
                weather_message += get_own_measure()
                weather_message += "\n"
                weather_message += str(yr_now)
                #weather_message += str(forecast)
                bot.send_message(message.chat.id, weather_message)

            else:
                print(message.text)

    @bot.message_handler(content_types=['sticker'])
    def sticker_id(message):
        print(message)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.data != '11':
            data['users'].append(call.data)
            try:
                with open("data.json", "w") as write_file:
                    json.dump(data, write_file)
                    bot.send_message(ADMIN, 'Добавил')
                    bot.send_sticker(call.data, sticker['start'], reply_markup=keyboard1)
            except Exception as e:
                #logging.exception("Exception occurred")
                bot.send_message(ADMIN, str(e))

        else:
            data['rejected_users'].append(call.data)
            try:
                with open("data.json", "w") as write_file:
                    json.dump(data, write_file)
                    bot.send_message(ADMIN, 'Отбой')

            except Exception as e:
                #logging.exception("Exception occurred")
                bot.send_message(ADMIN, str(e))

    pin_clean()
    bot.polling()


if __name__ == '__main__':
    try:
        main()
        pin_clean()
    except Exception as e:
        #logging.exception("Exception occurred")
        #logging.error(e)
        pin_clean()
