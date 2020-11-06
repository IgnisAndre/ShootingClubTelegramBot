#https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-–-Your-first-Bot
#https://groosha.gitbooks.io/telegram-bot-lessons/content/chapter8.html
version = '1.0.04'
revision = '書記'#.177
from telegram import replykeyboardmarkup, replykeyboardremove
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from GoogleCalendar import  get_credentials, init, create_event, del_from_event, find_event, api_import_events, api_update_event, datetime
from SQL import read_name, add_name, get_r_i, get_role, init_tables, injector
from credentials import TBToken, bd
from FaQ import rules, TaC

updater = Updater(token=TBToken)
dispatcher = updater.dispatcher

#test_keybord = [['1', '2'], ['3', '4']]
#reply_markup = replykeyboardmarkup.ReplyKeyboardMarkup(test_keybord)

def start(bot, update, args):
    print("start started")
    c_i=update.message.chat_id
    text = " ".join(args)
    print(f"c_i ={c_i}, args = {text}")
    s_n = text.split()
    if len(s_n) == 1:
        n = s_n[0].strip()
        s = "Анонович"
    elif len(s_n) == 2:
        n = s_n[0].strip().capitalize()
        s = s_n[1].strip().capitalize()
    else:
        n = 'Анон'
        s = 'Анонович'
    print(c_i, n, s)
    add_name(c_i, n, s)
    bot.send_message(chat_id=c_i, text=f"Привет, {n} {s}.\nЕсли тебе не нравится, как я к тебе обратился, введи команду '/start Имя Фамилия' ещё раз.")
    bot.send_message(chat_id=247893408, text=f"{c_i} зарегистрировался как {n} {s}")

def echo(bot, update):
    print('echo start')
    c_i = update.message.chat_id
    print('got c_i: ', c_i)
    n_s = read_name(c_i)

    faq_keybord = [['Время и условия работы', 'Правила записи'],['Ничего, просто мимокрокодил']]
    faq_markup = replykeyboardmarkup.ReplyKeyboardMarkup(faq_keybord, one_time_keyboard=True)
    if update.message.text == 'Время и условия работы':
        bot.send_message(chat_id=c_i, text=TaC, reply_markup=faq_markup)
    elif update.message.text == 'Правила записи':
        bot.send_message(chat_id=c_i, text=rules, reply_markup=faq_markup)
    elif update.message.text == 'Ничего, просто мимокрокодил':
        bot.send_message(chat_id=c_i, text=f"Ну и зачем же ты, {n_s[0]}, меня тогда беспокоишь?")
    else:
        if get_r_i(c_i) == 3:
                bot.send_message(chat_id=update.message.chat_id, text=f"Отстань, тестер №{c_i}, {n_s[0]}.")
        #elif c_i == 247893408:
        elif get_r_i(c_i) == 4:
            bot.send_message(chat_id=update.message.chat_id, text=f"Не трогай меня, я знаю что ты сделал.")
        else:
            bot.send_message(chat_id=update.message.chat_id, text=f"Отстань, {n_s[0]}.")

def ask(bot, update, args):
    c_i = update.message.chat_id
    msg = " ".join(args)
    bot.send_message(chat_id=c_i, text = "Вопрос отправлен от имени бота.")
    n_s = read_name(c_i)
    bot.send_message(chat_id=247893408, text=f"{n_s[0]} {n_s[1]} ({c_i}) спрашивает: \n{msg}")

def answer(bot, update, args):
    c_i = update.message.chat_id
    r_i = get_r_i(c_i)
    if r_i == 4:
        text = " ".join(args)
        body = text.split(' ', 1)
        c_i = int(body[0])
        text = body[1]
        bot.send_message(chat_id=c_i, text = f'Ответ на анонимный вопрос: \n{text}')
        bot.send_message(chat_id=247893408, text=f"Ответ на вопрос {c_i} был отправлен")
    else:
        role = get_role(r_i)
        bot.send_message(chat_id=c_i, text = f'Ты {role}, а не разработчик, ты не можешь отетить.')


