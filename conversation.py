from datetime import datetime, date, time, timedelta
import Time


class Task():
    '''A class for tasks storing'''

    def __init__(self, task_date, task:str):
        assert isinstance(task_date, datetime) or isinstance(task_date, date)
        self._date = task_date
        self._task = task
        self.reminded = False

    def __eq__(self, other):
        return self._date == other._date and self._task == other._task

    def __lt__(self, other):
        if self.__get_date_object() < other.__get_date_object():
            return True
        elif self.__get_date_object() > other.__get_date_object():
            return False
        else:
            if isinstance(self._date, datetime) and isinstance(other._date, datetime):
                return self._date < other._date
            else:
                return not isinstance(self._date, datetime)

    def __str__(self):
        return 'Когда: {}. Задача: {}.'.format(self._date, self._task)

    def __get_date_object(self)->date:
        '''Special function for getting date, not datetime'''
        if isinstance(self._date, datetime):
            return self._date.date()
        else:
            return self._date


    def get_date(self)->date:
        return self._date


    def get_task(self)->str:
        return self._task



    def is_today(self)->bool:
        '''Checks whether date is today'''
        return self.__get_date_object() == datetime.today().date()

    def is_tomorrow(self)->bool:
        '''Checks whether date is tomorrow'''
        return self.__get_date_object() == datetime.today().date() + timedelta(days=1)

    def is_outdated(self)->bool:
        '''Checks whether task is outdated'''
        return self.__get_date_object() < datetime.today().date()


class TaskManager():
    '''A class for managing tasks list'''
    def __init__(self):
        self._tasks = []

    def add_task(self, task:Task):
        '''This function adds task to tasks list'''
        if not isinstance(task, Task):
            return
        if(len(self._tasks) == 0):
            self._tasks.append(task)
            return
        L = 0
        R = len(self._tasks)-1
        while (R-L > 1):
            M = (L+R)//2
            if task < self._tasks[M]:
                R = M
            else:
                L = M

        if task < self._tasks[L]:
            self._tasks.insert(L, task)
        elif task < self._tasks[R]:
            self._tasks.insert(R, task)
        else:
            self._tasks.insert(R+1, task)


    def remove_task(self, task_id:int):
        '''Removes task from tasks list'''
        del self._tasks[task_id]

    def get_all_tasks(self)->list:
        '''Returns all tasks in list'''
        return self._tasks

    def get_tasks_for_today(self)->list:
        '''Returns tasks for today'''
        return list(filter(lambda x: x.is_today(), self._tasks))

    def get_tasks_for_tomorrow(self)->list:
        '''Returns tasks for tomorrow'''
        return list(filter(lambda x: x.is_tomorrow(), self._tasks))

    def remove_outdated_tasks(self):
        '''Removes outdated tasks'''
        self._tasks = list(filter(lambda x: not x.is_outdated(), self._tasks))


def create_task(input_string:str)->Task:
    '''Function for creating new task from string'''
    parsed_input_string = Time.Time().parse(input_string)
    if not parsed_input_string:
        return None
    if not parsed_input_string[0] or not parsed_input_string[1]:
        return None
    task_object = Task(parsed_input_string[0], parsed_input_string[1])
    return task_object
