import re
from datetime import datetime, timedelta, date, time
from typing import Union


class Time():
    """
    Класс, выполняющий парсинг введенных данных.
    """
    def __init__(self):
        """
        Функция-конструктор класса Time.
        """
        # Регулярное выражение для строк вида '2018/10/1 22:20'.
        self.reg_date = re.compile(r'(\d{4}/\d{1,2}/\d{1,2} \d{2}:\d{2}) (.*)')
        # Регулярное выражение для строк вида 'завтра в 15:00'.
        self.reg_word = re.compile(r'([A-zА-я ]*) (в|at) (\d{2}:\d{2}) (.*)')
        self.days_and_shift = {
            'сегодня': timedelta(days=0),
            'today': timedelta(days=0),
            'завтра': timedelta(days=1),
            'tomorrow': timedelta(days=1),
            'послезавтра': timedelta(days=2),
            'через неделю': timedelta(days=7),
            'in a week': timedelta(days=7)
        }

    def parse_raw_date(self, input_string: str) -> datetime:
        """
        Функция для превращения строки с датой и временем в объект datetime.

        :param input_string:
        :return: объект datetime
        """
        try:
            result = datetime.strptime(input_string, "%Y/%m/%d %H:%M")
        except ValueError:
            return None
        return result

    def input_word_and_time(self, word: str, time: str) -> datetime:
        """
        Функция для превращения строки со словесным обозначением даты и временем в объект datetime.

        :param word:
        :param time:
        :return: объект datetime
        """
        time_to_add = datetime.strptime(time, "%H:%M").time()
        if word not in self.days_and_shift:
            return None
        date_to_add = date.today() + self.days_and_shift[word]
        return datetime.combine(date_to_add, time_to_add)

    def input_word(self, word: str) -> date:
        """
        Функция для превращения строки со словесным обозначением даты в объект date.

        :param word:
        :return: объект date
        """
        today_date = datetime.today().date()
        if word not in self.days_and_shift:
            return None
        result = today_date + self.days_and_shift[word]
        return result

    def parse_string(self, input_string: str) -> Union[datetime, date]:
        """
        Функция, осуществляющая парсинг строк со словесным обозначением даты.

        :param input_string:
        :return: ответ
        """
        if ':' in input_string:
            if ' at ' in input_string:
                input_list = input_string.split(' at ')
            elif ' в ' in input_string:
                input_list = input_string.split(' в ')
            word = input_list[0]
            time = input_list[1]
            result = self.input_word_and_time(word, time)
        else:
            word = input_string
            result = self.input_word(word)
        return result

    def parse(self, input_string: str):
        """
        Функция, осуществляющая парсинг строки вне зависимости от формата.

        :param input_string:
        :return: ответ
        """
        if not input_string:
            return None

        match_reg_date = self.reg_date.match(input_string)
        if match_reg_date:
            return self.parse_raw_date(match_reg_date.group(1)), match_reg_date.group(2)

        match_reg_word = self.reg_word.match(input_string)
        if match_reg_word:
            return self.parse_string(match_reg_word.group(1) + ' ' +
                match_reg_word.group(2) + ' ' +
                match_reg_word.group(3)), match_reg_word.group(4)

        first_word = input_string.split()[0]
        if first_word in self.days_and_shift:
            if first_word == input_string:
                return self.parse_string(first_word), ''
            else:
                return self.parse_string(first_word), input_string[len(first_word) + 1:]
        return None