import os
import telegram
import datetime as dt
from git import Repo

from secrets import conf


def make_dir(root):
    path = f'{root}/{dt.datetime.today().strftime("%Y-%m-%d")}'
    os.makedirs(path, exist_ok=True)

    return path


def update_repo(root):
    repo = Repo(root)
    repo.git.add('*')
    repo.index.commit('Auto commit')

    origin = repo.remote(name='origin')

    return origin.push()


def send_notification(func):
    def wrapper():
        bot = telegram.Bot(conf.get('token'))
        chat_id = conf.get('chat_id')

        try:
            func()
            text = 'Option data collected!'
        except Exception as e:
            text = 'Something went wrong: ' + str(e)
            raise e

        bot.send_message(chat_id=chat_id, text=text)

    return wrapper


if __name__ == '__main__':
    update_repo('./data')
