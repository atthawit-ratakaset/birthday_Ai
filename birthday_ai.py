import streamlit as st
from gtts import gTTS
import os
import json
import time
from datetime import datetime, timedelta
import base64
from mutagen.mp3 import MP3
import tempfile
import pandas as pd
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
from ai_thinking import calculate_ai, word_translator

class Chatbot:
    def __init__(self):
        self.responses = self.load_responses()
        self.person_data = self.load_person_data()
        self.history = self.load_history()

    def load_responses(self):
        try:
            if os.path.exists("responses.json"):
                with open("responses.json", "r", encoding="utf-8") as file:
                    responses = json.load(file)
                    return responses
            else:
                st.write("responses.json not found, loading default responses")
                return {
                    "สวัสดี": "สวัสดีค่ะ! มีอะไรให้ช่วยไหม?",
                    "คุณชื่ออะไร": "ฉันคือ Chatbot ค่ะ",
                    "ขอบคุณ": "แล้วพบกันใหม่ค่ะ"
                }
        except Exception as e:
            st.write(f"Error loading responses.json: {e}")
            return {}

    def save_responses(self):
        try:
            with open("responses.json", "w", encoding="utf-8") as file:
                json.dump(self.responses, file, ensure_ascii=False, indent=4)
        except Exception as e:
            st.write(f"Error saving responses.json: {e}")

    def load_person_data(self):
        try:
            if os.path.exists("data_birthday.json"):
                with open("data_birthday.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
                    return data
            else:
                return []
        except Exception as e:
            st.write(f"Error loading data_birthday.json: {e}")
            return {}

    def save_person_data(self):
        with open("data_birthday.json", "w", encoding="utf-8") as file:
            json.dump(self.person_data, file, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            if os.path.exists("history.json"):
                with open("history.json", "r", encoding="utf-8") as file:
                    history = json.load(file)
                    return history
            else:
                return []
        except Exception as e:
            st.write(f"Error loading history.json: {e}")
            return []

    def save_history(self):
        with open("history.json", "w", encoding="utf-8") as file:
            json.dump(self.history, file, ensure_ascii=False, indent=4)
    
    def show_json(self, json_data, title):
        st.write(f"### {title}")
        st.json(json_data)

    def convert_list_to_string(self, value):
        if isinstance(value, list):
            return ', '.join(map(str, value)) 
        return value

    def show_history_json_as_table(self, user_name, json_data, user_id):
        st.markdown(f"<h2 style='font-size:20px;'>ประวัติสนทนาของ{user_name}</h2>", unsafe_allow_html=True)
        user_history = [entry for entry in json_data if entry.get('user_id') == user_id]
        
        if user_history:
            df = pd.DataFrame(user_history)
            df.index += 1
            df = df.rename(columns={
                'timestamp': 'Timestamp', 
                'bot_input': 'Bot Input', 
                'user_input': 'User Input'
            })
            df['Bot Input'] = df['Bot Input'].apply(self.convert_list_to_string)
            if 'user_id' in df.columns:
                df = df.drop(columns=['user_id'])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("ไม่มีประวัติการสนทนาของอาจารย์ท่านนี้")

    def add_to_history(self, user_input, bot_input):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.history.append({
            "user_id": selected_person,
            "timestamp": timestamp,
            "user_input": user_input,
            "bot_input": bot_input
        })
        self.save_history()

    def add_to_history_bot_fisrt(self, bot_input, user_input):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.history.append({
            "user_id": selected_person,
            "timestamp": timestamp,
            "bot_input": bot_input,
            "user_input": user_input
        })
        self.save_history()

    def speak(self, text):
        try:
            tts = gTTS(text=text, lang='th')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts.save(temp_audio.name)
                
                audio = MP3(temp_audio.name)
                audio_length = audio.info.length
            
                with open(temp_audio.name, "rb") as f:
                    mp3_data = f.read()

            b64_encoded_audio = base64.b64encode(mp3_data).decode("utf-8")
            
            audio_html = self.audio_html(b64_encoded_audio)

            return audio_html, audio_length
        
        except Exception as e:
            st.write(f"Error in speak function: {e}")
            return ""

    def audio_html(self, audio_cilp):
        audio_html = f"""
            <audio id="chatbot-audio{st.session_state['audio_stage']}" autoplay="true" style="display:none;">
                <source src="data:audio/mp3;base64,{audio_cilp}" type="audio/mp3">
            </audio>
            """
        return audio_html

    def get_thai_date(self, offset):
        target_date = datetime.now() + timedelta(days=offset)
        months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 
                  'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
        thai_year = target_date.year + 543
        return f"วันที่ {target_date.day} {months[target_date.month - 1]} {thai_year}"

    def check_birthday(self):
        if self.person_data.get('birthday', 'ไม่ทราบ'):
            months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 
                      'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
            
            today = f"{datetime.now().day} {months[datetime.now().month - 1]}"

            birthday = " ".join(chatbot.person_data[selected_person].get('birthday').split()[:2])

            if today == birthday:
                self.add_to_history_bot_fisrt(f"สุขสันต์วันเกิดค่ะ ท่าน{chatbot.person_data[selected_person].get('name')} ขอให้วันนี้เป็นวันที่ดีสำหรับท่านค่ะ! \n ไม่ทราบว่าวันนี้ต้องการอะไรหรอกคะ?", '-')
                bot = update_chat_history("", f"สุขสันต์วันเกิดค่ะ ท่าน{chatbot.person_data[selected_person].get('name')} ขอให้วันนี้เป็นวันที่ดีสำหรับท่านค่ะ! \n ไม่ทราบว่าวันนี้ต้องการอะไรหรอกคะ?")
                display_chat()
                time.sleep(bot)
                st.session_state["bot_state"] = "active"
                update_status_display()
            else:
                self.add_to_history_bot_fisrt("ไม่ทราบว่าวันนี้ต้องการอะไรหรอกคะ?", '-')
                bot = update_chat_history("", "ไม่ทราบว่าวันนี้ต้องการอะไรหรอกคะ?")
                display_chat()
                time.sleep(bot)
                st.session_state["bot_state"] = "active"
                update_status_display()

    def get_time(self):
        now = datetime.now() + timedelta(hours=7) # for build
        #now = datetime.now()
        hours = now.strftime('%H นาฬิกา')
        minutes = now.strftime('%M')
        
        if minutes == "00":
            return f"ตอนนี้เวลา {hours}ตรง ค่ะ"
        else:
            return f"ตอนนี้เวลา {hours} {minutes} นาที ค่ะ"

    def process_input(self, user_input):
        user_input = user_input.strip()
        if user_input.endswith("ครับ"):
            return user_input[:-4].strip()
        elif user_input.endswith("คะ"):
            return user_input[:-2].strip()
        elif user_input.endswith("ค่ะ"):
            return user_input[:-3].strip()
        return user_input

    def chatbot_response(self, user_input):
        pronouns = ["ฉัน", "ผม", "เรา"]
        grouped_responses = {
            "สวัสดี": ["สวัสดี", "สวัสดีค่ะ", "หวัดดี", "ดี" , "โหล"],
            "คุณชื่ออะไร": ["คุณชื่ออะไร", "บอกชื่อหน่อย", "ชื่อของคุณ", "เธอชื่ออะไร"],
            "คุณเกิดที่ไหน" : ["คุณเกิดที่ไหน"],
            "รู้จักฉันไหม" : ["รู้จัก{}ไหม".format(pronoun) for pronoun in pronouns],
            "สองวันก่อนหน้าวันอะไร" : ["2 วันก่อนหน้าเป็น", "2 วันก่อนหน้าวัน"],
            "สองวันข้างหน้าหน้าวันอะไร" : ["2 วันข้างหน้าเป็น", "2 วันข้างหน้าวัน"],
            "ตอนนี้เวลา": ["ตอนนี้เวลา", "บอกเวลา", "เวลาเท่าไหร่", "ตอนนี้เวลากี่โมง", "เวลาเท่าไร", "เวลา", "ตอนนี้กี่โมง", "วันนี้กี่โมง"],
            "ฉันชื่ออะไร": ["{}ชื่ออะไร".format(pronoun) for pronoun in pronouns] +
                    ["บอกชื่อ{}".format(pronoun) for pronoun in pronouns] + 
                    ["{}ชื่อว่าอะไร".format(pronoun) for pronoun in pronouns] + 
                    ["ชื่อของ{}".format(pronoun) for pronoun in pronouns],
            "ฉันชื่อเล่นอะไร": ["{}ชื่อเล่นอะไร".format(pronoun) for pronoun in pronouns] +
                        ["บอกชื่อเล่น{}".format(pronoun) for pronoun in pronouns] +
                        ["{}ชื่อเล่นว่า".format(pronoun) for pronoun in pronouns] +
                        ["ชื่อเล่นของ{}คืออะไร".format(pronoun) for pronoun in pronouns] +
                        ["ชื่อเล่น{}คือ".format(pronoun) for pronoun in pronouns],
            "ฉันเกิดวันไหน": ["{}เกิดวันไหน".format(pronoun) for pronoun in pronouns] +
                      ["บอกวันเกิด{}".format(pronoun) for pronoun in pronouns] +
                      ["{}เกิดวันที่".format(pronoun) for pronoun in pronouns] +
                      ["วันไหน{}เกิด".format(pronoun) for pronoun in pronouns] +
                      ["{}เกิดตอนไหน".format(pronoun) for pronoun in pronouns] +
                      ["{}เกิดวันอะไร".format(pronoun) for pronoun in pronouns],
            "วันนี้วันอะไร" : ["วันนี้วันที่"]
        }

        additional_responses = {
            "สวัสดี": "สวัสดีค่ะ! มีอะไรให้ช่วยไหม?",
            "คุณชื่ออะไร": "ฉันคือ Chatbot ค่ะ",
            "คุณเกิดที่ไหน" : "ฉันไม่รู้ว่าตัวเองเกิดที่ไหนคะ",
            "สองวันก่อนหน้าวันอะไร": f"สองวันก่อนหน้าเป็น {self.get_thai_date(-2)} ค่ะ",
            "เมื่อวานวันอะไร": f"เมื่อวาน {self.get_thai_date(-1)} ค่ะ",
            "วันนี้วันอะไร": f"วันนี้ {self.get_thai_date(0)} ค่ะ",
            "พรุ่งนี้วันอะไร": f"พรุ่งนี้ {self.get_thai_date(1)} ค่ะ",
            "สองวันข้างหน้าหน้าวันอะไร": f"สองวันข้างหน้าเป็น {self.get_thai_date(2)} ค่ะ",
            "ตอนนี้เวลา": self.get_time(),
            "ฉันชื่ออะไร" : f"ท่านชื่อ {self.person_data[selected_person].get('name')} ค่ะ",
            "ฉันชื่อเล่นอะไร" : f"ท่านชื่อเล่นว่า {self.person_data[selected_person].get('nickname')} ค่ะ",
            "ฉันเกิดวันไหน" : f"ท่านเกิดวันที่ {self.person_data[selected_person].get('birthday')} ค่ะ",
            "รู้จักฉันไหม" : f"รู้จักค่ะ! ท่านชื่อ {self.person_data[selected_person].get('name')} ค่ะ"
        }

        self.responses.update(additional_responses)

        if any(op in user_input for op in ["+", "-", "*", "/"]) and any(char.isdigit() for char in user_input):
            response = calculate_ai(user_input)

            if not response.endswith("ค่ะ"):
                response += " ค่ะ"
            
            self.add_to_history(user_input, response)
            return response
        
        if ("แปลคำว่า" in user_input or "ช่วยแปลคำว่า" in user_input or "คำว่า" in user_input or "แปล" in user_input or "ช่วยแปล" in user_input or "ประโยค" in user_input) and ("ในภาษาอังกฤษคือ" in user_input or "ในภาษาอังกฤษ" in user_input or "ภาษาอังกฤษคือ" in user_input or "ภาษาอังกฤษ" in user_input or "ในภาษาอังกฤษคืออะไร" in user_input or "ภาษาอังกฤษคืออะไร" in user_input or "เป็นภาษาอังกฤษให้หน่อย" in user_input or "เป็นภาษาอังกฤษหน่อย" in user_input or "เป็นภาษาอังกฤษ" in user_input):
            user_input = self.process_input(user_input)
            response, text = word_translator(user_input)

            if not response.endswith("ค่ะ"):
                response += " ค่ะ"
            
            new_response = f"คำว่า '{text}' ในภาษาอังกฤษคือ {response}"
            self.add_to_history(user_input, new_response)
            return new_response

        if "สวัสดี" in user_input and ("คุณชื่ออะไร" in user_input or "เธอชื่ออะไร" in user_input):
            response = "สวัสดีค่ะ! ฉันชื่อ Chatbot ค่ะ"
            self.add_to_history(user_input, response)
            return response

        for response, keywords in grouped_responses.items():
            for keyword in keywords:
                if keyword in user_input:
                    self.add_to_history(user_input, self.responses[response])
                    return self.responses[response]

        for keyword in self.responses:
            if keyword in user_input:
                self.add_to_history(user_input, self.responses[keyword])
                return self.responses[keyword]

        response = "ขอโทษค่ะ ฉันไม่เข้าใจสิ่งที่ท่านพูด"
        self.add_to_history(user_input, response)
        return response

    def run_chatbot(self):
        st.session_state['messages'] = []
        st.session_state.text_received = []
        st.session_state['last_bot_state'] = ""
        st.session_state['unknown_question'] = None
        st.session_state['learning_answer'] = None
        st.session_state['updateInfo_stage'] = None
        display_chat()
        self.greet()

    def greet(self):
        if st.session_state['user_selected'].get('name'):
            st.session_state['last_bot_state'] = "greeting"
            st.session_state['bot_state'] = "prepare"
            update_status_display()
            st.session_state['greeting_response'] = f"สวัสดีค่ะ ใช่ ท่าน{chatbot.person_data[selected_person].get('name')} ไหมคะ"
            response = st.session_state['greeting_response']
            bot = update_chat_history("", response)
            display_chat()
            time.sleep(bot)
            st.session_state['bot_state'] = "greeting"
            update_status_display()

    def review_person_data(self):
        st.session_state['last_bot_state'] = "comfirmInfo"
        st.session_state['bot_state'] = "prepare"
        update_status_display()
        st.session_state['comfirmInfo_response'] = "ขอบคุณสำหรับข้อมูลค่ะ ข้อมูลที่ท่านให้มามีดังนี้\n"
    
        list_data = []
        for field in ['name', 'nickname', 'birthday']:
            text = ''
            if field == 'name':
                text = 'ชื่อ'
            elif field == 'nickname':
                text = 'ชื่อเล่น'
            elif field == 'birthday':
                text = 'วันเกิด'
            data = chatbot.person_data[selected_person].get(field, 'ไม่ทราบ')
            list_data.append(f"{text}: {data}")
            st.session_state['comfirmInfo_response'] += f"{text}: {data}\n"
        
        st.session_state['comfirmInfo_response'] += "ข้อมูลถูกต้องหรือไม่คะ?"
        bot = update_chat_history("", st.session_state['comfirmInfo_response'])
        display_chat()
        time.sleep(bot)

        st.session_state['bot_state'] = "comfirmInfo"
        update_status_display()

    def update_person_data(self):
        st.session_state['last_bot_state'] = "changeInfo"
        st.session_state['bot_state'] = "prepare"
        update_status_display()
        st.session_state['fixInfo_response'] = "ขอโทษค่ะ ขอข้อมูลที่ต้องการแก้ไขใหม่ค่ะ \n กรุณาพูดข้อมูลที่ต้องการแก้ไขค่ะ? (เช่น ชื่อ, ชื่อเล่น หรือ วันเกิด)"
        bot = update_chat_history("", st.session_state['fixInfo_response'])
        display_chat()
        time.sleep(bot)
        st.session_state['bot_state'] = "changeInfo"
        update_status_display()

chatbot = Chatbot()

#before bot process bot_state
if 'last_bot_state' not in st.session_state:
    st.session_state['last_bot_state'] = ""

#bot mode
if 'bot_state' not in st.session_state:
    st.session_state['bot_state'] = ""

#selection
if 'user_selected' not in st.session_state:
    st.session_state['user_selected'] = None

#update selection
if 'upadate_user_selected' not in st.session_state:
    st.session_state['upadate_user_selected'] = None

#message box
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

#user chat text
if 'text_received' not in st.session_state:
    st.session_state.text_received = []

#audio stage
if 'audio_stage' not in st.session_state:
    st.session_state['audio_stage'] = 1

#default greeting response
if 'greeting_response' not in st.session_state:
    if st.session_state['user_selected'] != None:
        st.session_state['greeting_response'] = f"สวัสดีค่ะ ใช่ ท่าน{st.session_state['user_selected'].get('name', 'ไม่ระบุ')} ไหมคะ"
    else:
        st.session_state['greeting_response'] = None

#default data person info
if 'comfirmInfo_response' not in st.session_state:
    st.session_state['comfirmInfo_response'] = ""

#default fixInfo question
if 'fixInfo_response' not in st.session_state:
    st.session_state['fixInfo_response'] = "ขอโทษค่ะ ขอข้อมูลที่ต้องการแก้ไขใหม่ค่ะ \n กรุณาพูดข้อมูลที่ต้องการแก้ไขค่ะ? (เช่น ชื่อ, ชื่อเล่น หรือ วันเกิด)"

#stage for update person data
if 'updateInfo_stage' not in st.session_state:
    st.session_state['updateInfo_stage'] = None

#store learning answer
if 'learning_answer' not in st.session_state:
    st.session_state['learning_answer'] = None

#store unknown question from user
if 'unknown_question' not in st.session_state:
    st.session_state['unknown_question'] = None

def update_status_display():
    status_text = st.session_state['bot_state']
    status_colors = {
        "": "#808080",        
        "greeting": "#4CAF50",
        "active": "#4CAF50",  
        "new_name": "#FF0000",
        "new_nickname": "#FF0000",
        "new_birthday": "#FF0000",
        "prepare": "#00BFFF",
        "comfirmInfo": "#4CAF50",
        "changeInfo" : "#FF0000",
        "learning_confirm": "#1bf7f4",
        "learning_mode": "#1bf7f4"
    }

    status_messages = {
        "": "ไม่ได้ทำงาน",
        "greeting": "โหมดทักทาย(พูดได้เลย)",
        "active": "โหมดปกติ(พูดได้เลย)",
        "new_name": "โหมดเก็บข้อมูล(พูดได้เลย)",
        "new_nickname": "โหมดเก็บข้อมูล(พูดได้เลย)",
        "new_birthday": "โหมดเก็บข้อมูล(พูดได้เลย)",
        "prepare": "กำลังประมวลผล...(ห้ามพูด)",
        "comfirmInfo": "โหมดยืนยัน(พูดได้เลย)",
        "changeInfo" : "โหมดแก้ไขข้อมูล(พูดได้เลย)",
        "learning_confirm": "โหมดยืนยันการเรียนรู้(พูดได้เลย)",
        "learning_mode": "โหมดการเรียนรู้(พูดได้เลย)"
    }

    status_placeholder.markdown(
        f"""
        <div style="text-align: center; padding: 5px; border-radius: 5px; background-color: {status_colors[status_text]}; color: white; font-size: 18px; font-weight: bold;">
            {status_messages[status_text]}
        </div>
        """,
        unsafe_allow_html=True
    )

def sound(html):
    if st.session_state['audio_stage'] == 1:
        sound_placeholder1.markdown(html, unsafe_allow_html=True)
        st.session_state['audio_stage'] = 2
    elif st.session_state['audio_stage'] == 2:
        sound_placeholder2.markdown(html, unsafe_allow_html=True)
        st.session_state['audio_stage'] = 3
    elif st.session_state['audio_stage'] == 3:
        sound_placeholder3.markdown(html, unsafe_allow_html=True)
        st.session_state['audio_stage'] = 4
    elif st.session_state['audio_stage'] == 4:
        sound_placeholder4.markdown(html, unsafe_allow_html=True)
        st.session_state['audio_stage'] = 5
    elif st.session_state['audio_stage'] == 5:
        sound_placeholder5.markdown(html, unsafe_allow_html=True)
        st.session_state['audio_stage'] = 1

def update_chat_history(user_message, bot_message):
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    if user_message != "":
        st.session_state['messages'].append(f'<div style="text-align: right;">👤: {user_message}</div>')
        st.session_state['audio_stage'] = 1

    if bot_message != "":
        audio_html, audio_lenght = chatbot.speak(bot_message)
        bot_message = bot_message.replace('\n', '<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')

        sound(audio_html)

        st.session_state['messages'].append(f'<div style="text-align: left;">🤖: {bot_message}</div>')
        return audio_lenght
            
def display_chat():
    with chat_placeholder:
        chat_html = "<br>".join(st.session_state['messages'])
        st.markdown(
            f"""
                <div id="chat-container" style="height: 45vh; overflow-y: auto; border: 3px solid #ccc; padding: 10px;">
                    {chat_html}
                </div>
                """,
                unsafe_allow_html=True
            )

def get_data():
    list_data = ""
    for field in ['name', 'nickname', 'birthday']:
        text = ''
        if field == 'name':
            text = 'ชื่อ'
        elif field == 'nickname':
            text = 'ชื่อเล่น'
        elif field == 'birthday':
            text = 'วันเกิด'
        data = chatbot.person_data[selected_person].get(field, 'ไม่ทราบ')
        list_data += (f"{text}: {data}\n")
    
    return list_data

with st.sidebar:
    selected = option_menu(
        menu_title= "Menu",
        options=["Home", 
                "Show history", 
                "Add personal data", 
                "Show personal data"],
        icons=["wechat", "clock-history", "database", "file-person"],
        menu_icon=["house-door-fill"],
        default_index=0,

    )

if selected == "Home":
    st.markdown(
        """
        <h1 style='text-align: center;'>🤖 Chatbot AI</h1>
        """, 
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 2])

    chatbot.person_data = chatbot.load_person_data()

    months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
          'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
    today = f"{datetime.now().day} {months[datetime.now().month - 1]}"

    display_names_today = []
    display_names_others = []
    person_keys_today = []
    person_keys_others = []

    for person_id, info in chatbot.person_data.items():
        birthday = " ".join(info['birthday'].split()[:2])
        display_name = f"ท่าน {info['name']}"
        if birthday == today:
            display_name += f"  :rainbow[--เกิดวันนี้--]"
            display_names_today.append(display_name)
            person_keys_today.append(person_id)
        else:
            display_names_others.append(display_name)
            person_keys_others.append(person_id)

    display_names = display_names_today + display_names_others
    person_keys = person_keys_today + person_keys_others

    id_name_mapping = {display_names[i]: person_keys[i] for i in range(len(display_names))}

    selected_display_name = st.radio("รายชื่อ", display_names)

    selected_person = id_name_mapping[selected_display_name]

    with col1:
        st.button("🎤Start & Reset", on_click= chatbot.run_chatbot)

    with col2:
        status_placeholder = st.empty()

    st.write("")
    microphone_st = speech_to_text(start_prompt="🎤 Talking", stop_prompt="Stop Talking", language='th', use_container_width=True, just_once=True, key='STT')

    chat_placeholder = st.empty()

    if selected_person:
        if st.session_state['user_selected'] == None:
            st.session_state['user_selected'] = chatbot.person_data.get(selected_person, {})
            update_status_display()
        else:
            if st.session_state['user_selected'] != chatbot.person_data.get(selected_person, {}):
                st.session_state['bot_state'] = ""
                st.session_state['last_bot_state'] = ""
                update_status_display()
                st.session_state['user_selected'] = chatbot.person_data.get(selected_person, {})
                st.session_state['last_bot_state'] = ""
                st.session_state['unknown_question'] = None
                st.session_state['learning_answer'] = None
                st.session_state['updateInfo_stage'] = None
                display_chat()
            else:
                update_status_display()

    col3, col4, col5, col6, col7 = st.columns([1,1,1,1,1])
    with col3:
        sound_placeholder1 = st.empty()
    with col4:
        sound_placeholder2 = st.empty()
    with col5:
        sound_placeholder3 = st.empty()
    with col6:
        sound_placeholder4 = st.empty()
    with col7:
        sound_placeholder5 = st.empty()
    display_chat()

    #when process interupt
    if st.session_state['bot_state'] == "prepare":
        st.session_state['bot_state'] = st.session_state['last_bot_state']
        update_status_display()

    if microphone_st:
        if st.session_state["bot_state"] == "prepare":
            update_status_display()
            pass

        elif st.session_state["bot_state"] == "active":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text: 
                st.session_state['last_bot_state'] = "active"
                st.session_state["bot_state"] = "prepare"
                update_status_display()
                chatbot_response = chatbot.chatbot_response(text)
                update_chat_history(text, "")
                display_chat()
                if "ขอบคุณ" in text:
                    bot= update_chat_history("",chatbot_response)
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = ""
                    update_status_display()
                
                elif "ขอโทษค่ะ ฉันไม่เข้าใจสิ่งที่ท่านพูด" in chatbot_response:
                    st.session_state['last_bot_state'] = "learning_confirm"
                    st.session_state['unknown_question'] = chatbot.process_input(text)
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("",chatbot_response)
                    display_chat()
                    time.sleep(bot)
                    bot = update_chat_history("","ท่านต้องการสอนฉันไหมคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "learning_confirm"
                    update_status_display()
                else:
                    bot = update_chat_history("",chatbot_response)
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "active"
                    update_status_display()
        
        elif st.session_state["bot_state"] == "learning_confirm":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if st.session_state['updateInfo_stage'] == "comfirmUpdate_learning":
                    if "ไม่ถูก" in text or "ไม่ใช่" in text or text == "ไม่" or "ผิด" in text or "ไม่ครับ" in text or "ไม่คะ" in text or "ไม่ค่ะ" in text:
                        st.session_state['last_bot_state'] = "learning_mode"
                        st.session_state['updateInfo_stage'] = None
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt(f"ท่านต้องการให้ฉันตอบคำถามนี้ว่า \n {st.session_state['learning_answer']} ใช่มั้ยคะ?", text)
                        st.session_state['learning_answer'] = None
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        bot = update_chat_history("", "ท่านต้องการสอนให้ฉันตอบคำถามนี้ว่าอะไรคะ?")
                        display_chat()
                        time.sleep(bot)
                        st.session_state['bot_state'] = "learning_mode"
                        update_status_display()
                        
                    elif "ใช่" in text or text == "ครับ" or text == "คะ" or text == "ค่ะ" or "ถูก" in text:
                        st.session_state['updateInfo_stage'] = None
                        st.session_state['last_bot_state'] = "active"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt(f"ท่านต้องการให้ฉันตอบคำถามนี้ว่า \n {st.session_state['learning_answer']} ใช่มั้ยคะ?", text)
                        if not st.session_state['learning_answer'].endswith("ค่ะ"):
                            st.session_state['learning_answer'] += " ค่ะ"
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        chatbot.responses[st.session_state['unknown_question']] = st.session_state['learning_answer']
                        chatbot.save_responses()
                        chatbot.responses = chatbot.load_responses()
                        st.session_state['unknown_question'] = None
                        st.session_state['learning_answer'] = None
                        bot = update_chat_history("", "ขอบคุณที่ให้ข้อมูลค่ะ ไม่ทราบว่าวันนี้ต้องการอะไรอีกมั้ยคะ?")
                        chatbot.add_to_history_bot_fisrt("ขอบคุณที่ให้ข้อมูลค่ะ ไม่ทราบว่าวันนี้ต้องการอะไรอีกมั้ยคะ?", "-")
                        display_chat()
                        time.sleep(bot)
                        st.session_state['bot_state'] = "active"
                        update_status_display()

                    else:
                        st.session_state['updateInfo_stage'] = "comfirmUpdate_learning"
                        st.session_state['last_bot_state'] = "learning_confirm"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt(f"ท่านต้องการให้ฉันตอบคำถามนี้ว่า \n {st.session_state['learning_answer']} ใช่มั้ยคะ?", text)
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        bot = update_chat_history("", f"ท่านต้องการให้ฉันตอบคำถามนี้ว่า \n {st.session_state['learning_answer']} ใช่มั้ยคะ?")
                        display_chat()
                        time.sleep(bot)
                        st.session_state["bot_state"] = "learning_confirm"
                        update_status_display()
                        
                else:
                    if "ไม่ต้องการ" in text or "ไม่อยากสอน" in text or text == "ไม่" or "ไม่สอน" in text or "ไม่ครับ" in text or "ไม่คะ" in text or "ไม่ค่ะ" in text:
                        st.session_state['last_bot_state'] = "active"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt("ท่านต้องการสอนฉันไหมคะ?", text)
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        bot = update_chat_history("","รับทราบค่ะ! ไม่ทราบว่าต้องการอะไรอีกมั้ยคะ?")
                        chatbot.add_to_history_bot_fisrt("รับทราบค่ะ! ไม่ทราบว่าต้องการอะไรอีกมั้ยคะ?", "-")
                        display_chat()
                        time.sleep(bot)
                        st.session_state["bot_state"] = "active"
                        update_status_display() 
                    elif "ใช่" in text or text == "ครับ" or text == "คะ" or text == "ค่ะ" or "ต้องการ" in text:
                        st.session_state['last_bot_state'] = "learning_mode"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt("ท่านต้องการสอนฉันไหมคะ?", text)
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        response = f"ท่านต้องการสอนให้ฉันตอบคำถามนี้ว่าอะไรคะ?"
                        bot = update_chat_history("", response)
                        display_chat()
                        time.sleep(bot)
                        st.session_state["bot_state"] = "learning_mode"
                        update_status_display()
                    else:
                        st.session_state['last_bot_state'] = "learning_confirm"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt("ท่านต้องการสอนฉันไหมคะ?", text)
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        bot = update_chat_history("", "ท่านต้องการสอนฉันไหมคะ?")
                        display_chat()
                        time.sleep(bot)
                        st.session_state['bot_state'] = "learning_confirm"
                        update_status_display()

        elif st.session_state["bot_state"] == "learning_mode":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                st.session_state['last_bot_state'] = "learning_confirm"
                st.session_state['updateInfo_stage'] = "comfirmUpdate_learning"
                update_chat_history(text, "")
                display_chat()
                chatbot.add_to_history_bot_fisrt("รับทราบค่ะ! ท่านต้องการสอนให้ฉันตอบคำถามนี้ว่าอะไรคะ?", text)
                st.session_state['learning_answer'] = chatbot.process_input(text)
                st.session_state["bot_state"] = "prepare"
                update_status_display()
                bot = update_chat_history("", f"ท่านต้องการให้ฉันตอบคำถามนี้ว่า \n {st.session_state['learning_answer']} ใช่มั้ยคะ?")
                display_chat()
                time.sleep(bot)
                st.session_state["bot_state"] = "learning_confirm"
                update_status_display()

        elif st.session_state["bot_state"] == "greeting":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if "ไม่ใช่" in text or "ผิด" in text or text == "ไม่" or "ไม่ครับ" in text or "ไม่คะ" in text or "ไม่ค่ะ" in text:
                    st.session_state['last_bot_state'] = "new_name"
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['greeting_response'], text)
                    bot = update_chat_history("", "ขอโทษค่ะ ไม่ทราบว่าชื่ออะไรหรอคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "new_name"
                    update_status_display()
                elif "ใช่" in text or text == "ครับ" or text == "คะ" or text == "ค่ะ":
                    st.session_state['last_bot_state'] = "active"
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['greeting_response'], text)
                    chatbot.check_birthday()
                else:
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['greeting_response'], text)
                    st.session_state['last_bot_state'] = "greeting"
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    st.session_state['greeting_response'] = f"สวัสดีค่ะ ไม่ทราบว่าใช่ ท่าน{chatbot.person_data[selected_person].get('name')} ไหมคะ"
                    bot = update_chat_history("", st.session_state['greeting_response'])
                    display_chat()
                    time.sleep(bot)
                    st.session_state['bot_state'] = "greeting"
                    update_status_display()

        elif st.session_state["bot_state"] == "new_name":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if st.session_state['updateInfo_stage'] == "name":
                    st.session_state['last_bot_state'] = "comfirmInfo"
                    st.session_state['updateInfo_stage'] = "comfirmUpdate_name"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt("ชื่อของท่านคืออะไรคะ?", text)
                    chatbot.person_data[selected_person]['name']  = chatbot.process_input(text)
                    if "ชื่อ" in chatbot.process_input(text):
                        name = chatbot.process_input(text).replace("ชื่อ", "")
                        chatbot.person_data[selected_person]['name'] = name
                    chatbot.save_person_data()
                    chatbot.person_data = chatbot.load_person_data()
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", f"ท่านชื่อว่า {chatbot.person_data[selected_person].get('name')} ถูกต้องใช่มั้ยคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "comfirmInfo"
                    update_status_display()
                else:
                    st.session_state['last_bot_state'] = "new_nickname"
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt("ขอโทษค่ะ ไม่ทราบว่าชื่ออะไรหรอคะ?", text)
                    chatbot.person_data[selected_person]['name'] = chatbot.process_input(text)
                    if "ชื่อ" in chatbot.process_input(text):
                        name = chatbot.process_input(text).replace("ชื่อ", "")
                        chatbot.person_data[selected_person]['name'] = name
                    chatbot.save_person_data()
                    bot = update_chat_history("", "ชื่อเล่นของท่านคืออะไรคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "new_nickname"
                    update_status_display()

        elif st.session_state["bot_state"] == "new_nickname":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if st.session_state['updateInfo_stage'] == "nickname":
                    st.session_state['last_bot_state'] = "comfirmInfo"
                    st.session_state['updateInfo_stage'] = "comfirmUpdate_nickname"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt("ชื่อเล่นของท่านคืออะไรคะ?", text)
                    chatbot.person_data[selected_person]['nickname'] = chatbot.process_input(text)
                    if "ชื่อ" in chatbot.process_input(text):
                        nickname = chatbot.process_input(text).replace("ชื่อ", "")
                        chatbot.person_data[selected_person]['nickname'] == nickname
                    chatbot.save_person_data()
                    chatbot.person_data = chatbot.load_person_data()
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", f"ท่านชื่อเล่นว่า{chatbot.person_data[selected_person].get('nickname')} ถูกต้องใช่มั้ยคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "comfirmInfo"
                    update_status_display()
                else:
                    st.session_state['last_bot_state'] = "new_birthday"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt("ชื่อเล่นของท่านคืออะไรคะ?", text)
                    chatbot.person_data[selected_person]['nickname'] = chatbot.process_input(text)
                    if "ชื่อ" in chatbot.process_input(text):
                        nickname = chatbot.process_input(text).replace("ชื่อ", "")
                        chatbot.person_data[selected_person]['nickname'] = nickname
                    chatbot.save_person_data()
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", "วันเกิดของท่านคืออะไรคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "new_birthday"
                    update_status_display()

        elif st.session_state["bot_state"] == "new_birthday":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if st.session_state['updateInfo_stage'] == "birthday":
                    st.session_state['last_bot_state'] = "comfirmInfo"
                    st.session_state['updateInfo_stage'] = "comfirmUpdate_birthday"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt("วันเกิดของท่านคืออะไรคะ?", text)
                    chatbot.person_data[selected_person]['birthday'] = chatbot.process_input(text)
                    if "วันที่" in chatbot.process_input(text):
                        date = chatbot.process_input(text).replace("วันที่", "")
                        chatbot.person_data[selected_person]['birthday'] = date
                    chatbot.save_person_data()
                    chatbot.person_data = chatbot.load_person_data()
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", f"ท่านเกิด {chatbot.person_data[selected_person].get('birthday')} ถูกต้องใช่มั้ยคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "comfirmInfo"
                    update_status_display()
                else:
                    st.session_state['last_bot_state'] = "comfirmInfo"
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt("วันเกิดของท่านคืออะไรคะ?", text)
                    chatbot.person_data[selected_person]['birthday'] = chatbot.process_input(text)
                    if "วันที่" in chatbot.process_input(text):
                        date = chatbot.process_input(text).replace("วันที่", "")
                        chatbot.person_data[selected_person]['birthday'] = date
                    chatbot.save_person_data()

                    chatbot.person_data = chatbot.load_person_data()

                    chatbot.review_person_data()
        
        elif st.session_state["bot_state"] == "comfirmInfo":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if st.session_state['updateInfo_stage'] == "comfirmUpdate_name" or st.session_state['updateInfo_stage'] == "comfirmUpdate_nickname" or st.session_state['updateInfo_stage'] == "comfirmUpdate_birthday":
                    if "ไม่ถูก" in text or "ไม่ใช่" in text or text == "ไม่" or "ไม่ครับ" in text or "ไม่คะ" in text or "ไม่ค่ะ" in text:
                        update_chat_history(text, "")
                        display_chat()
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        if st.session_state['updateInfo_stage'] == "comfirmUpdate_name":
                            st.session_state['last_bot_state'] = "new_name"
                            st.session_state['updateInfo_stage'] = "name"
                            chatbot.add_to_history_bot_fisrt(f"ท่านชื่อว่า {chatbot.person_data[selected_person].get('name')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", "ชื่อของท่านคืออะไรคะ?")
                            display_chat()
                            time.sleep(bot)
                            st.session_state['bot_state'] = "new_name"
                            update_status_display()
                        elif st.session_state['updateInfo_stage'] == "comfirmUpdate_nickname":
                            st.session_state['last_bot_state'] = "new_nickname"
                            st.session_state['updateInfo_stage'] = "nickname"
                            chatbot.add_to_history_bot_fisrt(f"ท่านชื่อเล่นว่า {chatbot.person_data[selected_person].get('nickname')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", "ชื่อเล่นของท่านคืออะไรคะ?")
                            display_chat()
                            time.sleep(bot)
                            st.session_state['bot_state'] = "new_nickname"
                            update_status_display()
                        elif st.session_state['updateInfo_stage'] == "comfirmUpdate_birthday":
                            st.session_state['last_bot_state'] = "new_birthday"
                            st.session_state['updateInfo_stage'] = "birthday"
                            chatbot.add_to_history_bot_fisrt(f"ท่านเกิด {chatbot.person_data[selected_person].get('birthday')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", "วันเกิดของท่านคืออะไรคะ?")
                            display_chat()
                            time.sleep(bot)
                            st.session_state['bot_state'] = "new_birthday"
                            update_status_display()

                    elif "ใช่" in text or text == "ครับ" or text == "คะ" or text == "ค่ะ" or "ถูก" in text:
                        st.session_state['last_bot_state'] = "active"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.save_person_data()
                        if st.session_state['updateInfo_stage'] == "comfirmUpdate_name":
                            st.session_state['updateInfo_stage'] = None
                            chatbot.add_to_history_bot_fisrt(f"ท่านชื่อว่า {chatbot.person_data[selected_person].get('name')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", f"เข้าใจแล้วค่ะ! สวัสดีค่ะ ท่าน{chatbot.person_data[selected_person].get('name')}")
                            chatbot.add_to_history_bot_fisrt(f"เข้าใจแล้วค่ะ! สวัสดีค่ะ ท่าน{chatbot.person_data[selected_person].get('name')}", "-")
                            display_chat()
                            time.sleep(bot)
                            chatbot.check_birthday()
                        elif st.session_state['updateInfo_stage'] == "comfirmUpdate_nickname":
                            st.session_state['updateInfo_stage'] = None
                            chatbot.add_to_history_bot_fisrt(f"ท่านชื่อเล่นว่า {chatbot.person_data[selected_person].get('nickname')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", f"เข้าใจแล้วค่ะ! สวัสดีค่ะ ท่าน{chatbot.person_data[selected_person].get('nickname')}")
                            chatbot.add_to_history_bot_fisrt(f"เข้าใจแล้วค่ะ! สวัสดีค่ะ ท่าน{chatbot.person_data[selected_person].get('nickname')}", "-")
                            display_chat()
                            time.sleep(bot)
                            chatbot.check_birthday()
                        elif st.session_state['updateInfo_stage'] == "comfirmUpdate_birthday":
                            st.session_state['updateInfo_stage'] = None
                            chatbot.add_to_history_bot_fisrt(f"ท่านเกิด {chatbot.person_data[selected_person].get('birthday')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", f"เข้าใจแล้วค่ะ! ท่านเกิด {chatbot.person_data[selected_person].get('birthday')}")
                            chatbot.add_to_history_bot_fisrt(f"เข้าใจแล้วค่ะ! ท่านเกิด {chatbot.person_data[selected_person].get('birthday')}", "-")
                            display_chat()
                            time.sleep(bot)
                            chatbot.check_birthday()
                    
                    else:
                        st.session_state['last_bot_state'] = "comfirmInfo"
                        update_chat_history(text, "")
                        display_chat()
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        if st.session_state['updateInfo_stage'] == "comfirmUpdate_name":
                            st.session_state['updateInfo_stage'] = "comfirmUpdate_name"
                            chatbot.add_to_history_bot_fisrt(f"ท่านชื่อว่า {chatbot.person_data[selected_person].get('name')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", f"ท่านชื่อว่า {chatbot.person_data[selected_person].get('name')} ถูกต้องใช่มั้ยคะ?")
                            display_chat()
                            time.sleep(bot)
                        elif st.session_state['updateInfo_stage'] == "comfirmUpdate_nickname":
                            st.session_state['updateInfo_stage'] = "comfirmUpdate_nickname"
                            chatbot.add_to_history_bot_fisrt(f"ท่านชื่อเล่นว่า {chatbot.person_data[selected_person].get('nickname')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", f"ท่านชื่อเล่นว่า {chatbot.person_data[selected_person].get('nickname')} ถูกต้องใช่มั้ยคะ?")
                            display_chat()
                            time.sleep(bot)
                        elif st.session_state['updateInfo_stage'] == "comfirmUpdate_birthday":
                            st.session_state['updateInfo_stage'] = "comfirmUpdate_birthday"
                            chatbot.add_to_history_bot_fisrt(f"ท่านเกิด {chatbot.person_data[selected_person].get('birthday')} ถูกต้องใช่มั้ยคะ?", text)
                            bot = update_chat_history("", f"ท่านเกิด {chatbot.person_data[selected_person].get('birthday')} ถูกต้องใช่มั้ยคะ?")
                            display_chat()
                            time.sleep(bot)
                        st.session_state['bot_state'] = "comfirmInfo"
                        update_status_display()
                else:
                    if "ขออีก" in text or "ทวน" in text or "พูดอีก" in text or "พูดใหม่" in text or "ขอใหม่" in text:
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt(st.session_state['comfirmInfo_response'], text)
                        list_data = get_data()
                        st.session_state['last_bot_state'] = "comfirmInfo"
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        response = f"ได้ค่ะ!\n {list_data} ข้อมูลถูกต้องมั้ยคะ?"
                        bot = update_chat_history("", response)
                        display_chat()
                        time.sleep(bot)
                        st.session_state['bot_state'] = "comfirmInfo"
                        update_status_display()

                    if "ไม่ถูก" in text or "ไม่ใช่" in text or text == "ไม่" or "ไม่ครับ" in text or "ไม่คะ" in text or "ไม่ค่ะ" in text:
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt(st.session_state['comfirmInfo_response'], text)
                        chatbot.update_person_data()
                        
                    elif "ใช่" in text or text == "ครับ" or text == "คะ" or text == "ค่ะ" or "ถูก" in text:
                        st.session_state['last_bot_state'] = "active"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.save_person_data()
                        chatbot.add_to_history_bot_fisrt(st.session_state['comfirmInfo_response'], text)
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        response = f"เข้าใจแล้วค่ะ! สวัสดีค่ะ {chatbot.person_data[selected_person].get('nickname')} ยินดีที่ได้รู้จักค่ะ!"
                        chatbot.add_to_history_bot_fisrt(st.session_state['comfirmInfo_response'], "-")
                        bot = update_chat_history("", response)
                        display_chat()
                        time.sleep(bot)
                        chatbot.check_birthday()
                    else:
                        st.session_state['last_bot_state'] = "comfirmInfo"
                        update_chat_history(text, "")
                        display_chat()
                        chatbot.add_to_history_bot_fisrt(st.session_state['comfirmInfo_response'], text)
                        st.session_state["bot_state"] = "prepare"
                        update_status_display()
                        comfirmInfo_response = "ข้อมูลถูกต้องมั้ยคะ?"
                        bot = update_chat_history("", comfirmInfo_response)
                        display_chat()
                        time.sleep(bot)
                        st.session_state['bot_state'] = "comfirmInfo"
                        update_status_display()

        elif st.session_state["bot_state"] == "changeInfo":
            st.session_state.text_received.append(microphone_st)
            text = st.session_state.text_received[-1]
            if text:
                if "ชื่อเล่น" in text:
                    st.session_state['last_bot_state'] = "new_nickname"
                    st.session_state['updateInfo_stage'] = "nickname"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['fixInfo_response'], text)
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", "ชื่อเล่นของท่านคืออะไรคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "new_nickname"
                    update_status_display()
                elif "วันเกิด" in text:
                    st.session_state['last_bot_state'] = "new_birthday"
                    st.session_state['updateInfo_stage'] = "birthday"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['fixInfo_response'], text)
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", "วันเกิดของท่านคืออะไรคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "new_birthday"
                    update_status_display()
                elif "ชื่อ" in text:
                    st.session_state['last_bot_state'] = "new_name"
                    st.session_state['updateInfo_stage'] = "name"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['fixInfo_response'], text)
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    bot = update_chat_history("", "ชื่อของท่านคืออะไรคะ?")
                    display_chat()
                    time.sleep(bot)
                    st.session_state["bot_state"] = "new_name"
                    update_status_display()
                else:
                    st.session_state['last_bot_state'] = "changeInfo"
                    update_chat_history(text, "")
                    display_chat()
                    chatbot.add_to_history_bot_fisrt(st.session_state['fixInfo_response'], text)
                    st.session_state["bot_state"] = "prepare"
                    update_status_display()
                    comfirmInfo_response = "ขอโทษค่ะ ต้องการเปลี่ยนข้อมูลตรงไหนคะ? (ชื่อ, ชื่อเล่น หรือ วันเกิด)"
                    bot = update_chat_history("", comfirmInfo_response)
                    display_chat()
                    time.sleep(bot)
                    st.session_state['bot_state'] = "changeInfo"
                    update_status_display()

