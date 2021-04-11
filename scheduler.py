import os
import logging
import sqlite3
import schedule
import requests

logging.basicConfig(format='%(levelname)s[%(asctime)s]: %(message)s',
                    level=logging.INFO)

BOT_ID = os.getenv('BOT_ID', None)
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_ID}'

STAT_API_URL = os.getenv('ATS_STAT_API_URL', None)
STAT_API_TOKEN = os.getenv('ATS_STAT_API_TOKEN', None)


def run_query(sql_query):
    with sqlite3.connect('db/bot.sqlite') as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except Exception as e:
            print(e)

        result = cursor.fetchall()
        return result


def api_request(url, params, headers):
    logging.info(f'[REQUEST]: {url} {params}')
    res = requests.get(url, params=params, headers=headers)
    logging.info(f'[RESPONSE]: status - {res.status_code}')
    return res.json()


def stat_api_call():
    data = api_request(STAT_API_URL, None, {'BOT-AUTH': STAT_API_TOKEN})
    not_used = list(filter(lambda x: not x['last_used'], data))

    result = 'Не было звонков за послений час у брендов:\n'
    for item in not_used:
        result += f'\t\t- {item["name"]}\n'
    return result


def main():
    logging.info('[SCHEDULE]: Start')
    text = stat_api_call()
    users = run_query('SELECT chat_id FROM users')

    logging.info(f'[SCHEDULE]: Send for {len(users)} users')
    for user in users:
        chat_id = user[0]
        api_request(f'{TELEGRAM_API_URL}/sendMessage',
                    {'chat_id': chat_id, 'text': text}, None)


schedule.every(30).minutes.do(main)

if __name__ == '__main__':
    print('Scheduler started')
    while True:
        schedule.run_pending()
