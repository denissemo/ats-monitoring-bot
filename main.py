import os
import sqlite3

import telebot

BOT_ID = os.getenv('BOT_ID', None)

bot = telebot.TeleBot(BOT_ID)


def run_query(sql_query):
    with sqlite3.connect('db/bot.sqlite') as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except Exception as e:
            print(e)

        result = cursor.fetchall()
        return result


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        print(f'Subscribe user: {message.chat.id}')
        run_query(f'''
            INSERT INTO users (chat_id) VALUES ({message.chat.id})
        ''')

        bot.send_message(message.chat.id,
                         'Вы подписались на оповещения!\nОтписаться: /unsubscribe')
    else:
        bot.send_message(message.chat.id,
                         'I refuse to work in groups')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    print(f'Unsubscribe user: {message.chat.id}')
    run_query(f'DELETE FROM users WHERE chat_id = {message.chat.id}')
    bot.send_message(message.chat.id, 'Вы отписались от оповещений!')


if __name__ == '__main__':
    run_query('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER NOT NULL unique 
    )''')

    while True:
        try:
            print('Bot started')
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            break
