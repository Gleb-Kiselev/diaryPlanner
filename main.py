import telebot
from telebot import types
from datetime import datetime, date
import time
import conversation
import threading
import markdown


token = '6816422069:AAEG4Q1QrTZrrmldB2F5IHrMjHnU1PSgRII'

task_manager = dict()

bot = telebot.TeleBot(token, parse_mode="MARKDOWN")


@bot.message_handler(commands=['start', 'help'])
def start(message):
    task_manager[message.chat.id] = conversation.TaskManager()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Записать новое дело")
    btn2 = types.KeyboardButton("Получить список всех дел")
    btn3 = types.KeyboardButton("Получить дела на сегодня")
    btn4 = types.KeyboardButton("Получить дела на завтра")
    btn5 = types.KeyboardButton("Удалить дело")

    markup.add(btn1, btn3, btn2, btn4, btn5)
    with open('start_message.md', 'r')  as file:
        text = file.read()
    bot.send_message(message.chat.id, text, reply_markup=markup) #format(message.from_user)


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "Записать новое дело"):

        mesg = bot.send_message(message.chat.id, text="Введите, что вам нужно сделать и когда")
        bot.register_next_step_handler(mesg, adding_task)
    elif message.text == "Получить дела на сегодня":

        tasks_list = task_manager[message.chat.id].get_tasks_for_today()
        today_tasks = '\n'.join(map(str, tasks_list))
        bot.send_message(message.chat.id,
                         today_tasks if len(today_tasks) > 0 else "На сегодня ничего не запланировано.")

    elif message.text == "Получить список всех дел":
        tasks_list = task_manager[message.chat.id].get_all_tasks()
        all_tasks = '\n'.join(map(str, tasks_list))
        bot.send_message(message.chat.id,
                         all_tasks if len(all_tasks) > 0 else "Ничего не запланировано")

    elif message.text == "Получить дела на завтра":
        tasks_list = task_manager[message.chat.id].get_tasks_for_tomorrow()
        today_tasks = '\n'.join(map(str, tasks_list))
        bot.send_message(message.chat.id, today_tasks if len(today_tasks) > 0 else "На завтра ничего не запланировано.")

    elif message.text == "Удалить дело":


        tasks_list = list(map(str, task_manager[message.chat.id].get_all_tasks()))
        all_tasks = ''
        for count, elem in enumerate(tasks_list):
            all_tasks += (f'{count + 1}. {elem} \n')

        if len(tasks_list) > 0:
            bot.send_message(message.chat.id,
                         all_tasks)
            mesg = bot.send_message(message.chat.id, text="Введите номер задачи, которую нужно удалить")
            bot.register_next_step_handler(mesg, deleting_task)
        else:
            bot.send_message(message.chat.id, "Ничего не запланировано")
    else:
        bot.send_message(message.chat.id, text="Выберите одну из предложенных команд")


def adding_task(message):
    task = conversation.create_task(message.text.lower())
    if task is None:
        bot.send_message(message.chat.id,
                         text="Что-то пошло не так, убедитесь, что вы ввели задачу в правильном формате")
    else:
        task_manager[message.chat.id].add_task(task)
        bot.send_message(message.chat.id, text="Дело успешно добавлено")


def deleting_task(message):
    tasks_list = task_manager[message.chat.id].get_all_tasks()
    if int(message.text) - 1 > len(tasks_list):
        raise ValueError
    else:
        task_manager[message.chat.id].remove_task(int(message.text) - 1)
        bot.send_message(message.chat.id, text="Дело успешно удалено")

class ReminderHandler():
    def __init__(self):
        self.actual_date = date.today()
        self.today_reminder_sent = False
        self.tomorrow_reminder_sent = False

    # Метод для отправки напоминаний.
    def update(self):
        hour = datetime.now().hour

        # Проверяем, сменился ли день.
        if date.today() > self.actual_date:
            self.actual_date = date.today()
            self.today_reminder_sent = False
            self.tomorrow_reminder_sent = False
            filter_tasks()

        # Проверяем, нужно ли отправить напоминание о сегодняшних задачах.
        if self.today_reminder_sent is False and hour >= 9:
            self.today_reminder_sent = True
            for chat_id in task_manager.keys():
                tasks_list = task_manager[chat_id].get_tasks_for_today()
                today_tasks = '\n'.join(map(str, tasks_list))
                bot.send_message(chat_id,
                                 today_tasks if len(today_tasks) > 0 else "На сегодня ничего не запланировано.")

        # Проверяем, нужно ли отправить напоминание о завтрашних задачах.
        if self.tomorrow_reminder_sent is False and hour >= 19:
            self.tomorrow_reminder_sent = True
            for chat_id in task_manager.keys():
                tasks_list = task_manager[chat_id].get_tasks_for_tomorrow()
                today_tasks = '\n'.join(map(str, tasks_list))
                bot.send_message(chat_id,
                                 today_tasks if len(today_tasks) > 0 else "На завтра ничего не запланировано.")


def filter_tasks():
    for task_man in task_manager.values():
        task_man.remove_outdated_tasks()

def run_reminder():
    reminder_handler = ReminderHandler()
    while True:
        reminder_handler.update()
        time.sleep(3600)


def start_reminder():
    t = threading.Thread(target=run_reminder)
    t.daemon = True
    t.start()

start_reminder()

bot.polling(none_stop=True)
