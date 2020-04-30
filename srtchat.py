#-*- coding: utf-8 -*-

import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import os
import re
from SRT import SRT



pattern = "[a-zA-Z0-9]+[/][a-zA-Z0-9!@#$%^&*()]+"

def getToken():
    f = open("telebot")
    token = f.readline().strip()
    f.close()
    
    return token

def start_message(msg): 
    startMsg = "예약을 진행하겠습니다."
    content_type, chat_type, chat_id = telepot.glance(msg)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='1. 예약', callback_data='1')],
                   [InlineKeyboardButton(text='4. 종료', callback_data='4')],
               ])
    bot.sendMessage(chat_id,startMsg, reply_markup=keyboard)


def callback_query(msg): 
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    if query_data == '1':
        bot.sendMessage(from_id,'계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
    elif query_data == '4':
        bot.sendMessage(from_id,'종료')
        os._exit(1)
    bot.answerCallbackQuery(query_id, text='Got it')
'''
def handle(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    print(content_type,chat_type,chat_id,msg_date,msg_id)
    print(msg)
    print('[ --------- Message Received --------- ]\n\n')

    if content_type == 'text':
        if msg['text'] == '1':
            bot.sendMessage(chat_id,'계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
        elif re.match(pattern,msg['text']):
            user_id = msg['text'].split('/')[0]
            bot.sendMessage(chat_id,'{} 로그인 완료'.format(user_id))
        elif msg['text'] == '4':
            bot.sendMessage(chat_id,'종료')
            os._exit(1)
        else:
            bot.sendMessage(chat_id,checkIDMsg,reply_markup=keyboard)
'''

if __name__ == '__main__':

    srtoken = getToken()
    bot = telepot.Bot(srtoken)
    
    MessageLoop(bot, {'chat': start_message,'callback_query': callback_query}).run_as_thread()
    print('[+] ---------- Start Listening ----------')


    while True:
        time.sleep(10)