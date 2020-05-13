#-*- coding: utf-8 -*-

#기능별 모듈 구분

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import pave_event_space, per_chat_id, create_open

import time
from datetime import datetime
import random
import os
import re

from SRT import SRT
from SRT.passenger import Passenger, Adult, Child

users = {}

login_pattern = re.compile(r"[a-zA-Z0-9-.@]+[/].+")
reserve_pattern = re.compile(r"[\u3131-\u3163\uac00-\ud7a3]+[/][\u3131-\u3163\uac00-\ud7a3]+[/]\d{8}[/]\d{6}")
person_pattern = re.compile(r"[\uc5b4][\ub978][0-5]+[/]+[\uc544][\uc774[0-5]")
number_pattern = re.compile(r"\d{1}")
time_pattern = re.compile(r"[\u3131-\u3163\uac00-\ud7a3]+[~][\u3131-\u3163\uac00-\ud7a3]+[(][0-9:~]+[)]")
refer_pattern = re.compile(r"\d{2}.+[\u3131-\u3163\uac00-\ud7a3]+[~][\u3131-\u3163\uac00-\ud7a3]+[(][0-9:~]+[)].+[(]\d[\uc11d][)]")
seat_pattern = re.compile(r"[\u3131-\u3163\uac00-\ud7a3]+[\s][\u3131-\u3163\uac00-\ud7a3]+")

