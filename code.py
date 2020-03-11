#  RayGun Final Code Test 5/16/19
import time
import board
import neopixel
import math
import audioio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn, AnalogOut

bar_pin = board.D5          #define pixels in barrel
dial_pin = board.D4         #define pixels in dial
bar_pixels = 15             #define number of pixels in barrel
dial_pixels = 3             #define number of pixels in dial
RED = (255, 0, 0)           #define red in rgb
YELLOW = (255, 255, 0)      #define yellow in rgb
GREEN = (0, 255, 0)         #define green in rgb

phase = 0                   #set phase to 0

barrel = neopixel.NeoPixel(bar_pin, bar_pixels, brightness=1.0, auto_write=False) #define strip for barrel
dial = neopixel.NeoPixel(dial_pin, dial_pixels, brightness=1.0, auto_write=False) #define strip for dial

#  Give power to D10 which powers the speaker amplifier
enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

#  Set up audio channel/Open audio files and prep for playback
audio = audioio.AudioOut(board.A0)
startup = audioio.WaveFile(open("Startup.wav", "rb"))
shoot = audioio.WaveFile(open("RayGunPew.wav", "rb"))
empty = audioio.WaveFile(open("Empty.wav", "rb"))
quote1 = audioio.WaveFile(open("Dempsey_1.wav", "rb"))
quote2 = audioio.WaveFile(open("Dempsey_2.wav", "rb"))
quote3 = audioio.WaveFile(open("Dempsey_3.wav", "rb"))
reloadOpen = audioio.WaveFile(open("Reload_Open.wav", "rb"))
reloadClose = audioio.WaveFile(open("Reload_Close.wav", "rb"))

trigger = DigitalInOut(board.D11)
trigger.direction = Direction.INPUT
trigger.pull = Pull.UP

sensor = DigitalInOut(board.D12)
sensor.direction = Direction.INPUT
sensor.pull = Pull.UP

pot_read = AnalogIn(board.A2)
galv_out = AnalogOut(board.A1)

barrel_open = False         #set boolean value for if the barrel is open
hallstate = barrel_open     #set boolean for the hallstate
trigger_count = 0           #init trigger pull counter
ct = 0                      #init ct value

def get_mode(mode):                         #define get_mode funtion with | mode parameter comes from pot
    if mode <= 100:                             #if parameter is less than or = 100
        barrel.fill((15, 100, 175))                 #prep barrel pixels to blue
        barrel.show()                               #show color
    elif mode > 100 and mode <= 200:            #else if parameter is between 100 and 201 
        barrel.fill((0, 255, 0))                    #prep barrel pixels as green
        barrel.show()                               #show color
    elif mode > 200 and mode <= 300:            #else if parameter is between 200 and 301
        barrel.fill((255, 0, 0))                    #prep barrel pixels as red
        barrel.show()                               #show color
    elif mode > 300 and mode <= 400:            #else if parameter is between 300 and 401
        blue_wave()                                 #run blue_wave animation
    else:                                       #else
        white_wave()                                #run white_wave()

def blue_wave():                                                    #define blue_wave funtion/ animation
    for p in range(bar_pixels):                                         #loop for number of pixels in barrel
        BLUE = int(abs(math.sin((p - phase)*3.14 / 18) * 235))+15           #set BLUE to 
        barrel[p] = (0, 0, BLUE)
        barrel.show()
        time.sleep(0.002)

def white_wave():
    for p in range(bar_pixels):
        WHITE = int(abs(math.sin((p - phase)*3.14 / 18) * 175))+15
        barrel[p] = (WHITE, WHITE, WHITE)
        barrel.show()
        time.sleep(0.002)

def red_wave():
    for p in range(bar_pixels):
        RED = int(abs(math.sin((p - phase)*3.14 / 18) * 175))+15
        barrel[p] = (RED, 0, 0)
        barrel.show()
        time.sleep(0.002)

def dial_disp():
    dial[0] = RED
    dial[1] = YELLOW
    dial[2] = GREEN
    dial.show()

def bad_fire(i):
    if i == 0:
        audio.play(empty)
    elif i == 1:
        audio.play(quote1)
    elif i == 2:
        audio.play(quote2)
    elif i == 3:
        audio.play(quote3)

audio.play(startup)

for i in range(155):
    barrel.fill((i, i, i))
    dial[0] = (i, 0, 0)
    dial[1] = (i, i, 0)
    dial[2] = (0, i, 0)
    dial.show()
    barrel.show()
dial_disp()

#  Main loop
while True:
    reading = pot_read.value
    val = (reading * 500.0) / 65536
    get_mode(val)
    phase += 1
    last_hallstate = hallstate
    hallstate = sensor.value

    if not trigger.value and not sensor.value and not audio.playing:  # If trigger is pulled while the barrel is closed
        if trigger_count < 20:
            galv_out.value = 7000
            audio.play(shoot)
            galv_out.value = 0
        elif ct < 4:
            galv_out.value = 0
            bad_fire(ct)
            ct += 1
        else:
            ct = 0
        trigger_count += 1
    elif hallstate and hallstate != last_hallstate:
        galv_out.value = 7000
        audio.play(reloadOpen)
    elif not hallstate and hallstate != last_hallstate:
        trigger_count = 0
        audio.play(reloadClose)