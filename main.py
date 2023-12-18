import telebot
from telebot import types
from datetime import datetime, date
import time
import conversation
import threading
from settings import TG_TOKEN

task_manager = dict()

bot = telebot.TeleBot(TG_TOKEN, parse_mode="MARKDOWN")


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    """
    Функция для ответа на команды \start, \help
    Отправляет стартовое сообщение из файла "start_message.md"
    Создаёт кнопки для работы бота
    "Записать новое дело"
    "Получить дела на сегодня"
    "Получить список всех задач"
    "Получить дела на завтра"
    "Удалить дело"
    args:  message -- telebot.types.Message
    """

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
    bot.send_message(message.chat.id, text, reply_markup=markup)  # format(message.from_user)


@bot.message_handler(content_types=['text'])
def func(message: telebot.types.Message):
    """
    Функция для ответа на команды из кнопок
    "Записать новое дело"
    "Получить дела на сегодня"
    "Получить список всех задач"
    "Получить дела на завтра"
    "Удалить дело"

    args:  message -- telebot.types.Message
    """
    if message.text == "Записать новое дело":
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


def adding_task(message: telebot.types.Message):
    """
    Функция для добавления новых задач в переменную task_manager
    args - message -- telebot.types.Message
    """
    task = conversation.create_task(message.text.lower())
    if task is None:
        bot.send_message(message.chat.id,
                         text="Что-то пошло не так, убедитесь, что вы ввели задачу в правильном формате")
    else:
        task_manager[message.chat.id].add_task(task)
        bot.send_message(message.chat.id, text="Дело успешно добавлено")


def deleting_task(message: telebot.types.Message):
    """
    Функция для удаления  задач из переменной task_manager
    args - message -- telebot.types.Message
    """
    tasks_list = task_manager[message.chat.id].get_all_tasks()
    if int(message.text) - 1 > len(tasks_list):
        raise ValueError
    else:
        task_manager[message.chat.id].remove_task(int(message.text) - 1)
        bot.send_message(message.chat.id, text="Дело успешно удалено")


class ReminderHandler():
    """
    Класс содержит информацию об отправке уведомлений пользователю
    Методы:

    update - метод для отправки напоминаний в начале и в конце дня о сегодняшних и завтрашних задачах

    moment_reminder - метод для отпарвки напоминаний за 10 минут до дела
    """

    def __init__(self):
        self.actual_date = date.today()
        self.today_reminder_sent = False
        self.tomorrow_reminder_sent = False

    def update(self):
        """
        Метод для отправки напоминаний
        -Проверяет сменился ли день
        -Проверяет, нужно ли отправлять увдедомления о сегодняшних делах в 9:00
        -Проверяет, нужно ли отправлять увдедомления о делах на завтра в 21:00
        """
        hour = datetime.now().hour

        if date.today() > self.actual_date:
            self.actual_date = date.today()
            self.today_reminder_sent = False
            self.tomorrow_reminder_sent = False
            filter_tasks()

        if self.today_reminder_sent is False and hour >= 9:
            self.today_reminder_sent = True
            for chat_id in task_manager.keys():
                tasks_list = task_manager[chat_id].get_tasks_for_today()
                today_tasks = '\n'.join(map(str, tasks_list))
                bot.send_message(chat_id, 'Задачи на сегодня:\n' +
                                          today_tasks if len(
                    today_tasks) > 0 else "На сегодня ничего не запланировано.")

        if self.tomorrow_reminder_sent is False and hour >= 19:
            self.tomorrow_reminder_sent = True
            for chat_id in task_manager.keys():
                tasks_list = task_manager[chat_id].get_tasks_for_tomorrow()
                today_tasks = '\n'.join(map(str, tasks_list))
                bot.send_message(chat_id, 'Задачи на завтра:\n' +
                                          today_tasks if len(today_tasks) > 0 else "На завтра ничего не запланировано.")

        self.moment_reminder()

    def moment_reminder(self):
        """
        Метод для отправки  мгновенных напоминаний - за 10 минут до дела
        """
        now = datetime.now()
        for chat_id in task_manager.keys():
            tasks_list = task_manager[chat_id].get_tasks_for_today()
            for task in tasks_list:
                if (not task.reminded
                        and isinstance(task._date, datetime)
                        and (task._date - now).seconds <= 600):
                    task.reminded = True
                    bot.send_message(chat_id, 'Напоминание:\n' + str(task))


def filter_tasks():
    """
    Функция для удаления просроченных задач из словаря task_manager
    """
    for task_man in task_manager.values():
        task_man.remove_outdated_tasks()


def run_reminder():
    """
    Функция запускает обновление объекта ReminderHandler
    Каждые 10 секунд происходит обновление аттрибутов класса ReminderHandler
    """
    reminder_handler = ReminderHandler()
    while True:
        reminder_handler.update()
        time.sleep(10)


def start_reminder():
    """
   Функция создаёт отдельный поток для фоновой работы run_reminder
    """
    t = threading.Thread(target=run_reminder)
    t.daemon = True
    t.start()


start_reminder()

bot.polling(none_stop=True)