elif selected == "Show history":
    user_data = chatbot.load_person_data()
    user_id = st.selectbox("เลือกอาจารย์", options=list(user_data.keys()), format_func=lambda x: f"ท่าน {user_data[x]['name']}")

    if user_id:
        chatbot.show_history_json_as_table(f"ท่าน {user_data[user_id]['name']}", chatbot.history, user_id)

elif selected == "Add personal data":
    status = st.empty()
    st.markdown(f"<h2 style='font-size:28px;'>เพิ่มข้อมูลอาจารย์</h2>", unsafe_allow_html=True)
    name = st.text_input("ชื่อ", value="", key="add_name")
    nickname = st.text_input("ชื่อเล่น", value="", key="add_nickname")
    birthday = st.text_input("วันเกิด", value="", key="add_birthday")

    def clear_input():
        if not name or not nickname or not birthday:
            status.error("กรุณากรอกข้อมูลให้ครบทุกช่อง")
            time.sleep(1)
            status.empty()
            return
        new_person_id = f"{len(chatbot.person_data) + 1}"
        chatbot.person_data[new_person_id] = {
            'name': name,
            'nickname': nickname,
            'birthday': birthday
        }
        chatbot.save_person_data()
        st.session_state["add_name"] = ""
        st.session_state["add_nickname"] = ""
        st.session_state["add_birthday"] = ""
        status.success("บันทึกสำเร็จ!")
        time.sleep(0.5)
        status.empty()

    st.button("บันทึกข้อมูล", on_click=clear_input)
        
