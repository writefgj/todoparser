import json
import requests
import os
import datetime
import time
from requests import RequestException


def response_from_api(url):
    """Запрашивает данные у сервера. Возварщает массив"""
    response = None
    try:
        response = requests.get(url)
    except RequestException:
        print("Ошибка получения данных. Попробуйте повторить запрос позже.")
        time.sleep(3)
        exit()
    if response:
        return json.loads(response.text)


def todo_list(todostr, todotitle):
    """Собирает список задач. Возвращает строку."""
    todostr = f'{todostr}{todotitle[0:50] + "..." if len(todotitle) > 50 else todotitle}\n'
    return todostr


def valid_user(dicuser):
    """Проверяет корректность данных пользователя"""
    if 'username' in dicuser and 'id' in dicuser and 'name' in dicuser and 'email' in dicuser and 'company' in dicuser:
        return True
    else:
        return False


def valid_todo(dictodo):
    """Проверяет корректность данных задач"""
    if 'userId' in dictodo and 'completed' in dictodo and 'title' in dictodo:
        return True
    else:
        return False


todos = response_from_api('https://json.medrating.org/todos')
users = response_from_api('https://json.medrating.org/users')
# Случай с многократным запуском скрипта в течении одной минуты в задании не описан, поэтому добавил секунды
crnttime = datetime.datetime.today().strftime("%Y.%m.%d %H:%M:%S")
oldfilename = None
if __name__ == '__main__':
    # Проверяем наличие директории, если ее нет - создаем
    if not os.path.exists('tasks'):
        os.makedirs('tasks')
    # Перебираем элементы массива с пользователями
    for user in users:
        execute = ''
        notexec = ''
        tmpfile = None
        if valid_user(user):
            filename = os.path.join(r'tasks', f"{user['username']}.txt")
            # Перебираем элементы массива с задачами
            for todo in todos:
                if valid_todo(todo):
                    if todo['userId'] == user['id'] and todo['completed']:
                        execute = todo_list(execute, todo["title"])
                    elif todo['userId'] == user['id'] and not todo['completed']:
                        notexec = todo_list(notexec, todo["title"])
            # Если файл уже существует - создаем его бэкап
            if os.path.isfile(filename):
                oldfile = open(filename, 'r')
                oldfileline = oldfile.readline()
                oldfile.close()
                oldfilelist = oldfileline.split('> ')
                filemodify = oldfilelist[1].replace(':', '-').strip('\n')
                tmpfile = os.path.join(r'tasks', f"{user['username']}.tmp")
                oldfilename = os.path.join(r'tasks', f"{user['username']}_{filemodify}.txt")
                os.rename(filename, tmpfile)
            # Пробуем записать новый файл, если не удалось - восстанавливаем бэкап
            try:
                with open(filename, "w", encoding='utf-8') as f:
                    temp = f'{user["name"]} <{user["email"]}> {crnttime}\n{user["company"]["name"]}\n' \
                           f'\nЗавершенные задачи:\n' \
                           f'{execute if len(execute) > 0 else "Пользователь не имеет завершенных задач"}' \
                           f'\nОставшиеся задачи: \n' \
                           f'{notexec if len(notexec) > 0 else "Пользователь не имеет не завершенных задач"}'
                    f.write(temp)
                    f.close()
                    print(f"Создан {filename}")
            except IOError:
                os.remove(filename)
                os.rename(tmpfile, filename)
                continue
            # Если новый файл создан успешно - создаем старый отчет с датой в имени
            if tmpfile:
                try:
                    os.rename(tmpfile, oldfilename)
                    print(f'Обнаружен файл, сформированный ранее. Переименовываем в {oldfilename}.')
                except FileExistsError:
                    os.remove(oldfilename)
                    os.rename(tmpfile, oldfilename)
        else:
            print('Данные пользователя некорректны, файл не создан.')
