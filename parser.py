import json
import requests
import os
import datetime

from requests import RequestException


def response_from_api(url):
    try:
        response = requests.get(url)
    except RequestException:
        print("Ошибка получения данных. Попробуйте повторить запрос позже.")
        exit()
    return json.loads(response.text)


def todo_list(todostr, todotitle):
    todostr = f'{todostr}{todotitle[0:50] + "..." if len(todotitle) > 50 else todotitle}\n'
    return todostr


todos = response_from_api('https://json.medrating.org/todos')
users = response_from_api('https://json.medrating.org/users')
crnttime = datetime.datetime.today().strftime("%Y.%m.%d %H:%M:%S")
if not os.path.exists('tasks'):
    os.makedirs('tasks')
for user in users:
    filename = os.path.join(r'tasks', f"{user['username']}.txt")
    execute = ''
    notexec = ''
    tmpfile = None
    for todo in todos:
        if todo['userId'] == user['id'] and todo['completed']:
            execute = todo_list(execute, todo["title"])
        elif todo['userId'] == user['id'] and not todo['completed']:
            notexec = todo_list(notexec, todo["title"])
    if os.path.isfile(filename):
        oldfile = open(filename, 'r')
        oldfileline = oldfile.readline()
        oldfile.close()
        oldfilelist = oldfileline.split('> ')
        filemodify = oldfilelist[1].replace(':', '-').strip('\n')
        tmpfile = os.path.join(r'tasks', f"{user['username']}.tmp")
        oldfilename = os.path.join(r'tasks', f"{user['username']}_{filemodify}.txt")
        os.rename(filename, tmpfile)
    try:
        with open(filename, "w", encoding='utf-8') as f:
            temp = f'{user["name"]} <{user["email"]}> {crnttime}\n{user["company"]["name"]}\n' \
                   f'\nЗавершенные задачи:\n' \
                   f'{execute if len(execute)>0 else "Пользователь не имеет завершенных задач"}' \
                   f'\nОставшиеся задачи: \n' \
                   f'{notexec if len(notexec)>0 else "Пользователь не имеет не завершенных задач"}'
            f.write(temp)
            f.close()
    except IOError:
        os.rename(tmpfile, filename)
        continue
    if tmpfile:
        try:
            os.rename(tmpfile, oldfilename)
        except FileExistsError:
            os.remove(oldfilename)
            os.rename(tmpfile, oldfilename)
