import MySQLdb
import values


# добавляет запись в users !!!ДОПИСАТЬ ПРОВЕРКУ по базе amount. Если пользователя нет, он добавляется.
# Если есть, смотрится по количеству записей. При превышении users_insert возвращает сообщение об этом!!!
def users_insert(message, target, tar_type):
    conn = MySQLdb.connect(host=values.host, port=values.port, user=values.user, passwd=values.passwd, db=values.db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("INSERT INTO users VALUES(0,%s,%s,%s,%s)",
                   (str(message.from_user.id), target, tar_type, message.date)
                   )
    conn.close()


# функция циклической проверки соответсвий в БД
def check_target(currency_data):
    conn = MySQLdb.connect(host=values.host, port=values.port, user=values.user, passwd=values.passwd, db=values.db)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("SELECT * FROM users")

    while True:
        row = cursor.fetchone()
        if row:
            bot.send_message(row[1], row[2])
            print(row[1], row[2])
        else:
            break

    conn.close()
