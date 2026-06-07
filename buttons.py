import gpiod
import requests
import time

FLASK_URL = "http://127.0.0.1:5000"

PREV_PIN = 17
PLAY_PIN = 27
NEXT_PIN = 22

def handle(pin):
    if pin == PREV_PIN:
        requests.post(f"{FLASK_URL}/api/previous")
        print("Previous")
    elif pin == PLAY_PIN:
        requests.post(f"{FLASK_URL}/api/playpause")
        print("Play/Pause")
    elif pin == NEXT_PIN:
        requests.post(f"{FLASK_URL}/api/next")
        print("Next")

last = {PREV_PIN: 1, PLAY_PIN: 1, NEXT_PIN: 1}

with gpiod.request_lines(
    '/dev/gpiochip0',
    consumer="buttons",
    config={
        (PREV_PIN, PLAY_PIN, NEXT_PIN): gpiod.LineSettings(
            direction=gpiod.line.Direction.INPUT,
            bias=gpiod.line.Bias.PULL_UP,
        )
    }
) as request:
    print("Button listener running...")
    while True:
        for pin in [PREV_PIN, PLAY_PIN, NEXT_PIN]:
            val = request.get_value(pin)
            int_val = 0 if val == gpiod.line.Value.INACTIVE else 1
            if int_val == 0 and last[pin] == 1:
                handle(pin)
                time.sleep(0.3)
            last[pin] = int_val
        time.sleep(0.01)