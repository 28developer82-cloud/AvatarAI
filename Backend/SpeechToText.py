import speech_recognition as sr
from mtranslate import translate
import audioop

LANGUAGE_IN = "en-IN"
TRANSLATE_TO = "en"
PHRASE_TIME_LIMIT = 8
VOLUME_GAIN = 2
MIN_CHARS = 3

r = sr.Recognizer()
r.energy_threshold = 300
r.dynamic_energy_threshold = True
r.pause_threshold = 1

mic = sr.Microphone()

def SpeechRecognition():
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, phrase_time_limit=PHRASE_TIME_LIMIT)

        raw = audio.get_raw_data()
        boosted = audioop.mul(raw, audio.sample_width, VOLUME_GAIN)
        audio = sr.AudioData(boosted, audio.sample_rate, audio.sample_width)

        text = r.recognize_google(audio, language=LANGUAGE_IN).lower()

        if len(text) < MIN_CHARS:
            return None

        return translate(text, TRANSLATE_TO)

    except:
        return None
