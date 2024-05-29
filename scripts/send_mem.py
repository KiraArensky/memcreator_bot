from database.config import token_bot
import telebot

import os
import sqlite3

bot = telebot.TeleBot(token_bot)  # токен бота из BotFather


def send_mem(user_id, mode):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    cur.execute(f'''UPDATE id SET key = 'defolt' WHERE id = {user_id} ''')
    con.commit()

    if mode == "mem":
        pic_name = cur.execute(f'''SELECT pic FROM users_mem WHERE id = {user_id}''').fetchone()[0]
    elif mode == "demotivator":
        pic_name = cur.execute(f'''SELECT pic FROM users_demotivator WHERE id = {user_id}''').fetchone()[0]
    pic = open(pic_name, 'rb')

    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text="Сообщить об ошибке", url="https://t.me/kshi_rar")
    keyboard.add(url_button)

    bot.send_photo(user_id, photo=pic, caption="Готово! @pizdza_memcreator_bot", reply_markup=keyboard)

    cur.execute(f"""SELECT name FROM id WHERE id = {user_id}""").fetchall()[0][0]

    pic.close()

    os.remove(pic_name)
