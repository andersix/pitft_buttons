#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:fileformat=unix:

from gpiozero import Button
from gpiozero import PWMLED
from time import sleep
from signal import pause
import subprocess as sproc

# Looking at display, with buttons on the left:
B0 = 17  # first button from the top on PiTFT+
B1 = 22  # second button from the top on PiTFT+
B2 = 23  # third button from the top on PiTFT+
B3 = 27  # fourth button from the top on PiTFT+

LEDPIN = 18  # Backlight LED is on GPIO 18 on PiTFT 2.8"s
PWMF = 240  # PWM frequency for LED dimming

class Buttons_PiTFTplus():

    def __init__(self):
        self.hold_time=0.0
        self.led_ucorr = 1.0  # uncorrected LED PWM value, 0.0 to 1.0. Initial value == 1.0
        self.gamma = 2.2  # gamma used to correct LED PWM

        # LED backlight setting and control
        self.led = PWMLED(pin=LEDPIN, initial_value=1.0, frequency=PWMF)

        # Button 0: Tie to LED backlight brightness function
        self.led_button = Button(B0, bounce_time=.01)
        self.led_button.when_pressed = self.brightness

        # Button 1: Tie to PiHole update function
        self.pihole_up_button = Button(B1)
        self.pihole_up_button.when_pressed = self.pihole_update

        # Button 2: Tie to PiHole update gravity DB.
        # TODO FIXME

        # Button 3: Tie to Reset/Shutdown function
        self.rs_button = Button(B3, hold_time=1.0, hold_repeat=True)
        self.rs_button.when_held = self.rs_hold
        self.rs_button.when_released = self.rs_release

        # For restart/shutdown:
        self.blink1 = True
        self.blink2 = True
        self.wait_for_blinky()

    def rs_release(self):
        """
        callback when rs button is released
        if the hold time at release is > 2 but < 5, then restart
        if the hold time at release is > 5, the shutdown
        """
        ht = self.hold_time
        if ht >= 5.0:
            sproc.check_call(['/sbin/poweroff'])
        elif ht >= 2.0:
            sproc.check_call(['/sbin/reboot'])
        else:
            self.hold_time = 0.0

    def rs_hold(self):
        """
        callback function when rs button is held
        """
        # need to use max() as button.held_time resets to zero on last callback
        self.hold_time = max(self.hold_time, self.rs_button.held_time + self.rs_button.hold_time)

    def brightness(self):
        """
        Reduce brightness by 1/8th each time this
        method is called. If brightness is zero, then
        turn brightness to full.
        """
        if self.led_ucorr == 0.0:
            self.led_ucorr = 1.0
        else:
            self.led_ucorr -= 0.125
        self.led.value = pow(self.led_ucorr, self.gamma)

    def wait_for_blinky(self):
        """
        If R/S button is held for more that 2 secs, blink once.
        If R/S button is held for more than 5 secs, blink again.
        So, Reset/Shutdown indicator is, display does:
        * one blinky: will restart on button release
        * two blinky: will shutdown on button release
        """
        def led_toggle():
            if self.led.value == 0.0:
                self.led.value = 1.0
            else:
                self.led.value = 0.0

        while True:
            if self.hold_time >= 2.0 and self.blink1:
                led_toggle()
                sleep(.5)
                led_toggle()
                sleep(.5)
                if self.led.value == 0.0:
                    self.led.value = 1.0
                self.blink1 = False
                print("blink1")
            elif self.hold_time >= 5.0 and self.blink2:
                led_toggle()
                sleep(.5)
                led_toggle()
                sleep(.5)
                if self.led.value == 0.0:
                    self.led.value = 1.0
                self.blink2 = False
                print("blink2")
            sleep(.5)

    def pihole_update(self):
        """
        Check to see if PiHole needs an update.
        If it does, do it. If not skip it.
        """
        check_cmd = "pihole -up --check-only"
        update_cmd = "pihole -up".split()
        sp = sproc.Popen(check_cmd, shell=True, stdout=sproc.PIPE, stderr=sproc.PIPE)
        # Store the return code in rc variable
        rc = sp.wait()
        # Separate the output and error by communicating with sp variable.
        # This is similar to Tuple where we store two values to two different variables
        out,err = sp.communicate()
        if (b"Everything is up to date") in out:
            pass  # no updates, just burn
        else:
            sproc.check_call(update_cmd)
            # TODO: mebe blink display when update is finished?




if __name__ == '__main__':

    pb = Buttons_PiTFTplus()
    pause() # keep this sumbitch runnin'

