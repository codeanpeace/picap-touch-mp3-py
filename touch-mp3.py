################################################################################
#
# Bare Conductive Pi Cap
# ----------------------
#
# touch-mp3.py - polyphonic touch triggered MP3 playback
#
# Written for Raspberry Pi.
#
# Bare Conductive code written by Stefan Dzisiewski-Smith, Szymon Kaliski,
# Pascal Loose and Tom Hartley.
#
# This work is licensed under a MIT license https://opensource.org/licenses/MIT
#
# Copyright (c) 2016, Bare Conductive
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#################################################################################

import MPR121
from gpiozero import RGBLED
import subprocess
import pygame
from pygame.mixer import Sound
from glob import glob
from time import sleep

sensor = MPR121.begin()

# set threshold for touch
# sensor.set_touch_threshold(40)
# sensor.set_release_threshold(20)

# set threshold for proximity
sensor.set_touch_threshold(20)
sensor.set_release_threshold(10)

led = RGBLED(6, 5, 26, active_high=False)

num_electrodes = 12

# convert mp3s to wavs with picap-samples-to-wav
led.blue = 1
subprocess.call("picap-samples-to-wav tracks", shell=True)
subprocess.call("picap-samples-to-wav card_tracks_part_1", shell=True)
subprocess.call("picap-samples-to-wav card_tracks_part_2", shell=True)
led.off()

# initialize mixer and pygame
pygame.mixer.pre_init(frequency=44100, channels=64, buffer=1024)
pygame.init()

selected_card = 2
sounds = [Sound(path) for path in sorted(glob("tracks/.wavs/TRACK*.wav"))] + [Sound(path) for path in sorted(glob("card_tracks_part_1/.wavs/TRACK*.wav"))] + [Sound(path) for path in sorted(glob("card_tracks_part_2/.wavs/TRACK*.wav"))]

def play_sounds_when_touched():
    global selected_card_index
    if sensor.touch_status_changed():
        sensor.update_touch_data()

        is_any_touch_registered = False

        for i in range(num_electrodes):
            if sensor.get_touch_data(i):
                # check if touch is registered to set the led status
                is_any_touch_registered = True
            if sensor.is_new_touch(i):
                # dropzones of two
                if i in range(2):
                    # TRACK000 (0, 1)
                    print ("dropzones index: " + str(i))
                    index = i
                # touch card header of six
                elif i in range(2, 8):
                    # TRACK002 (2, 3, 4, 5, 6, 7)
                    print ("setting selected_card_index: " + str(i))
                    selected_card_index = i
                    index = i
                # dynamic values range(8..12)
                else:
                    # top card of six, first of four dynamic value => (2 * 10) + 8 - 7 = 21 => TRACK021 (21, 22, 23, 24)
                    # bottom card of six, last of four dynamic value => (7 * 10) + 11 - 7 = 74 => TRACK074 (71, 72, 73, 74)
                    # index = (selected_card * 10) + i - 7

                    # top card of six, first of four dynamic value => ((2 - 2) * 4) + 8 = 8 => TRACK008 (8, 9, 10, 11)
                    # 12 - 15, 16 - 19, 20 - 23, 24 - 27, 28 - 31
                    # bottom card of six, last of four dynamic value => ((7 - 2) * 4) + 11 = 31 => TRACK074 (28, 29, 30, 31)
                    print ("dynamic values")
                    print ("selected_card_index: " + str(selected_card_index))
                    index = (selected_card_index - 2) * 4 + i
                    print ("index: " + str(index))
                
                # play sound associated with that touch
                sound = sounds[index]
                print ("playing sound: " + str(index))
                sound.play()

        if is_any_touch_registered:
            led.red = 1
        else:
            led.off()

running = True
while running:
    try:
        play_sounds_when_touched()
    except KeyboardInterrupt:
        led.off()
        running = False
    sleep(0.01)