elif selected == "Show personal data":
    st.markdown(f"<h2 style='font-size:28px;'>แก้ไขข้อมูลอาจารย์</h2>", unsafe_allow_html=True)

    chatbot.person_data = chatbot.load_person_data()

    display_names = [f"ท่าน {info['name']}" for info in chatbot.person_data.values()]
    person_ids = list(chatbot.person_data.keys())

    id_name_mapping = {f"ท่าน {info['name']}": person_id for person_id, info in chatbot.person_data.items()}

    selected_display_name = st.selectbox("เลือกบุคคลที่ต้องการแก้ไขข้อมูล", display_names)

    selected_person = id_name_mapping[selected_display_name]
    
    if selected_person:
        st.session_state['upadate_user_selected'] = selected_person
        person_info = chatbot.person_data.get(selected_person, {})
        name = st.text_input("ชื่อ", value=person_info.get('name', ''))
        nickname = st.text_input("ชื่อเล่น", value=person_info.get('nickname', ''))
        birthday = st.text_input("วันเกิด", value=person_info.get('birthday', ''))


        if st.button("บันทึกข้อมูล"):
            chatbot.person_data[selected_person] = {
                'name': name,
                'nickname': nickname,
                'birthday': birthday
            }
            chatbot.save_person_data() 
            st.success("Success!")
            time.sleep(0.5)
            st.rerun()
