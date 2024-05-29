# Импорт библиотек
import os
import time
import traceback
import sqlite3

from database.config import token_bot
from scripts.demotivator import mem_ramka
from scripts.send_mem import send_mem
from scripts.text_up import text_up
from scripts.text_down import text_down

try:
    import cowsay
    import requests
    import telebot
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as e:
    os.system("pip install cowsay")
    os.system("pip install pyTelegramBotAPI")
    os.system("pip install pillow")
    os.system("pip install requests")
    import telebot
    import cowsay
    import requests
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

bot = telebot.TeleBot(token_bot)  # токен бота из BotFather

print(cowsay.get_output_string('turtle', "Бот запущен!"))  # это для проверки что бот запустился
print(" " * 10, "##" * 12)
print("", end='\n')


@bot.message_handler(commands=['start'])  # запуск бота
def start(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()
    # Выполнение запроса и получение всех результатов в виде списка
    result = cur.execute("""SELECT id FROM id""").fetchall()
    id_list = [elem[0] for elem in result]
    chatid = message.chat.id  # переменная для сохранения айди чата

    # добавляем айди и имя в базу данных
    if chatid not in id_list:
        cur.execute(
            f'''INSERT INTO id (id, name, key) VALUES({chatid}, '{message.from_user.first_name}', 'defolt') ''')
        cur.execute(
            f'''INSERT INTO users_mem (id) VALUES({chatid}) ''')
        con.commit()
    bot.send_message(chatid,
                     text=f'Хаю хай с вами {message.from_user.first_name}!\n\n'
                          f'При помощи команды /mem_create ты сможешь создать мем!\n\n'
                          f'А также вспомни классику и создай демотиватор /demotivator!')

    pic = open("database/example/all.jpg", 'rb')
    bot.send_photo(message.chat.id, photo=pic, caption="Вот пример")


@bot.message_handler(commands=['mem_create'])
def mem_create(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    result = cur.execute("""SELECT id FROM users_mem""").fetchall()
    id_list = [elem[0] for elem in result]
    chatid = message.chat.id  # переменная для сохранения айди чата

    # добавляем айди и имя в базу данных
    if chatid not in id_list:
        cur.execute(
            f'''INSERT INTO users_mem (id) VALUES({message.chat.id}) ''')
        con.commit()
    else:
        cur.execute(f'''UPDATE users_mem SET text_up = NULL WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE users_mem SET text_down = NULL WHERE id = {message.chat.id} ''')
        con.commit()

    bot.send_message(message.chat.id, text='Пришли картинку для мема')

    cur.execute(f'''UPDATE id SET key = 'pic' WHERE id = {message.chat.id} ''')
    con.commit()


@bot.message_handler(commands=['demotivator'])
def demotivator(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    bot.send_message(message.chat.id, text='Пришли картинку для демотиватора')

    result = cur.execute("""SELECT id FROM users_demotivator""").fetchall()
    id_list = [elem[0] for elem in result]
    chatid = message.chat.id  # переменная для сохранения айди чата

    # добавляем айди и имя в базу данных
    if chatid not in id_list:
        cur.execute(
            f'''INSERT INTO users_demotivator (id) VALUES({message.chat.id}) ''')
        con.commit()
    else:
        cur.execute(f'''UPDATE users_demotivator SET text__demotivator_up = NULL WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE users_demotivator SET text__demotivator_down = NULL WHERE id = {message.chat.id} ''')
        con.commit()

    pic = open("database/example/demotivator.jpg", 'rb')
    bot.send_photo(message.chat.id, photo=pic, caption="Если ты не знаешь, что такое демотиватор, держи пример")

    cur.execute(f'''UPDATE id SET key = 'demotivator' WHERE id = {message.chat.id} ''')
    con.commit()


@bot.message_handler(commands=['no_text'])
def no_text(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    flag = cur.execute(f'''SELECT key FROM id WHERE id = {message.chat.id}''').fetchone()[0]

    if flag == "text_up":
        cur.execute(f'''UPDATE id SET key = 'text_down' WHERE id = {message.chat.id} ''')
        con.commit()

        cur.execute(f'''UPDATE users_mem SET text_up = NULL WHERE id = {message.chat.id} ''')
        con.commit()

        pic = open("database/example/down.jpg", 'rb')
        bot.send_photo(message.chat.id, photo=pic,
                       caption='Тогда отправь текст, который будет снизу, иначе пропиши /no_text\n'
                               '\nНапример\n\n')
    elif flag == "text_down":
        cur.execute(f'''UPDATE users_mem SET text_down = NULL WHERE id = {message.chat.id} ''')
        con.commit()

        send_mem(message.chat.id, "mem")

    elif flag == "text__demotivator_up":
        cur.execute(f'''UPDATE id SET key = 'text__demotivator_down' WHERE id = {message.chat.id} ''')
        con.commit()

        cur.execute(f'''UPDATE users_demotivator SET text__demotivator_up = "" WHERE id = {message.chat.id} ''')
        con.commit()

        pic = open("database/example/demotivator_down.jpg", 'rb')
        bot.send_photo(message.chat.id, photo=pic,
                       caption='Тогда отправь текст, который будет снизу, иначе пропиши /no_text\n'
                               '\nНапример\n\n')

    elif flag == "text__demotivator_down":
        cur.execute(f'''UPDATE users_demotivator SET text__demotivator_down = "" WHERE id = {message.chat.id} ''')
        con.commit()

        name = cur.execute(f'''SELECT pic FROM users_demotivator WHERE id = {message.chat.id}''').fetchone()[0]
        mes_up = (cur.execute(f'''SELECT text__demotivator_up FROM users_demotivator 
            WHERE id = {message.chat.id}''').fetchone())[0]
        mes_down = (cur.execute(f'''SELECT text__demotivator_down FROM users_demotivator 
            WHERE id = {message.chat.id}''').fetchone())[0]
        if mem_ramka(name, mes_up, mes_down):
            send_mem(message.chat.id, "demotivator")


@bot.message_handler(content_types=['text'])
def text_message(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    flag = cur.execute(f'''SELECT key FROM id WHERE id = {message.chat.id}''').fetchone()[0]

    if flag == "text_up":
        if len(message.text) > 255:
            bot.send_message(message.chat.id, text='Не должно превышать 255 символов!')
        else:
            name = cur.execute(f'''SELECT pic FROM users_mem WHERE id = {message.chat.id}''').fetchone()[0]
            texttt = message.text
            pic_name = text_up(name, texttt)
            cur.execute(f'''UPDATE users_mem SET pic = '{pic_name}' WHERE id = {message.chat.id} ''')
            cur.execute(f'''UPDATE users_mem SET mem = '{pic_name}' WHERE id = {message.chat.id} ''')
            cur.execute(f'''UPDATE id SET key = 'text_down' WHERE id = {message.chat.id} ''')
            con.commit()

            pic = open("database/example/down.jpg", 'rb')
            bot.send_photo(message.chat.id, photo=pic,
                           caption='Отправь текст, который будет снизу, иначе пропиши /no_text\n'
                                   'Важно! Не больше 255 символов!\n'
                                   '\nНапример:')
    elif flag == "text_down":
        if len(message.text) > 255:
            bot.send_message(message.chat.id, text='Не должно превышать 255 символов!')
        else:
            name = cur.execute(f'''SELECT pic FROM users_mem WHERE id = {message.chat.id}''').fetchone()[0]
            texttt = message.text
            pic_name = text_down(name, texttt)
            cur.execute(f'''UPDATE users_mem SET mem = '{pic_name}' WHERE id = {message.chat.id} ''')
            con.commit()
            send_mem(message.chat.id, "mem")

    elif flag == "text__demotivator_up":
        if len(message.text) > 255:
            bot.send_message(message.chat.id, text='Не должно превышать 255 символов!')
        else:
            cur.execute(
                f'''UPDATE users_demotivator SET text__demotivator_up = '{message.text}' WHERE id = {message.chat.id} ''')
            con.commit()

            cur.execute(f'''UPDATE id SET key = 'text__demotivator_down' WHERE id = {message.chat.id} ''')
            con.commit()

            pic = open("database/example/demotivator_down.jpg", 'rb')
            bot.send_photo(message.chat.id, photo=pic, caption='Отправь текст, который будет пониже,'
                                                               ' иначе пропиши /no_text\n'
                                                               'Важно! Не больше 255 символов!\n'
                                                               '\nНапример:')
    elif flag == "text__demotivator_down":
        if len(message.text) > 255:
            bot.send_message(message.chat.id, text='Не должно превышать 255 символов!')
        else:
            cur.execute(
                f'''UPDATE users_demotivator SET text__demotivator_down = '{message.text}' WHERE id = {message.chat.id} ''')
            con.commit()

        name = cur.execute(f'''SELECT pic FROM users_demotivator WHERE id = {message.chat.id}''').fetchone()[0]
        mes_up = (cur.execute(f'''SELECT text__demotivator_up FROM users_demotivator 
            WHERE id = {message.chat.id}''').fetchone())[0]
        mes_down = (cur.execute(f'''SELECT text__demotivator_down FROM users_demotivator 
            WHERE id = {message.chat.id}''').fetchone())[0]
        if mem_ramka(name, mes_up, mes_down):
            send_mem(message.chat.id, "demotivator")


@bot.message_handler(content_types=['photo'])
def pic_message(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    chatid = message.chat.id  # переменная для сохранения айди чата

    flag = cur.execute(f'''SELECT key FROM id WHERE id = {chatid}''').fetchone()[0]

    if flag == "pic":
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'database/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        im = Image.open(new_file.name)
        position = (0.05 * im.width, im.height - im.height * 0.2)
        font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=10, encoding="unic")
        draw_text = ImageDraw.Draw(im)
        draw_text.text(
            position,
            '@pizdza_memcreator_bot',
            font=font,
            fill='#1C0606'
        )
        os.remove(new_file.name)
        im.save(new_file.name, quality=95)

        cur.execute(f'''UPDATE users_mem SET pic = '{new_file.name}' WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE id SET key = 'text_up' WHERE id = {message.chat.id} ''')
        con.commit()

        pic = open("database/example/up.jpg", 'rb')
        bot.send_photo(chatid, photo=pic, caption='Отправь текст, который будет сверху, иначе пропиши /no_text\n'
                                                  'Важно! Не больше 255 символов!\n'
                                                  '\nВыглядеть будет примерно так:\n\n')
    elif flag == "demotivator":
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'database/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        im = Image.open(new_file.name)
        position = (0.05 * im.width, im.height - im.height * 0.2)
        font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=10, encoding="unic")
        draw_text = ImageDraw.Draw(im)
        draw_text.text(
            position,
            '@pizdza_memcreator_bot',
            font=font,
            fill='#1C0606'
        )
        os.remove(new_file.name)
        im.save(new_file.name, quality=95)

        cur.execute(f'''UPDATE users_demotivator SET pic = '{new_file.name}' WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE id SET key = 'text__demotivator_up' WHERE id = {message.chat.id} ''')
        con.commit()

        pic = open("database/example/demotivator_up.jpg", 'rb')
        bot.send_photo(chatid, photo=pic, caption='Отправь текст, который будет выше, иначе пропиши /no_text\n'
                                                  'Важно! Не больше 255 символов!\n'
                                                  '\nВыглядеть будет примерно так:\n\n')
    elif flag == "defolt":
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'database/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        im = Image.open(new_file.name)
        position = (0.05 * im.width, im.height - im.height * 0.2)
        font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=10, encoding="unic")
        draw_text = ImageDraw.Draw(im)
        draw_text.text(
            position,
            '@pizdza_memcreator_bot',
            font=font,
            fill='#1C0606'
        )
        os.remove(new_file.name)
        im.save(new_file.name, quality=95)

        cur.execute(f'''UPDATE users_mem SET pic = '{new_file.name}' WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE users_demotivator SET pic = '{new_file.name}' WHERE id = {message.chat.id} ''')
        con.commit()
        keyboard = telebot.types.InlineKeyboardMarkup()
        url_button1 = telebot.types.InlineKeyboardButton(text="мем", callback_data="mem")
        url_button2 = telebot.types.InlineKeyboardButton(text="демотиватор", callback_data="demotivator")
        keyboard.add(url_button1, url_button2)

        bot.send_message(chatid,
                         text=f'Выберите, что хотите сделать', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    chatid = call.message.chat.id  # переменная для сохранения айди чата

    if call.data == "mem":

        cur.execute(f'''UPDATE id SET key = 'text_up' WHERE id = {call.message.chat.id} ''')
        con.commit()

        pic = open("database/example/up.jpg", 'rb')
        bot.send_photo(chatid, photo=pic, caption='Отправь текст, который будет сверху, иначе пропиши /no_text\n'
                                                  'Важно! Не больше 255 символов!\n'
                                                  '\nВыглядеть будет примерно так:\n\n')
    elif call.data == "demotivator":
        cur.execute(f'''UPDATE id SET key = 'text__demotivator_up' WHERE id = {call.message.chat.id} ''')
        con.commit()

        pic = open("database/example/demotivator_up.jpg", 'rb')
        bot.send_photo(chatid, photo=pic, caption='Отправь текст, который будет выше, иначе пропиши /no_text\n'
                                                  'Важно! Не больше 255 символов!\n'
                                                  '\nВыглядеть будет примерно так:\n\n')


def telegram_polling():
    try:
        bot.polling()
    except requests.exceptions.ReadTimeout:
        traceback_error_string = traceback.format_exc()
        with open("Error.Log", "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime("%c") + "\r\n<<ERROR polling>>\r\n" + traceback_error_string
                         + "\r\n<<ERROR polling>>")
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


if __name__ == '__main__':
    telegram_polling()
