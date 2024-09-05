import tkinter as tk
from tkinter import Text, Entry, Button, Label, StringVar, OptionMenu
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time
import threading

class SpeechApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Speech-to-Text and Text-to-Speech")
        self.language_codes = {
            "English": "en",
            "Hindi": "hi",
            "Gujrati": "gu",
            "Bengali": "bn",
            "Marathi": "mr",
            "Odia": "or",
            "Tamil": "ta",
            "Telugu": "te",
            "Urdu": "ur"
        }

        pygame.mixer.init()  # Initialize pygame mixer

        self.setup_gui()

    def setup_gui(self):
        self.labelSTT = Label(self.master, text="Speech-to-Text")
        self.labelSTT.pack()

        self.textSTT = Text(self.master, height=5, width=50)
        self.textSTT.pack()

        self.languageVar = StringVar(self.master)
        self.languageVar.set("Select language")
        self.languages = list(self.language_codes.keys())
        self.dropdown = OptionMenu(self.master, self.languageVar, *self.languages)
        self.dropdown.pack()

        self.statusLabel = Label(self.master, text="Status: Idle")
        self.statusLabel.pack()

        self.btnSTT = Button(self.master, text="Listen", command=self.run_speech_to_text_thread)
        self.btnSTT.pack()

        self.labelTTS = Label(self.master, text="Text-to-Speech")
        self.labelTTS.pack()

        self.textTTS = Entry(self.master, width=50)
        self.textTTS.pack()

        self.btnTTS = Button(self.master, text="Speak", command=self.text_to_speech)
        self.btnTTS.pack()

    def run_speech_to_text_thread(self):
        threading.Thread(target=self.speech_to_text).start()

    def speech_to_text(self):
        self.update_status("Listening...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source)
        try:
            self.update_status("Processing...")
            language_code = self.language_codes.get(self.languageVar.get())
            if not language_code:
                raise ValueError("Unsupported language selected")
            text = recognizer.recognize_google(audio, language=language_code)
            self.textSTT.delete(1.0, tk.END)
            self.textSTT.insert(tk.END, text)
            self.update_status("Idle")
        except sr.UnknownValueError:
            self.textSTT.delete(1.0, tk.END)
            self.textSTT.insert(tk.END, "Could not understand audio")
            self.update_status("Idle")
        except sr.RequestError as e:
            self.textSTT.delete(1.0, tk.END)
            self.textSTT.insert(tk.END, f"Error with the service; {e}")
            self.update_status("Idle")
        except ValueError as ve:
            self.textSTT.delete(1.0, tk.END)
            self.textSTT.insert(tk.END, str(ve))
            self.update_status("Idle")

    def text_to_speech(self):
        text = self.textTTS.get()
        language_code = self.language_codes.get(self.languageVar.get())
        if text and language_code:
            self.speak_text(text, language_code)
        else:
            print("Please enter text and select a valid language to convert to speech.")

    def speak_text(self, command, language):
        try:
            self.update_status("Generating speech...")
            voice = gTTS(command, lang=language)
            voice.save("voice.mp3")
            pygame.mixer.music.load("voice.mp3")
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.music.unload()
            os.remove("voice.mp3")
            self.update_status("Idle")
        except Exception as e:
            print(f"Error generating or playing speech: {e}")
            self.update_status("Idle")

    def update_status(self, status):
        self.statusLabel.config(text=f"Status: {status}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x300")
    app = SpeechApp(root)
    root.mainloop()
