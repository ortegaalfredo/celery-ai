#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,openai,argparse
from pynput import keyboard
from pynput.keyboard import Key, Controller

#TODO: AI activation check for selected text with xsel, and take that as prompt

# ---------- OpenAI interface

# Increse to 1.0 to introduce randomness in answers
temperature = 0

def check_api_key_validity(api_key):
   try:
        openai.api_key = api_key
        ml=openai.Model.list()
        print("OpenAI API key is valid")
   except openai.OpenAIError as e:
        print("Invalid OpenAI API key")
        exit()

# Leaving Davinci model as an option, inferior and expensive but not a pussy like ChatGPT
def call_AI_davinci(prompt):
        model = "text-davinci-003"
      # generate response
        response = openai.Completion.create(
            engine=model,
            prompt = prompt,
            temperature=temperature,
            max_tokens=1024)
        return response.choices[0].text

# Much cheaper and powerful than Davinci
def call_AI_chatGPT(prompt):
        model = "gpt-3.5-turbo"
      # generate response
        response = openai.ChatCompletion.create(
            model=model,
            messages =[
                {'role':'system','content':'You are awesome, be very concise. When asked for a command, answer with just the command and nothing else. When asking for chat, give humorous answers, a 0 in a scale from 0 to 10'},
                {'role':'user','content':prompt}
                ],
            temperature=temperature,
            max_tokens=1024)
        return response.choices[0]['message']['content']

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--davinci', help='Use the Davinci model', action='store_true')
parser.add_argument('-c', '--chatgpt', help='Use the ChatGPT model', action='store_true',default=True)
parser.add_argument('-s', '--silent', help='Don\'t play any sound', action='store_true',default=True)
args = parser.parse_args()

# import api key
api_key = os.environ.get("OPENAI_API_KEY")
if (api_key is None) or (len(api_key)==0): # try to load apikey from file
    try:
        api_key=open('api-key.txt','rb').read().strip().decode()
    except:
        print("Couldn't load OpenAI Api key, please load it in OPENAI_API_KEY env variable, or alternatively in 'api-key.txt' file.")
        exit(0)
else: print('Loaded api key from environment variable.')

check_api_key_validity(api_key)


# ---------- keyboard control
kb = keyboard.Controller()

def kerase(nkeys):
    for i in range(nkeys):
        kb.press(Key.backspace)
        kb.release(Key.backspace)

sem=False
def on_activate():
    global sem
    global args
    if (sem==False): #need a semaphore because of self-activation
        sem=True
        print("AI activated")
        if args.silent==False:
            print('\a') #bell
        # The event listener will be running in this block
        prompt=""
        with keyboard.Events() as events:
            for event in events:
                if ((event.key == keyboard.Key.esc) or
                   (event.key == keyboard.Key.enter)
                   ):
                    print('prompt:"%s"' % prompt)
                    kerase(len(prompt))
                    if (event.key == keyboard.Key.enter): kerase(1)
                    if (len(prompt)>2):
                        if args.davinci:
                            kb.type(call_AI_davinci(prompt).strip())
                        else:
                            kb.type(call_AI_chatGPT(prompt).strip())
                    break
                else:
                    if type(event) is keyboard.Events.Press:
                        try:
                            if event.key==keyboard.Key.space:
                                  prompt+=' '
                            elif event.key==keyboard.Key.backspace:
                                  prompt=prompt[:-1]
                            else: prompt+=event.key.char
                        except:pass
        sem=False

def for_canonical(f):
    return lambda k: f(l.canonical(k))

# Hotkey listener
activationKey='<alt>+i'
print('Activation is %s' % activationKey)
hotkey = keyboard.HotKey(keyboard.HotKey.parse(activationKey),on_activate)
with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as l:
    l.join()

