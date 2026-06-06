import RPi.GPIO as GPIO
import requests
import time

FLASK_URL = "http://127.0.0.1:5000"

PREV_PIN = 17
PLAY_PIN = 27
NEXT_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(PREV_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(NEXT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def previous(channel):
    requests.post(f"{FLASK_URL}/api/previous")
    print("Previous")

def playpause(channel):
    requests.post(f"{FLASK_URL}/api/playpause")
    print("Play/Pause")

def next_track(channel):
    requests.post(f"{FLASK_URL}/api/next")
    print("Next")

GPIO.add_event_detect(PREV_PIN, GPIO.FALLING, callback=previous, bouncetime=300)
GPIO.add_event_detect(PLAY_PIN, GPIO.FALLING, callback=playpause, bouncetime=300)
GPIO.add_event_detect(NEXT_PIN, GPIO.FALLING, callback=next_track, bouncetime=300)

print("Button listener running...")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()