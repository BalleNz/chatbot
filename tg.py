import telebot
import sqlite3
import os.path
from random import choice

bot = telebot.TeleBot('1869980719:AAGIzUkAODkq3YKDsqFUk6DVMKKsVlcNGVo')
mes = str()
id = int()

@bot.message_handler(commands=['words'])
def commands(command):
    choices = set([m for m, a in sql_data()])
    choices.update(set([a for m, a in sql_data()]))
    bot.send_message(command.chat.id, f'my BD has {len(choices)} words')

@bot.message_handler(content_types='text')
def botting(message):
    global mes
    global id
    id = message.from_user.id
    temp = check_for_message(message)
    if temp:
        mes = temp
        bot.send_message(message.chat.id, message_main(temp))
    else:
        sql_write(message.text, 1) #write old_message
        mes = get_old_mes()
        bot.send_message(message.chat.id, message_main(mes))
        bot.register_next_step_handler(message, get_answer)

def message_main(text):
    if len(text) > 1:
        return text.upper()[0] + text.lower()[1:]
    return text.upper()

def get_old_mes(): #if have's
    olds = sql_data(1)
    if len(olds) > 20:
        x = choice([x[0] for x in olds[:20]])
        with sqlite3.connect(os.path.abspath('data.db')) as db:
            cursor = db.cursor()
            cursor.execute("""DELETE FROM old_messages WHERE message=(?) or message=(?)""", (x, x.lower()))
            db.commit()
        return x #if olds
    choices = set([m for m, a in sql_data()])
    choices.update(set([a for m, a in sql_data()]))
    return(choice(list(choices)))

def get_answer(answer):
    if answer.text[0] != '/': #такая тупая проверка на команду
        if id == answer.from_user.id: sql_write(answer.text) #id is equal -> write(m, a) in BD
        botting(answer)
    else: commands(answer)

def grab_unique(answers):
    dict = {x:answers.count(x) for x in answers}
    return choice([x for x in dict.keys() if dict[x] == max(list(dict.values()))])

def check_for_message(message):
    dict = sql_data()
    if message.text.lower() not in [m.lower() for m, a in dict]: return 0
    answers = [a for m, a in dict if m.lower() == message.text.lower()]
    return grab_unique(answers)

def sql_data(toggle=0): #0: messages; 1: old_messages
    with sqlite3.connect(os.path.abspath('data.db')) as db:
        if not toggle:
            return list(db.execute("""SELECT * FROM 'messages'"""))
        else:
            return list(db.execute("""SELECT * FROM 'old_messages'"""))

def sql_write(answer, toggle=0): #0: (m, a) in mes; 1: (m) in old_mes
    with sqlite3.connect(os.path.abspath('data.db')) as db:
        cursor = db.cursor()
        if not toggle:
            cursor.execute("""INSERT INTO messages (message, answer) VALUES(?, ?)""", (mes, answer))
        else:
            cursor.execute("""INSERT INTO old_messages (message) VALUES (?)""", (answer,))
        db.commit()

bot.polling(none_stop=1, interval=0)