from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import speech_recognition as sr
import pyttsx3
import pytz
import subprocess
from googlesearch import search
import playsound
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ["nd", "rd", "th", "st"]


def speak(text):  # will only say
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 40)
    engine.say(text)
    engine.runAndWait()


def get_audio():  # will get the audio and print it on the console
    r = sr.Recognizer()
    #r.energy_threshold = 300

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
        rec_audio = str()
        try:
            rec_audio = r.recognize_google(audio)
            print(rec_audio)
        except Exception as e:
            print("Exception :" + str(e))

    return rec_audio.lower()


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next n events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())  # A combination of a date and a time.
                                                                        # Attributes: year, month, day, hour, minute,
                                                                        # second, microsecond, and tzinfo.
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                         singleEvents=True,
                                        orderBy='startTime').execute()
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, ">> ", event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event['summary'] + "at" + start_time)


def get_date(text):
    today = datetime.date.today()
    if text.count() > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year
    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1  # list indexing starts from 0 so +1 means january = 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for extensions in DAY_EXTENSIONS:
                found = word.find(extensions)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

        if month < today.month and month != -1:
            year += 1
        if day < today.day and month == 1 and day != -1:
            month += 1
        if month == -1 and day == -1 and day_of_week != -1:
            current_day_of_week = today.weekday()
            dif = day_of_week - current_day_of_week
            if dif < 0:
                dif += 7
                if text.count("next") >= 1:
                    dif += 7
                return today + datetime.timedelta(dif)
        if month == -1 or day == -1:
            return None
        return datetime.date(month=month, day=day, year=year)


def note(text):
    curr_date = datetime.datetime.now()
    file_name = str(curr_date).replace(":", "-") + " note.txt"
    with open(file_name, 'w') as f:
        f.write(text)
    subprocess.Popen(["notepad.exe", file_name])


def web_search(audio):
    for url in search(audio, stop=10):
        print(url)


def play_music(function):
    list_directory = os.listdir("E:/Department_YouTube/MP_3/")
    speak("Which music would you like to hear?")
    for music_name in function:
        if music_name in list_directory:
            playsound.playsound("E:/Department_YouTube/MP_3/" + str(music_name))
            break


bot_name = "hey tim"
service = authenticate_google()
print("start")

while True:
    print("I'm listening")
    var_a = get_audio()
    if bot_name in var_a:
        speak("I am listening")
        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
        var_getting_date = get_audio()
        for phrase in CALENDAR_STRS:
            if phrase in var_getting_date:
                date = get_date(var_getting_date)
                if date:
                    get_events(date, service)
                else:
                    speak("Please try again")

        note_strs = ["make a note of this", "remember this", "note it down"]
        for note_phrase in note_strs:
            if note_phrase in var_a:
                speak("What should I make a note of?")
                var_making_note = get_audio()
                note(var_making_note)
                speak("Done")

        search_strs = ['google this']
        for search_phrs in search_strs:
            if search_phrs in var_a:
                try:
                    speak("tell me what to search for?")
                    var_making_google_search = get_audio()
                    web_search(var_making_google_search)
                except Exception as e:
                    print("Error: " + str(e))

        music_strs = ['play music']
        for music_phrs in music_strs:
            if music_phrs in var_a:
                play_music(get_audio())
