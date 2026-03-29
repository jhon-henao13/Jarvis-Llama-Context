import os
import webbrowser
import subprocess
import pyttsx3
import speech_recognition as sr
from groq import Groq
import json
from datetime import datetime
import requests
import pyautogui
import time
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN ---
MODEL_IA = "llama-3.1-8b-instant" 
# Ahora leemos la API de forma segura
GROQ_API_KEY = os.getenv("API")
client = Groq(api_key=GROQ_API_KEY) 
USER_NAME = "Señor Estiguar"
CITY = "Cali"

# Memoria de contexto (Guarda los últimos 5 intercambios)
context_history = []

def speak(text):
    print(f"Jarvis: {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 195)
        voices = engine.getProperty('voices')
        for voice in voices:
            if "spanish" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Error en voz: {e}")

def get_weather():
    try:
        res = requests.get(f"https://wttr.in/{CITY}?format=%t+%C", timeout=5)
        return res.text.replace("+", " ")
    except:
        return "clima tropical, como siempre"

def listen():
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    with sr.Microphone() as source:
        print("\n[Escuchando...]")
        r.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = r.listen(source, timeout=None, phrase_time_limit=7)
            query = r.recognize_google(audio, language="es-ES")
            print(f"Tú: {query}")
            return query
        except:
            return ""

def get_intent_with_context(user_input):
    global context_history
    
    # Construir el prompt con historia
    history_str = "\n".join([f"Usuario: {h['u']}\nJarvis: {h['j']}" for h in context_history])
    
    prompt = f"""
    Eres JARVIS, la IA avanzada de Tony Stark. Eres profesional, irónico a veces, pero muy leal.
    Usuario: {USER_NAME}. Ubicación: {CITY}.
    
    HISTORIAL RECIENTE:
    {history_str}


    REGLAS DE ORO:
    1. Si el usuario pide reproducir/poner música, extrae EL NOMBRE REAL de la canción.
    2. NUNCA pongas "historial" o "comando" en el campo 'search'. 
    3. Si el usuario dice "ponla", busca en el historial de arriba qué canción era y pon el nombre real en 'search'.

    
    CATEGORÍAS: 'PROGRAMMING', 'MUSIC', 'TIME', 'WEATHER', 'CHAT', 'CMD', 'OFF'.
    
    Responde SOLO JSON: 
    {{
      "intent": "CATEGORIA", 
      "search": "busqueda_o_comando", 
      "reply": "respuesta_estilo_jarvis"
    }}
    
    NOTAS:
    - Si pide abrir algo general (calculadora, notepad, settings) usa CMD.


    - Si el usuario dice "ponme", "reproduce", "escuchar" o "busca la canción", usa intent: 'MUSIC'.
    - En el campo 'search', pon SOLO el nombre y artista. Ejemplo: "Sweet Child O Mine Guns N Roses".
    - Si solo pide abrir Youtube Music sin una canción específica, pon 'search': 'homepage'.

    - Mantén la continuidad: si el usuario dice "hazlo", mira el historial.
    
    Usuario dice ahora: "{user_input}"
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_IA,
            response_format={"type": "json_object"}
        )
        res = json.loads(chat_completion.choices[0].message.content)
        
        # Guardar en memoria
        context_history.append({"u": user_input, "j": res['reply']})
        if len(context_history) > 5: context_history.pop(0)
        
        return res
    except:
        return {"intent": "CHAT", "search": "", "reply": "Mis sistemas están procesando mucha información, señor."}

def execute_action(data):
    intent = data.get("intent", "CHAT")
    search = data.get("search", "")
    reply = data.get("reply", "A sus órdenes.")

    if intent == "PROGRAMMING":
        speak(reply)
        try:
            subprocess.Popen(["C:/Program Files/Sublime Text/sublime_text.exe"])
        except: pass
        webbrowser.open("https://gemini.google.com")
        os.startfile(r"C:\Users\Servi\Documents")


    elif intent == "MUSIC":
        if search == "homepage" or not search:
            speak(f"Abriendo su biblioteca de música, {USER_NAME}.")
            webbrowser.open("https://music.youtube.com")
        else:
            speak(f"Entendido, señor. Iniciando la frecuencia para {search}.")
            search_query = search.replace(" ", "+")
            
            # Usamos YouTube normal con filtro de 'video' para que el primer resultado sea el correcto
            url = f"https://www.youtube.com/results?search_query={search_query}+audio"
            webbrowser.open(url)
            
            # --- RUTINA DE AUTOPLAY STARK ---
            # Esperamos 5 segundos a que el navegador abra y cargue la página
            time.sleep(5) 
            
            # 1. Presionamos 'Tab' para entrar al área de resultados y 'Enter' en el primero
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.press('enter')
            
            # 2. Esperamos a que cargue el video y presionamos 'k' (tecla universal de Play en YouTube)
            time.sleep(3)
            pyautogui.press('k') 
            # --------------------------------


    elif intent == "CMD":
        speak(reply)
        search_cmd = search.lower()
        try:
            if "word" in search_cmd:
                os.system("start winword") # Comando directo de Windows para Word
            elif "excel" in search_cmd:
                os.system("start excel")
            elif "calculadora" in search_cmd or "calc" in search_cmd:
                subprocess.Popen("calc.exe")
            elif "google" in search_cmd or "chrome" in search_cmd:
                webbrowser.open("https://www.google.com")
            else:
                os.system(f"start {search_cmd}")
        except:
            speak(f"Señor, el protocolo {search_cmd} no respondió como esperaba.")


    elif intent == "TIME":
        hora = datetime.now().strftime("%I:%M %p")
        speak(f"{reply} Son las {hora}.")

    elif intent == "WEATHER":
        clima = get_weather()
        speak(f"{reply}. El reporte para {CITY} indica {clima}.")

    elif intent == "CHAT":
        speak(reply)

    elif intent == "OFF":
        speak(reply)
        exit()

# --- MAIN ---
if __name__ == "__main__":
    hora_actual = datetime.now().strftime("%I:%M %p")
    speak(f"Protocolos listos. Son las {hora_actual}. ¿En qué puedo servirle, Señor Estiguar?")
    
    while True:
        try:
            text = listen()
            if text and len(text) > 2:
                intent_data = get_intent_with_context(text)
                execute_action(intent_data)
        except Exception as e:
            print(f"Error: {e}")
            continue