def faq(bot, update, args):
    c_i = update.message.chat_id
    faq_keybord = [['Время и условия работы', 'Правила записи'],['Ничего, просто мимокрокодил']]
    reply_markup = replykeyboardmarkup.ReplyKeyboardMarkup(faq_keybord, one_time_keyboard=True)
    bot.send_message(chat_id=c_i, text = "Что могу подсказать?", reply_markup=reply_markup)

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text = f"""
    Версия бота {version}.\nРевизия - {revision}\n Поддерживает следующие команды:
    /start - начать общение с ботом. Желательно указать имя и фамилию, например /start Анальный Властелин.
    /create - после команды надо цифрами ввести месяц, день, время, имя, разделять пробелами. Использовать только если это будет первая запись.
    /update - после команды надо цифрами ввести месяц, день, время, имя. Можно использовать и для создания первой записи.\nПример для обеих команд: Я хочу записаться на 27 часов 43 мартобря (семнадцатый месяц года). Я набираю /update 17 43 27 Вуглускр. Вуаля, запись появилась :)
    /show  - показать записавшихся. После команды надо ввести номер месяца и день, например /show 12 31
    /faq - получить справку по вопросам работы тира.
    /ask - задать анонимный вопрос разработчику c неиллюзорной перспективой получить ответ.\n
    Скрытые (не очень) команды:
    /init - Инициировать \ ренициировать БД. Не использовать, если нет ясного понимания значения каждого слова до точки. Если есть, всё равно не стоит.
    /inject - выполнить SQL-injection скрипт, введённый после команды. Не использовать, если нет ясного понимания всех слов до точки, или если нет разумных, светлых, добрых и вечных намерений.
    """)

def init_t(bot, update):
    c_i=update.message.chat_id
    print("Try to init tables")
    if c_i == 247893408:
        bot.send_message(chat_id=c_i, text="Инициация таблиц запущена")
        print('Start init')
        init_tables()
        print('End init')
        bot.send_message(chat_id=c_i, text="Инициация таблиц завершена")
    else:
        print(f"Attempt to init tables by {c_i} was blocked")
        bot.send_message(chat_id=c_i, text="Peнициация таблиц запрещена. Сказано же, 'без понимания не использовать'!")
        bot.send_message(chat_id=247893408, text="Инициация таблиц {c_i} была предотвращена")

def save_t(bot, update):
    try:
        bot.send_document(chat_id=247893408, document=open(bd, 'rb'))
    except BaseException as be:
        print('DB save error: ', be)
    c_i=update.message.chat_id
    bot.send_message(chat_id=247893408, text="{c_i} запросил дамп бд")

def inject_t(bot, update, args):
    c_i=update.message.chat_id
    if c_i == 247893408:
        print(f'{c_i} tries to')
        command = " ".join(args)
        try:
            result = injector(command)
            bot.send_message(chat_id=c_i, text=result)
        except BaseException as be:
                print("On showing tables error occur: ", type(be), be)
    else:
        print(f"Attempt to init tables by {c_i} was blocked")
        bot.send_message(chat_id=c_i, text="Просмотр таблиц запрещён. обратитесь к АСУБД за дальнейшими разъяснениями")
        bot.send_message(chat_id=247893408, text="Просмотр таблиц {c_i} был предотвращён")

def TGCcreate(bot, update, args):
    text=' '.join(args)
    msg = text.split()
    credentials = get_credentials()
    service = init(credentials)
    api_import_events(25, service, msg[0], msg[1])
    r = find_event(datetime.date.today().year, int(msg[0]),int(msg[1]),int(msg[2]))
    if r != None:
        bot.send_message(chat_id=update.message.chat_id, text="Нельзя создавать запись, если время уже занято. Надо использовать /update")
        return None
    n_s = 0
    c_i = update.message.chat_id
    mdt = update.message.date
    n_s = read_name(c_i)
    print("try to create with comment:", f"\n{mdt}::{n_s[0]} {n_s[1]}->{msg[3]}")
    create_event(service,int(msg[0]),int(msg[1]),int(msg[2]),msg[3], f"\n{mdt}::{n_s[0]} {n_s[1]}->{msg[3]}")#, year=int(2018))
    print("Success")
    bot.send_message(chat_id=update.message.chat_id, text="Запись создана")

    na_su = 0
    c_i = update.message.chat_id
    if c_i != 247893408:
        n_s = read_name(c_i)
        bot.send_message(chat_id=247893408, text=f"{n_s[0]} {n_s[1]} ({c_i}) записывается на {msg[0]}/{msg[1]}-{msg[2]}:00 как {msg[3]}")

