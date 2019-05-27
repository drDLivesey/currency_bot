import MySQLdb
import telebot
from telebot import types
import time
import requests
import json
import re
from functions import*
from values import*
from threading import Timer
import codecs
import cherrypy

WEBHOOK_HOST = host
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (bot_key)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


bot = telebot.TeleBot(bot_key)
step = {}
target_type = {}
currency = {}
user_currency_values = {}


def send(chat_id, text):
    bot.send_message(chat_id, text)


# рекурсивно ищем сигналы в базе и сообщаем их пользователю
def check_target():
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("SELECT * FROM users")

    while True:
        row = cursor.fetchone()
        currency_data = json_recipient()
        if row:
            cur_values = currency_values(row[4], currency_data)
            if cur_values is not None:
                tar_type = int.from_bytes(row[3], 'big')

                if tar_type == 0:
                    cur_value = str(round(float(cur_values['price_usd']), 2))
                    cur_value_change = "+" + cur_values['percent_change_1h'] + "%"
                    if row[2] < float(cur_values['percent_change_1h']):
                        bot.send_message(row[1], check_target_answer(row, 0, i[18], cur_value, cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 1:
                    cur_value = str(round(float(cur_values['price_usd']), 2))
                    cur_value_change = "+" + cur_values['percent_change_24h'] + "%"
                    if row[2] < float(cur_values['percent_change_24h']):
                        bot.send_message(row[1], check_target_answer(row, 1, i[18], cur_value, cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 2:
                    cur_value = str(round(float(cur_values['price_usd']), 2))
                    cur_value_change = "+" + cur_values['percent_change_7d'] + "%"
                    if row[2] < float(cur_values['percent_change_7d']):
                        bot.send_message(row[1], check_target_answer(row, 2, i[18],  cur_value, cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 3:
                    cur_value = str(round(float(cur_values['price_usd']), 2))
                    cur_value_change = cur_values['percent_change_1h'] + "%"
                    if row[2] > float(cur_values['percent_change_1h']):
                        bot.send_message(row[1], check_target_answer(row, 0, i[17], cur_value, cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 4:
                    cur_value = str(round(float(cur_values['price_usd']), 2))
                    cur_value_change = cur_values['percent_change_24h'] + "%"
                    if row[2] > float(cur_values['percent_change_24h']):
                        bot.send_message(row[1], check_target_answer(row, 1, i[17], cur_value, cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 5:
                    cur_value = str(round(float(cur_values['price_usd']), 2))
                    cur_value_change = cur_values['percent_change_7d'] + "%"
                    if row[2] > float(cur_values['percent_change_7d']):
                        bot.send_message(row[1], check_target_answer(row, 2, i[17], cur_value, cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 6:
                    if row[2] < float(cur_values['price_usd']):
                        cur_value = round(float(cur_values['price_usd']), 2)
                        percent_change = float(cur_values['percent_change_1h'])
                        cur_value_change = "+" + str(round(cur_value * percent_change / (100 + percent_change), 2)) + i[8]

                        bot.send_message(row[1], check_target_answer(row, 8, i[18], str(cur_value), cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

                elif tar_type == 7:
                    if row[2] > float(cur_values['price_usd']):
                        cur_value = round(float(cur_values['price_usd']), 2)
                        percent_change = float(cur_values['percent_change_1h'])
                        cur_value_change = str(round(cur_value * percent_change / (100 + percent_change), 2)) + i[8]

                        bot.send_message(row[1], check_target_answer(row, 8, i[17], str(cur_value), cur_value_change)
                                         , parse_mode='HTML')
                        db_users_delete(row[0])
                        db_amount_subtraction(row[1])

        else:
            break

    conn.close()
    check_target_timer = Timer(10, check_target)
    check_target_timer.start()


# выводим информацию о возможностях бота для команд start и help
@bot.message_handler(commands=["start", "help", "h"])
def start_command_handler(message):
    send(message.from_user.id, h[0])


# выводим список из команд пользователя
@bot.message_handler(commands=["show"])
def start_command_handler(message):
    user_targets = db_user_targets(str(message.from_user.id))
    keyboard = types.InlineKeyboardMarkup()
    callback_button = {}

    try:
        user_targets[0]
        message_text = i[19]
        for row in user_targets:
            tar_type = int.from_bytes(row[3], 'big')
            if tar_type == 0 or tar_type == 3:
                target_type = i[0]
            elif tar_type == 1 or tar_type == 4:
                target_type = i[1]
            elif tar_type == 2 or tar_type == 5:
                target_type = i[2]
            else:
                target_type = i[3]

            button_text = row[4] + ": " + str(row[2]) + " " + target_type
            id_and_name = "id&name|" + str(row[0]) + "|" + str(row[1]) + "|" + button_text
            callback_button[row[0]] = types.InlineKeyboardButton(text=button_text, callback_data=id_and_name)
            keyboard.add(callback_button[row[0]])
    except IndexError:
        message_text = i[20]

    bot.send_message(message.from_user.id, text=message_text, reply_markup=keyboard, parse_mode='HTML')


@bot.message_handler(commands=["t"])
def t_command_handler(message):
    if bd_amount_check(message.from_user.id) is True:
        mes = message.text.split()
        if len(mes) == 1:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text=i[10], callback_data="cur_list")
            keyboard.add(callback_button)
            bot.send_message(message.from_user.id, t[0], reply_markup=keyboard)

            step[message.chat.id] = 1
    else:
        bot.send_message(message.from_user.id, t[4], parse_mode='HTML')


@bot.message_handler(commands=["c"])
def c_command_handler(message):
    mes = message.text.split()

    try:
        step.pop(message.chat.id)
    except KeyError:
        pass

    if len(mes) == 1:
        all_coins = currency_list()
        send(message.from_user.id, "".join(all_coins))

    else:
        recipient = message.chat.id
        cur = mes[1]
        cur_value = currency_values(cur, json_recipient())
        if cur_value is not None:
            send(recipient, str(round(float(cur_value['price_usd']), 2)))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    recipient = call.message.chat.id

    try:
        step[recipient]
    except KeyError:
        step[recipient] = 0

    if call.message:
        if call.data == "cur_list":
            all_coins = currency_list()
            send(recipient, "".join(all_coins))

        elif step[recipient] == 2:
            step[recipient] = 3
            if call.data == "1h":
                target_type[recipient] = 0b000
                send(recipient, t[2])
            elif call.data == "27h":
                target_type[recipient] = 0b001
                send(recipient, t[2])
            elif call.data == "7d":
                target_type[recipient] = 0b010
                send(recipient, t[2])
            elif call.data == "tar_line":
                target_type[recipient] = 0b110
                send(recipient, t[3])
            else:
                step[recipient] = 2

        else:
            id_and_name = call.data.split("|")
            if id_and_name[0] == "id&name":
                if db_users_delete(id_and_name[1]) is True:
                    print(2)
                    db_amount_subtraction(id_and_name[2])
                    answer = t[6] + id_and_name[3]
                    bot.send_message(recipient, answer, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    mes = message.text
    recipient = message.chat.id

    try:
        step[recipient]
    except KeyError:
        step[recipient] = 0

    if step[recipient] == 0:
        if mes[0] == '/':
            if recipient < 0:
                cur = mes[1:-16]
            else:
                cur = mes[1:]
            answer = currency_values(cur, json_recipient())
            if answer is not None:
                send(recipient, answer["price_usd"])
                print(recipient, " ", message.from_user.username, "\n ", answer["id"], ": ", answer["price_usd"])
        step.pop(recipient)

    elif step[recipient] == 1:
        cur = mes[1:]
        user_currency_values[recipient] = currency_values(cur, json_recipient())
        if user_currency_values[recipient] is not None:
            keyboard = types.InlineKeyboardMarkup()
            callback_button_1h = types.InlineKeyboardButton(text=i[0], callback_data="1h")
            callback_button_24h = types.InlineKeyboardButton(text=i[1], callback_data="27h")
            callback_button_7d = types.InlineKeyboardButton(text=i[2], callback_data="7d")
            callback_button_tar_line = types.InlineKeyboardButton(text=i[3], callback_data="tar_line")
            keyboard.add(callback_button_1h, callback_button_24h, callback_button_7d, callback_button_tar_line)
            bot.send_message(recipient, user_currency_values[recipient]["price_usd"] + "\n" + t[1], reply_markup=keyboard)

            step[recipient] = 2
            currency[recipient] = cur

    elif step[recipient] == 3:

        try:
            target = float(mes)

            if target < 0:
                if target_type[recipient] == 0b110:
                    send(recipient, i[14])
                    raise ValueError()
                elif target_type[recipient] == 0b000:
                    target_type[recipient] = 0b011
                elif target_type[recipient] == 0b001:
                    target_type[recipient] = 0b100
                elif target_type[recipient] == 0b010:
                    target_type[recipient] = 0b101

            elif target_type[recipient] == 0b110:
                if target < float(user_currency_values[recipient]["price_usd"]):
                    target_type[recipient] = 0b111

            bd_users_insert(message, target, target_type[recipient], currency[recipient])
            print(target, target_type[recipient])
            step.pop(recipient)
            target_type.pop(recipient)
            currency.pop(recipient)
            user_currency_values.pop(recipient)
            bot.send_message(recipient, t[5], parse_mode='HTML')
        except ValueError:
            step[recipient] = 3


check_target()


#bot.polling(none_stop=True, interval=0)

# Ставим вебхук
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

 # Запускаем вебхук
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