startMsg = "기능 개발중입니다.\n봇 관련 문의는 [@chocodotz]로 연락바랍니다.\n\
모든 소스코드는 (https://github.com/choco0908/SRTChatBot.git)에 \
있으며 어떤 개인정보도 서버에 남기지 않습니다.\n\
지금은 일반실만 예약가능하며 자리 선택은 불가능합니다.\n예약을 진행하겠습니다."
commonMsg = "원하는 기능을 선택하세요."
startKeyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='1. 예약', callback_data='reserve')],
                   [InlineKeyboardButton(text='2. 조회', callback_data='refers')],
                   [InlineKeyboardButton(text='3. 취소', callback_data='cancel')],
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
    if len(trains) == 0:
        keyboard.append([InlineKeyboardButton(text='해당 시간에는 기차가 없습니다.', callback_data=' ')])
    else:
        for train in trains:
            key = []
            time = time_pattern.findall(str(train))[0]
            seat = seat_pattern.findall(str(train))[1]
            key.append(InlineKeyboardButton(text=time+' '+seat,callback_data='reserve_'+str(i)))
            keyboard.append(key)
            i = i+1
    keyboard.append([InlineKeyboardButton(text='돌아가기', callback_data='back')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    bot.sendMessage(chat_id,'열차 검색 완료.\n시간표 선택시 열차가 예약됩니다.', reply_markup=keyboard)

def refer_message(chat_id,trains):
    keyboard =[]
    i = 0
    if len(trains) == 0:
        keyboard.append([InlineKeyboardButton(text='예약된 기차가 없습니다.', callback_data=' ')])
    else:
        for train in trains:
            key = []
            time = refer_pattern.findall(str(train))[0]
            key.append(InlineKeyboardButton(text=time,callback_data='refer_'+str(i)))
            keyboard.append(key)
            i = i+1
    keyboard.append([InlineKeyboardButton(text='돌아가기', callback_data='back')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    bot.sendMessage(chat_id,'조회 할 열차표를 선택하세요.', reply_markup=keyboard)

def cancel_message(chat_id,trains):
    keyboard =[]
    i = 0
    if len(trains) == 0:
        keyboard.append([InlineKeyboardButton(text='예약된 기차가 없습니다.', callback_data=' ')])
    else:
        for train in trains:
            key = []
            time = refer_pattern.findall(str(train))[0]
            key.append(InlineKeyboardButton(text=time,callback_data='cancel_'+str(i)))
            keyboard.append(key)
            i = i+1
    keyboard.append([InlineKeyboardButton(text='돌아가기', callback_data='back')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    bot.sendMessage(chat_id,'취소 할 열차표를 선택하세요.', reply_markup=keyboard)

def handle_message(msg):
    global users
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(datetime.now().isoformat(),'    Received Query : ', content_type, chat_type, chat_id)
    #print(msg)
    if content_type == 'text':
        if login_pattern.match(msg['text']):
            cred = msg['text'].split('/')
            user_id = cred[0]
            user_pwd = cred[1]
            try:
                srt = SRT(user_id,user_pwd)
                users[chat_id] = {}
                users[chat_id]['srt'] = srt
                bot.sendMessage(chat_id,'{} 로그인 완료'.format(user_id))
                bot.sendMessage(chat_id,'조회할 기차 정보를 입력하세요(출발지/도착지/날짜/시간)\nex)수서/부산/20190913/144000')
                bot.sendMessage(chat_id,'인원수를 입력하세요.\n입력이 없으면 어른1명으로 예약됩니다.\nex)어른3/아이1')
            except Exception as e:
                print(e)
                bot.sendMessage(chat_id,'로그인 실패\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
        elif reserve_pattern.match(msg['text']):
            if chat_id in users:
                try:
                    srt = users.get(chat_id).get('srt')
                except Exception as e:
                    bot.sendMessage(chat_id,'로그인 정보가 없습니다\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
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
                    bot.sendMessage(chat_id,'조회 실패\n조회할 기차 정보를 입력하세요(출발지/도착지/날짜/시간)\nex)수서/부산/20190913/144000')
            else:
                bot.sendMessage(chat_id,'로그인 정보가 없습니다\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
        elif person_pattern.match(msg['text']):
            if chat_id in users:
                try:
                    srt = users.get(chat_id).get('srt')
                except Exception as e:
                    bot.sendMessage(chat_id,'로그인 정보가 없습니다\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
                persons = number_pattern.findall(msg['text'])
                adult = int(persons[0])
                child = int(persons[1])
                if (adult+child) > 9 or (adult+child) == 0 :
                    bot.sendMessage(chat_id,'예약 가능인원은 총 9 명까지 입니다.\n다시 입력하세요.\nex)어른3/아이1')
                    return
                passenger = []
                for i in range(adult):
                    passenger.append(Adult())
                for i in range(child):
                    passenger.append(Child())
                try:
                    users[chat_id]['passenger'] = passenger
                    bot.sendMessage(chat_id,msg['text']+' 인원 입력')
                except Exception as e:
                    print(e)
                    bot.sendMessage(chat_id,'인원 입력 실패.\n다시 입력하세요.\nex)어른3/아이1')
            else:
                bot.sendMessage(chat_id,'로그인 정보가 없습니다\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
        else:
            bot.sendMessage(chat_id,startMsg, reply_markup=startKeyboard)

def reserve_query(msg): 
    global users
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    if query_data == 'reserve':
        try :
            srt = users.get(from_id).get('srt')
            bot.sendMessage(from_id,'조회할 기차 정보를 입력하세요(출발지/도착지/날짜/시간)\nex)수서/부산/20190913/144000')
        except Exception as e:
            bot.sendMessage(from_id,'로그인 정보가 없습니다.\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
    elif 'reserve_' in query_data:
        print(query_data+'예약진행')
        num = int(query_data.split('_')[1])
        try :
            srt = users.get(from_id).get('srt')
            train = users.get(from_id).get('trains')[num]
            bot.sendMessage(from_id,str(train)+'\n예약 중')  
            while True:
                try:    
                    if 'passenger' in users.get(from_id):
                        passenger = users.get(from_id).get('passenger')
                        reservation = srt.reserve(train,passengers=passenger)
                    else:
                        reservation = srt.reserve(train)
                    bot.sendMessage(from_id,str(reservation)+'\n예약완료')
                    bot.sendMessage(from_id,commonMsg, reply_markup=startKeyboard)
                    break
                except Exception as e:
                    print(e)
                    #bot.sendMessage(from_id,'예약 실패\n약 1초 후 재시도 합니다.')
                    time.sleep(random.random()+0.5)
        except Exception as e:
            bot.sendMessage(from_id,'로그인 정보가 없습니다.\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
    elif query_data == 'refers':
        try :
            srt = users.get(from_id).get('srt')
            try:
                trains = srt.get_reservations()
                refer_message(from_id,trains)
            except Exception as e:
                print(e)
                bot.sendMessage(from_id,'조회 실패')
        except Exception as e:
            bot.sendMessage(from_id,'로그인 정보가 없습니다.\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
    elif query_data == 'cancel':
        try :
            srt = users.get(from_id).get('srt')
            try:
                trains = srt.get_reservations()
                cancel_message(from_id,trains)
            except Exception as e:
                print(e)
                bot.sendMessage(from_id,'조회 실패')
        except Exception as e:
            bot.sendMessage(from_id,'로그인 정보가 없습니다.\n계정정보를 입력하세요(USER_ID/USER_PW)\nex)id_1234/pw_1234')
    elif 'cancel_' in query_data:
        print(query_data+'취소진행')
        num = int(query_data.split('_')[1])
        try:
            srt = users.get(from_id).get('srt')
            train = srt.get_reservations()[num]
            reservation = srt.cancel(train)
            bot.sendMessage(from_id,str(train)+'\n취소완료')
            bot.sendMessage(from_id,commonMsg, reply_markup=startKeyboard)
        except Exception as e:
            print(e)
            bot.sendMessage(from_id,'예약 실패')
    elif query_data == 'back':
        bot.sendMessage(from_id,commonMsg, reply_markup=startKeyboard)
    elif query_data == 'exit':
        bot.sendMessage(from_id,'종료')
        if from_id in users:
            del users[from_id]
        bot.sendMessage(from_id,startMsg, reply_markup=startKeyboard)
        #os._exit(1)
        

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0
    
    def open(self, initial_msg, seed):
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