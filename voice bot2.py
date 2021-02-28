from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pyttsx3
import subprocess
import playsound
import webbrowser
import pytz
import speech_recognition as sr

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']

DAYS = ['monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday']

DAY_EXTENSIONS = ["nd", "rd", "th", "st"]


def get_audio():  # will get audio as input
    '''r = sr.Recognizer()

    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        print("speak")
        audio_in = r.listen(source, phrase_time_limit=3)
        print("stop")
        audio_ou = str()
        try:
            audio_ou = r.recognize_google(audio_in)
            print(audio_ou)
        except sr.UnknownValueError:
            print("....")
            get_audio()
        # return get_audio()
    return audio_ou.lower()'''
    string = str(input("enter anything : "))
    return string.lower()


def speak(text):  # will speak
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 45)
    engine.say(text)
    engine.runAndWait()


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(
                    ":")[0]) - 12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # if the month mentioned is before the current month set the year to the
    # next
    if month < today.month and month != -1:
        year = year + 1

    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)


def play_music():
    file_dir = "E:/Department_YouTube/MP_3/"
    var = os.listdir(file_dir)
    speak("Which music you would like to listen?")
    for music in var:
        print(music)
    song_name = str(input("enter song name : "))
    for song in var:
        if song_name.lower() in song.lower():
            playsound.playsound(file_dir + song)


def google_search(audio):
    google_search_phrases = ['google']
    str_audio = str(audio).split()
    google_null_str = str()
    for ev_word in google_search_phrases:
        for word in str_audio:
            if ev_word.lower() == word.lower():
                wrd_ind = str_audio.index(word)
                srch_index = wrd_ind + 1
                while srch_index < len(str_audio):
                    google_null_str += str_audio[srch_index]
                    srch_index += 1
                speak("Launching Chrome")
                query = 'https://www.google.co.in/search?q='
                webbrowser.open(query + google_null_str)


def youtube_(audio):
    youtube_phrs = ['search in youtube']
    str_audio = str(audio).split()
    youtube_null_str = str()
    for ev_word in youtube_phrs:
        for word in str_audio:
            if word.lower() == "youtube":
                wrd_ind = str_audio.index(word)
                src_index = wrd_ind + 1
                while src_index < len(str_audio):
                    youtube_null_str += str_audio[src_index]
                    src_index += 1
    speak("Opening Youtube")
    query_youtube = 'http://www.youtube.com/results?search_query='
    webbrowser.open(query_youtube + youtube_null_str)


def make_note():
    curr_date = datetime.datetime.now()
    file_name = str(curr_date).replace(":", "-") + " note.txt"
    with open(file_name, 'w') as f:
        speak("what to note?")
        text_to_be_noted = get_audio()
        f.write(text_to_be_noted)
    speak("I've made a note of it.")
    subprocess.Popen(["notepad.exe", file_name])


def time_funct():
    current_time = datetime.datetime.now()
    current_time_v3 = current_time.strftime("%d-%B %Y  %H:%M:%S")
    print(current_time_v3)
    speak("The clock is ticking at" + str(current_time_v3).lower())


def launch_app(audio):
    app_launch = ['open', 'launch']
    str_audio = str(audio).split()  # returns a list of words in string
    app_str = str()
    for exp in app_launch:
        for word in str_audio:  # audio is "Open ......./ launch ........"
            if word.lower() == exp.lower():
                # index of open or launch in str_audio
                word_index = str_audio.index(word)
                app_index = word_index + 1
                while app_index < len(str_audio):
                    app_str += "C:/Windows/System32/" + \
                        str_audio[app_index] + ".exe"
                    app_index += 1
    # calc, notepad, dxdiag, osk, SnippingTool, mspaint
    # print(app_str)  >>> its working
    os.system(app_str)


def operate(audio):  # parameter audio is get_audio
    covid_phrases = ['give me corona updates', 'corona']
    for phrase in covid_phrases:
        if phrase in audio:
            import web_scrapping

    CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
    for phrase in CALENDAR_STRS:
        if phrase in audio:
            date = get_date(get_audio())
            if date:
                get_events(date, service)
            else:
                speak("I don't know what that mean.")

    music_phrases = ['play some song', 'play me some music']

    for i in music_phrases:
        if i.lower() in audio:
            # code_looped()
            play_music()

    google_search_phrases = ['google']

    for i in google_search_phrases:
        if i.lower() in audio:
            google_search(audio)

    note_pad_phrases = ['make a note of this', 'note this']

    for i in note_pad_phrases:
        if i.lower() in audio:
            # code_looped()
            make_note()

    youtube_phrs = ['youtube']

    for i in youtube_phrs:  # WORKS!
        if i.lower() in audio:
            # code_looped()
            youtube_(audio)

    quit_strs = ['bye', 'see you soon', 'talk to you later']

    for i in quit_strs:
        if i.lower() in audio:
            speak("Had a nice time talking to you.")

    time_phrs = ['time']
    for i in time_phrs:
        if i.lower() in audio:
            time_funct()

    list_app_launch = ['open', 'launch']
    for word in list_app_launch:
        if word.lower() in audio:
            launch_app(audio)


# service = authenticate_google()


speak("Go Ahead\nI'm listening....")
while True:
    operate(get_audio())