def TGCshow(bot, update, args):
    text = ' '.join(args)
    params = text.split()
    credentials = get_credentials()
    service = init(credentials)
    message = api_import_events(25, service, params[0], params[1])
    bot.send_message(chat_id=update.message.chat_id, text=message)

def TGCupdate(bot, update, args):
    text = ' '.join(args)
    credentials = get_credentials()
    service = init(credentials)
    params = text.split(' ', 3)
    n_s = 0
    c_i = update.message.chat_id
    mdt = update.message.date
    n_s = read_name(c_i)
    try:
        print(f"{mdt} try to update with:\n{n_s[0]} {n_s[1]}->{params[3]}")
        v = api_update_event(service, params[0], params[1], params[2], params[3], f"\n{mdt}::{n_s[0]} {n_s[1]}->{params[3]}")
    except BaseException as be:
        print("shit happened in event update: ", type(be), be)
        v == -1
    if v == 0:
        message = f'Запись {params[3]} создана'
    elif v == -1:
        print("ERROR in update")
    else:
        message = f'Запись {params[3]} обновлена'
    bot.send_message(chat_id=update.message.chat_id, text=message)
    if c_i != 247893408:
        bot.send_message(chat_id=247893408, text=f"{n_s[0]} {n_s[1]} ({c_i}) записывается на {params[0]}/{params[1]}-{params[2]}:00 как {params[3]}")

def TGCdelete(bot, update, args):
    text = ' '.join(args)
    credentials = get_credentials()
    service = init(credentials)
    params = text.split(' ', 3)
    n_s = 0
    c_i = update.message.chat_id
    mdt = update.message.date
    n_s = read_name(c_i)
    try:
        v = del_from_event(service, params[0], params[1], params[2], params[3], f"\n{mdt}::{n_s[0]} {n_s[1]}-X{params[3]}")
    except BaseException as be:
        print("shit happened in delete from : ", type(be), be)
        v = -1
    if v == -1:
        print("ERROR in delete")
        message = f"Не удалось удалить {params[3]}"
    elif v == 0:
        message = "Запись удалена"
    else:
        message = f'Запись обновлена'
    bot.send_message(chat_id=update.message.chat_id, text=message)
    if c_i != 247893408:
        bot.send_message(chat_id=247893408, text=f"{n_s[0]} {n_s[0]} ({c_i}) удалил {params[3]} с {params[0]}/{params[1]}-{params[2]}:00")






start_handler = CommandHandler('start', start, pass_args=True)

init_t_handler = CommandHandler('init', init_t)
inject_t_handler = CommandHandler('inject', inject_t, pass_args=True)
save_t_handler = CommandHandler('savebd', save_t)
echo_handler = MessageHandler(Filters.text, echo)
ask_handler = CommandHandler('ask', ask, pass_args=True)
answer_handler = CommandHandler('answer', answer, pass_args=True)
faq_handler = CommandHandler('faq', faq, pass_args=True)
help_handler = CommandHandler('help', help)

TGCcreate_handler = CommandHandler('create', TGCcreate, pass_args=True)
TGCshow_handler = CommandHandler('show', TGCshow, pass_args=True)
TGCupdate_handler = CommandHandler('update', TGCupdate, pass_args=True)
TGCdelete_handler = CommandHandler('delete', TGCdelete, pass_args=True)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(init_t_handler)
dispatcher.add_handler(inject_t_handler)
dispatcher.add_handler(save_t_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(ask_handler)
dispatcher.add_handler(answer_handler)
dispatcher.add_handler(faq_handler)
dispatcher.add_handler(help_handler)

dispatcher.add_handler(TGCcreate_handler)
dispatcher.add_handler(TGCshow_handler)
dispatcher.add_handler(TGCupdate_handler)
dispatcher.add_handler(TGCdelete_handler)

init_tables()
updater.start_polling()
