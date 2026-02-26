from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    TempDirectoryPath,
    ShowTextToScreen,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

from dotenv import dotenv_values
from time import sleep
from asyncio import run
import threading
import subprocess
import json
import os

# -------------------- ENV --------------------
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")

DefaultMessage = f"""{Username} : Hello {Assistantname}
{Assistantname} : Hello {Username}, how can I help you?"""

Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
processes = []

# -------------------- CHAT INIT --------------------
def ShowDefaultChatIfNoChats():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as f:
            if len(f.read()) > 5:
                return
    except:
        pass

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as f:
        f.write("")
    with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as f:
        f.write(DefaultMessage)

def ChatLogIntegration():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return

    formatted = ""
    for e in data:
        role = Username if e["role"] == "user" else Assistantname
        formatted += f"{role} : {e['content']}\n"

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as f:
        f.write(AnswerModifier(formatted))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as f:
            text = f.read()
        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as f:
            f.write(text)
    except:
        pass

# -------------------- STARTUP --------------------
def InitialExecution():
    SetMicrophoneStatus("False")
    SetAssistantStatus("Available...")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

# -------------------- MAIN AI LOGIC --------------------
def MainExecution():
    SetMicrophoneStatus("False")
    SetAssistantStatus("Listening...")

    Query = SpeechRecognition()
    if not Query:
        SetAssistantStatus("Available...")
        return

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")

    Decision = FirstLayerDMM(Query)

    # 🔧 Automation
    for q in Decision:
        if any(q.startswith(f) for f in Functions):
            run(Automation(Decision))
            break

    # 🔍 Realtime
    for q in Decision:
        if q.startswith("realtime"):
            SetAssistantStatus("Searching...")
            final = q.replace("realtime ", "")
            Answer = RealtimeSearchEngine(QueryModifier(final))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            SetAssistantStatus("Available...")
            return

    # 💬 General Chat
    for q in Decision:
        if q.startswith("general"):
            final = q.replace("general ", "")
            Answer = ChatBot(QueryModifier(final))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            SetAssistantStatus("Available...")
            return

# -------------------- BACKGROUND THREAD --------------------
def VoiceLoop():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        sleep(0.1)

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    InitialExecution()

    threading.Thread(target=VoiceLoop, daemon=True).start()

    # GUI MUST be in main thread
    GraphicalUserInterface()
