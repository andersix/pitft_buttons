#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:fileformat=unix:

from gpiozero import Button
from gpiozero import PWMLED
from time import sleep
from signal import pause
import syslog
import subprocess as sproc

# Looking at display, with buttons on the left:
B0 = 17  # first  button from the top on PiTFT+
B1 = 22  # second button from the top on PiTFT+
B2 = 23  # third  button from the top on PiTFT+
B3 = 27  # fourth button from the top on PiTFT+

LEDPIN = 18  # Backlight LED is on GPIO 18 on PiTFT 2.8"s
PWMF = 240  # PWM frequency for LED dimming

class Buttons_PiTFTplus():

    def __init__(self):
        self.hold_time=0.0
        self.led_ucorr = 1.0  # uncorrected LED PWM value, 0.0 to 1.0. Initial value == 1.0
        self.gamma = 2.2  # gamma used to correct LED PWM
        self.blink_display = False

        # LED backlight setting and control
        self.led = PWMLED(pin=LEDPIN, initial_value=1.0, frequency=PWMF)

        # Button 0: Tie to LED backlight brightness function
        self.led_button = Button(B0, bounce_time=.01)
        self.led_button.when_pressed = self.brightness

        # Button 1: Tie to PiHole update function
        self.pihole_up_button = Button(B1)
        self.pihole_up_button.when_pressed = self.pihole_update

        # Button 2: Tie to PiHole update gravity DB.
        self.gu_button = Button(B2)
        self.gu_button.when_pressed = self.pihole_gravity_up

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
            """
            Toggle the LED backlight when this method is called
            """
            if self.led.value == 0.0:
                self.led.value = 1.0
            else:
                self.led.value = 0.0

        while True:
            if self.hold_time >= 2.0 and self.blink1:
                for i in range(2):
                    led_toggle()
                    sleep(.5)
                self.blink1 = False
                print("blink1")
            elif self.hold_time >= 5.0 and self.blink2:
                for i in range(2):
                    led_toggle()
                    sleep(.5)
                self.blink2 = False
                print("blink2")
            elif self.blink_display:
                led_toggle()
                sleep(.5)
            else:
                sleep(.5)

    def pihole_update(self):
        """
        Check to see if PiHole needs an update.
        If it does, do it. If not skip it.
        While updating, the display will continuously blink on/off
        """
        # first check if PiHole needs an update
        cmd = "pihole -up --check-only"
        sp = sproc.Popen(cmd, shell=True, stdout=sproc.PIPE, stderr=sproc.PIPE)
        # Store the return code in rc variable
        rc = sp.wait()
        # Separate the output and error by communicating with sp variable.
        # This is similar to Tuple where we store two values to two different variables
        out,err = sp.communicate()  # NOTE: returns a byte-string
        if (b"Everything is up to date") in out:
            # no updates
            out = out.split(b'\n')
            for s in out:
                syslog.syslog(s.decode("utf-8"))
        else:
            # run the updater
            cmd = "pihole -up"
            self.led.value = 1.0
            self.blink_display = True
            sp = sproc.Popen(cmd, shell=True, stdout=sproc.PIPE, stderr=sproc.PIPE)
            rc = sp.wait()
            out,err = sp.communicate()
            out = out.split(b'\n')
            for s in out:
                syslog.syslog(s.decode("utf-8"))
            self.blink_display = False
            self.led.value = 1.0

    def pihole_gravity_up(self):
        """
        Update gravity DB. Blink display while updating.
        """
        cmd = "pihole -g"
        self.led.value = 1.0
        self.blink_display = True
        sp = sproc.Popen(cmd, shell=True, stdout=sproc.PIPE, stderr=sproc.PIPE)
        rc = sp.wait()
        out,err = sp.communicate()
        out = out.split(b'\n')
        for s in out:
            syslog.syslog(s.decode("utf-8"))
        self.blink_display = False
        self.led.value = 1.0



if __name__ == '__main__':

    pb = Buttons_PiTFTplus()
    pause() # keep this sumbitch runnin'

