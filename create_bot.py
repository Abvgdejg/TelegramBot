import config_parser

config = config_parser.config
services = config_parser.services
commands = config_parser.commands

########## Change ###########
host = None
port = None
password = None

API_TOKEN = None
#############################


imports = """
import logging
from telebot import types, TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from redis import Redis
"""
token = f"""
API_TOKEN = {API_TOKEN}
"""

redis = """
r = Redis(host=None, port=0, password=None, db=10)
def enter_command(channel, data):
    r.publish(channel, data)
"""
bot_init = """
logging.basicConfig(level=logging.INFO)

bot = TeleBot(token=API_TOKEN)
last_message = None
"""

start = """
##### Start #####

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: types.Message):

    global last_message
    last_message = menu_markup(message)
"""

##### Handler #####

tmp_1 = ""
for service in services:
    tmp_1 += f"""
    elif call.data == "{service}": last_message = {service}_markup(call.message)
"""
    for command in commands[service]:
        tmp_1 += f"""
    elif call.data == "{service}_{command}": {service}_{command}(call.message)
"""

handler = """
##### Handler #####

@bot.callback_query_handler(func=lambda call: True)
def commands_handler(call: types.CallbackQuery):
    global last_message

    if call.data == "to_menu" : menu_markup(call.message)
""" + tmp_1
    
##### Markups #####

tmp_1 = ""
for service in services:
    tmp_1 += f"""
    b_{service} = InlineKeyboardButton("{service}", callback_data='{service}')
    k.add(b_{service})
    """
tmp_1 += """
    if last_message == None:
        message = bot.send_message(message.chat.id, 
                                   "Choose Service", 
                                   reply_markup=k)
    else: 
        message = bot.edit_message_text(text="Choose Service",
                                        chat_id=message.chat.id,
                                        message_id=last_message.id,
                                        reply_markup=k)
    return message
"""


tmp_2 = ""
for service in services:
    tmp_2 += f"""
def {service}_markup(message):
    k = InlineKeyboardMarkup()
"""
    for command in commands[service]:
        tmp_2 += f"""
    b_{command} = InlineKeyboardButton("{config[service][command]["display_text"]}", callback_data='{service}_{command}')
    k.add(b_{command})
    """
    tmp_2 += f"""
    k.add(add_menu_button())

    message = bot.edit_message_text(chat_id=message.chat.id,
                                    text="{service} commands", 
                                    message_id=last_message.id, 
                                    reply_markup=k)
    return message
    """
markups = f"""
##### Markups #####

def menu_markup(message):
    k = InlineKeyboardMarkup()
""" + tmp_1 + tmp_2

##### Functions #####

tmp_1 = ""
for service in services:
    for command in commands[service]:
        tmp_1 += f"""
def {service}_{command}(message):
    k = InlineKeyboardMarkup().add(add_menu_button())
    bot.edit_message_text(chat_id=message.chat.id, 
                          text="{config[service][command]["bot_text"]}",
                          message_id=last_message.id,
                          reply_markup=k)
    enter_command("{service}", "{command}")
"""
        
functions = """
##### Functions #####

def add_menu_button():
    return InlineKeyboardButton("Menu", callback_data='to_menu')

""" + tmp_1

##### Run #####

run = """
##### Run #####


bot.polling(non_stop=True)
"""

bot_code = "".join([imports, token, redis, bot_init, 
                          start, handler, markups, functions, run])

with open("test_bot.py", "w") as f: f.write(bot_code)