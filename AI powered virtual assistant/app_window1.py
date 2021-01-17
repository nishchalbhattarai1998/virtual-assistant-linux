import os
import signal
import logging
import threading

import gi
gi.require_version('Gtk', '3.0')  # nopep8

#from bot import script1 as va
from gi.repository import Gtk, GObject


import concurrent.futures

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

# import gobject
GObject.threads_init()
import aiml
import os
import time
import argparse

import speech_recognition as sr
import pyttsx3 as pyttsx
# from gtts import gTTS
# from pygame import mixer

mode = "text"
voice = "pyttsx"
terminate = ['bye', 'buy', 'shutdown', 'exit', 'quit', 'gotosleep', 'goodbye']


def get_arguments():
    parser = argparse.ArgumentParser()
    optional = parser.add_argument_group('params')
    optional.add_argument('-v', '--voice', action='store_true', required=False,
                          help='Enable voice mode')
    optional.add_argument('-g', '--gtts', action='store_true', required=False,
                          help='Enable Google Text To Speech engine')
    arguments = parser.parse_args()
    return arguments


def gtts_speak(jarvis_speech):
    tts = gTTS(text=jarvis_speech, lang='en')
    tts.save('jarvis_speech.mp3')
    mixer.init()
    mixer.music.load('jarvis_speech.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(1)


def offline_speak(jarvis_speech):
    engine = pyttsx.init()
    engine.say(jarvis_speech)
    engine.runAndWait()


def speak(jarvis_speech):
    if voice == "gTTS":
        gtts_speak(jarvis_speech)
    else:
        offline_speak(jarvis_speech)


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        #print("Talk to J.A.R.V.I.S: ")
        audio = r.listen(source)
    try:
        print(r.recognize_google(audio))
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        # speak("I couldn't understand what you said! Would you like to repeat?")
        return(listen())
    except sr.RequestError as e:
        print("Could not request results from " +
              "Google Speech Recognition service; {0}".format(e))


def assistant_init():
    #args = get_arguments()
    try:
        mode = "voice"
    except ImportError:
        print("\nInstall SpeechRecognition to use this feature." + "\nStarting text mode\n")

    kernel = aiml.Kernel()

    if os.path.isfile("bot_brain.brn"):
        kernel.bootstrap(brainFile="bot_brain.brn")
    else:
        kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
        # kernel.saveBrain("bot_brain.brn")

    # kernel now ready for use
    print('SPEAK')
    speak('ego is online')
    while True:
        if mode == "voice":
            response = listen()
        else:
            response = input("Talk to J.A.R.V.I.S : ")
        if response.lower().replace(" ", "") in terminate:
            break
        jarvis_speech = kernel.respond(response)
        speak(jarvis_speech)
        return jarvis_speech, response

#text = assistant_init()


class SusiAppWindow:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(TOP_DIR, "glade_files/susi_app.glade"))

        self.window = builder.get_object("app_window")
        self.user_text_label = builder.get_object("user_text_label")
        self.susi_text_label = builder.get_object("susi_text_label")
        self.root_box = builder.get_object("root_box")
        
        self.state_stack = builder.get_object("state_stack")
        
        self.mic_button = builder.get_object("mic_button")

        self.mic_box = builder.get_object("mic_box")
        self.listening_box = builder.get_object("listening_box")
        self.thinking_box = builder.get_object("thinking_box")
        self.error_label = builder.get_object("error_label")
        
        self.settings_button = builder.get_object("settings_button")

        # listeningAnimator = ListeningAnimator(self.window)
        # self.listening_box.add(listeningAnimator)
        # self.listening_box.reorder_child(listeningAnimator, 1)
        # self.listening_box.set_child_packing(listeningAnimator, False, False, 0, Gtk.PackType.END)

        # thinkingAnimator = ThinkingAnimator(self.window)
        # self.thinking_box.add(thinkingAnimator)
        # self.thinking_box.reorder_child(thinkingAnimator, 1)
        # self.thinking_box.set_child_packing(thinkingAnimator, False, False, 0, Gtk.PackType.END)

        builder.connect_signals(SusiAppWindow.Handler(self))
        self.window.set_default_size(300, 600)
        self.window.set_resizable(False)


    def show_window(self):
        self.window.show_all()
        Gtk.main()

    def exit_window(self):
        self.window.destroy()
        Gtk.main_quit()

    def receive_message(self, widget):
        print('RECEIVED')
        self.state_stack.set_visible_child_name("listening_page")
        '''if message_type == 'idle':
            self.state_stack.set_visible_child_name("mic_page")

        elif message_type == 'listening':
            self.state_stack.set_visible_child_name("listening_page")
            self.user_text_label.set_text("")
            self.susi_text_label.set_text("")

        elif message_type == 'recognizing':
            self.state_stack.set_visible_child_name("thinking_page")

        elif message_type == 'recognized':
            user_text = payload
            self.user_text_label.set_text(user_text)

        elif message_type == 'speaking':
            self.state_stack.set_visible_child_name("empty_page")
            susi_reply = payload['susi_reply']
            if 'answer' in susi_reply.keys():
                self.susi_text_label.set_text(susi_reply['answer'])

        elif message_type == 'error':
            self.state_stack.set_visible_child_name("error_page")
            error_type = payload
            if error_type is not None:
                if error_type == 'connection':
                    self.error_label.set_text("Problem in internet connectivity !!")
                elif error_type == 'recognition':
                    self.error_label.set_text("Couldn't recognize the speech.")
            else:
                self.error_label.set_text('Some error occurred,')'''

    class Handler:
        def __init__(self, app_window):
            self.app_window = app_window
            self.g = 'GObject.timeout_add(0, self.listen)'
            self.speech, self.response = 'EGO: Hello Ashwin', 'Response:Script not responding, connect.'

        def listen(self):
            self.speech, self.response = assistant_init()
            return True
	    

        def on_delete(self, *args):
            self.app_window.exit_window()
            os.kill(os.getppid(), signal.SIGHUP)

        def on_mic_button_clicked(self, button):
            print('BUTTON CLICKED')
            self.listen()
            '''with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.listen)
                return_value = future.result()
                print(return_value)'''
            # x = threading.Thread(target=self.listen)
            # x.start()
            # self.g = GObject.timeout_add(0, self.listen)
            print(self.speech+"\n"+self.response)
            self.app_window.state_stack.set_visible_child_name("listening_page")
            # text = va.assistant_init()
            # if self.response == 'hello':
            self.listening_mode()

            
        def listening_mode(self):
            self.app_window.state_stack.set_visible_child_name("thinking_page")
            self.app_window.susi_text_label.set_text('User: '+self.response+"\n\n"+'BOT: '+self.speech)
            self.app_window.state_stack.set_visible_child_name("mic_page")

        def on_settings_button_clicked(self, button):
            window = ConfigurationWindow()
            window.show_window()


window = SusiAppWindow()
window.show_window()
