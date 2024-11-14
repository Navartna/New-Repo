import datetime
import os
import sys
import pyautogui
import time
import webbrowser
import pyttsx3
import speech_recognition as sr
import json
import pickle
import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import numpy as np
import psutil

with open("intents.json") as file:
    data=json.load(file)
model=keras.models.load_model("chat_model.h5")
with open("tokenizer.pkl", "rb") as f:
    tokenizer=pickle.load(f)

with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder=pickle.load(encoder_file)


def initialize_engine():
    engine=pyttsx3.init("sapi5")
    voices=engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate=engine.getProperty('rate')
    engine.setProperty('rate', rate-50)
    volume=engine.getProperty('volume')
    engine.setProperty('volume', volume+0.25)
    return engine

def speak(text):
    engine=initialize_engine()
    engine.say(text)
    engine.runAndWait()

def command():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...", end="", flush=True)
        r.pause_threshold=1.0
        r.phrase_threshold=0.3
        r.sample_rate=48000
        r.dynamic_energy_threshold=True
        r.operation_timeout=5
        r.non_speaking_duration=0.5
        r.dynamic_energy_adjustment=2
        r.energy_threshold=4000
        r.phrase_time_limit=10
        #print(sr.Microphone.list_microphone_names())
        audio=r.listen(source)
        try:
            print("\r",end="",flush=True)
            print("Recognizing...",end="", flush=True)
            query=r.recognize_google(audio, language='en-in')
            print("\r",end="",flush=True)
            print(f"User said :{query}\n")
        except Exception as e:
            print("Say that again please")    
            return "None"
        return query 

def cal_day():
    day=datetime.datetime.today().weekday()+1
    day_dict={
        1:"Monday",
        2:"Tuesday",
        3:"Wednesday",
        4:"Thursday",
        5:"Friday",
        6:"Saturday",
        7:"Sunday"
    }
    if day in day_dict.keys():
        day_of_week=day_dict[day]
        print(day_of_week)
    return day_of_week    

def openApp(command):
     
    if "google chrome" in command:
        speak("Opening google chrome")
        os.startfile("C:\Program Files\Google\Chrome\Application\chrome.exe")      
    else:
        speak("This application is not added in the list")   

def closeApp(command):
    if "close google chrome" in command:
        speak("closing google chrome")
        os.system('taskkill /f /im chrome.exe')
    else:
        speak("This application is not running in the list") 
            
def condition():
    usage=str(psutil.cpu_percent())
    speak(f"Cpu is at {usage} percentage")
    battery=psutil.sensors_battery()
    percentage=battery.percent
    speak(f"System has {percentage} percent battery remaining")


def wishMe():
    hour=datetime.datetime.now().hour
    t=time.strftime("%I:%M:%p")
    day=cal_day()

    if(hour>=0) and (hour<=12) and ('AM' in t):
        speak(f"Good Morning Sir, It's {day} and the time is {t}")
    elif(hour>=12) and (hour<=16) and ('PM' in t):
        speak(f"Good afternoon Sir, It's {day} and the time is {t}")
    else:
        speak(f"Good Evening Sir, It's {day} and the time is {t}")        

def browsing(query):
    if 'google' in query:
        speak("Sir, What should i search on google..")
        s=command().lower()
        webbrowser.open(f"{s}")

def social_media(command):
    if 'facebook' in command:
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com/")
    elif 'instagram' in command:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com/")    
    elif 'youtube' in command:
        speak("Opening Youtube") 
        webbrowser.open("https://www.youtube.com/")

    else:
        speak("No result found")    


if __name__=="__main__":
    wishMe()
    while True:
        query=command().lower()     
        #query=input("Enter your command->")
        if('facebook' in query) or ('instagram' in query) or ('youtube' in query):
            social_media(query)
        elif ("volume up" in query) or ("increaase volume" in query):
            pyautogui.press("volumeup")
            speak("Volume increased")   
        elif ("volume down" in query) or ("decrease volume" in query):
            pyautogui.press("volumedown")
            speak("Volume Decreased") 
        elif ("volume mute" in query) or ("Mute the sound" in query):
            pyautogui.press("volumemute")
            speak("Volume Muted")     

        elif ("open google chrome" in query):
            openApp(query)
        elif ("close google chrome" in query):
            closeApp(query)  
        elif ("what" in query ) or ("who" in query) or ("how" in query) or  ("Hi" in query)  or ("thanks" in query) or ("hello" in query):
            padded_sequences=pad_sequences(tokenizer.texts_to_sequences([query]), maxlen=20, truncating='post')
            result=model.predict(padded_sequences)
            tag=label_encoder.inverse_transform([np.argmax(result)])
    
            for i in data['intents']:
                if i['tag']==tag:
                 speak(np.random.choice(i['responses']))

        elif ("open google" in query):
            browsing(query)

        elif ("system condition" in query) or ("condition of the system" in query):
            speak("Checking the system condition")
            condition()
        elif "exit" in query:
            sys.exit()      
        




#speak("Hello, I'm Jarvis")    