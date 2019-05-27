from values import*
import requests
import MySQLdb


# Получает и преобразовывает json данные с коинмаркеткап
def json_recipient():
    json_response = requests.get(currency_url)
    currency_data = json_response.json()
    return currency_data


# Возвращает список валют типа /BTC, /ETH etc
def currency_list():
    currency_data = json_recipient()
    all_coins = [i[9], ]
    for element in currency_data:
        all_coins.append(" /" + element['symbol'])
    return all_coins


# Возвращает значения переданной валюты с коинмаркеткап
def currency_values(cur, currency_data):
    for element in currency_data:
        if element['symbol'].lower() == cur.lower() \
                or element['id'].lower() == cur.lower() or element['name'].lower() == cur.lower():
            return element

# Формирует строковый ответ при срабатывании сигнала
def check_target_answer(row, i_number, emoji, cur_value, cur_value_change):
    answer = i[4] + emoji + row[4] + " " + cur_value_change + i[5] + str(row[2]) + i[i_number] \
             + i[6] + i[7] + " <b>" + row[4] + "</b> " + \
             " now:\n<b>                                    \U000025AA" + cur_value + i[8] + "</b>"
    return answer


####################MYSQL#####################
# добавляет запись в users, увеличивая значение пользователя в amount на единицу
def bd_users_insert(message, target, tar_type, currency):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    name = str(message.from_user.id)

    cursor.execute("SELECT * FROM amount WHERE name = %s", (name,))

    row = cursor.fetchone()
    amount = row[1]
    amount += 1
    cursor.execute("UPDATE amount SET amount = %s WHERE name = %s", (str(amount), name))
    cursor.execute("INSERT INTO users VALUES(0,%s,%s,%s,%s,%s)", (name, target, tar_type, currency, message.date))
    conn.close()


# проверяет amount на наличие пользователя, добавляя запись в случае его отсутствия, и превышение им лимита
def bd_amount_check(name):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("SELECT * FROM amount WHERE name = %s", (name,))

    row = cursor.fetchone()

    try:
        amount = row[1]
    except TypeError:
        cursor.execute("INSERT INTO amount VALUES(%s, 0)", (name,))
        conn.close()
        return True

    if amount > max_amount:
        conn.close()
        return False
    else:
        conn.close()
        return True


def db_amount_subtraction(name):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("SELECT * FROM amount WHERE name = %s", (name,))
    row = cursor.fetchone()
    amount = row[1] - 1
    cursor.execute("UPDATE amount SET amount = %s WHERE name = %s", (str(amount), name))
    conn.close()


def db_user_targets(name):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    user_targets = cursor.fetchall()
    conn.close()
    return user_targets


def db_users_delete(user_id):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("DELETE FROM users WHERE id = %s", (str(user_id),))
    conn.close()
    if cursor.rowcount == 0:
        return False
    else:
        return True
