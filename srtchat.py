#-*- coding: utf-8 -*-

import time
from datetime import datetime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import pave_event_space, per_chat_id, create_open
import json
import os
import re
from SRT import SRT

users = {}

login_pattern = "[a-zA-Z0-9]+[/][a-zA-Z0-9!@#$%^&*()]+"
reserve_pattern = "[\u3131-\u3163\uac00-\ud7a3]+[/][\u3131-\u3163\uac00-\ud7a3]+[/][0-9]+[/][0-9]+"
#email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
#number_pattern = re.compile(r"(\d{3})-(\d{3,4})-(\d{4})")
startMsg = "아직은 기능 개발중입니다.\n지금은 일반실만 예약가능합니다.\n예약을 진행하겠습니다."
startKeyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='1. 예약', callback_data='reserve')],
                   [InlineKeyboardButton(text='4. 종료', callback_data='exit')],
               ])

def getToken():
    f = open("telebot")
    token = f.readline().strip()
    f.close()
    
    return token

def reserve_message(chat_id,trains):
    keyboard =[]
    i = 0
    for train in trains:
        key = []
        key.append(InlineKeyboardButton(text=str(train),callback_data=str(i)))
        keyboard.append(key)
        i = i+1
    keyboard.append([InlineKeyboardButton(text='예약 종료', callback_data='exit')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    bot.sendMessage(chat_id,'조회 완료', reply_markup=keyboard)


def handle_message(msg):
    global users
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(datetime.now().isoformat(),'    Received Query : ', content_type, chat_type, chat_id)
    print(msg)
    if content_type == 'text':
        if re.match(login_pattern,msg['text']):
            cred = msg['text'].split('/')
            user_id = cred[0]
            user_pwd = cred[1]
            try:
                srt = SRT(user_id,user_pwd,verbose=True)
                users[chat_id] = {}
                users[chat_id]['srt'] = srt
                bot.sendMessage(chat_id,'{} 로그인 완료'.format(user_id))
                bot.sendMessage(chat_id,'조회할 기차 정보를 입력하세요(출발지/도착지/날짜/시간)\nex)수서/부산/20190913/144000')
            except Exception as e:
                print(e)
                bot.sendMessage(chat_id,'로그인 실패\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
        elif re.match(reserve_pattern,msg['text']):
            if chat_id in users:
                print(chat_id,' User logged in')
                srt = users.get(chat_id).get('srt')
                infos = msg['text'].split('/')
                dep = infos[0]
                arr = infos[1]
                data = infos[2]
                time = infos[3]
                try:
                    trains = srt.search_train(dep,arr,data,time)
                    users[chat_id]['trains'] = trains
                    reserve_message(chat_id,trains)
                except Exception as e:
                    print(e)
                    bot.sendMessage(chat_id,'조희 실패\n조회할 기차 정보를 입력하세요(출발지/도착지/날짜/시간)\nex)수서/부산/20190913/144000')
            else:
                bot.sendMessage(chat_id,'로그인 정보가 없습니다\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
        else:
            bot.sendMessage(chat_id,startMsg, reply_markup=startKeyboard)

def reserve_query(msg): 
    global users
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    if query_data == 'reserve':
        bot.sendMessage(from_id,'계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
    elif query_data == 'exit':
        bot.sendMessage(from_id,'종료')
        if from_id in users:
            del users[from_id]
        bot.sendMessage(from_id,startMsg, reply_markup=startKeyboard)

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0
    
    def open(self, initial_msg, seed):
        self.sender.sendMessage('Guess my number')
        return True  # prevent on_message() from being called on the initial message
    
    def on_chat_message(self, msg):
        self._count += 1
        self.sender.sendMessage(self._count)

if __name__ == '__main__':

    srtoken = getToken()
    bot = telepot.DelegatorBot(srtoken, [
        pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10),
    ])
    
    MessageLoop(bot, {'chat': handle_message,'callback_query': reserve_query}).run_as_thread()
    print('[+] ---------- Start Listening ----------')


    while True:
        time.sleep(10)