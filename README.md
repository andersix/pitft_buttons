# Pi-Hole PiTFT (or other) buttons

This is a python module and companion systemd service file,
performing useful functions using the four built-in buttons
on the PiTFT 2.8" Plus 320x240 TFT display panel PCB.

I use this display on a running Pi-Hole to display the Pi-Hole status.
The buttons are used for things like dimming the display, updating, and
restarting or shuting down the Pi for maintenance, etc.

## Use

The code in pitft_buttons.py determines what each button's function is.

The PiTFT 2.8" display has four buttons on GPIO 17, 22, 23, and 27.
In the python code, they are button0, button1, button2, and button3 respectively.

TODO: insert image

#### Button Functions

* Button 0 (GPIO 17):
  - Dim display backlight by 1/8th of full brightness for each press until display reaches "off" state.
    - When in the "off" state, the next button press turns display backlight back to full brightness.
      The PiTFT backlight LEDs are connected to GPIO 18. Brightness is set by PWM to this GPIO. The PWM is gamma-corrected so the 1/8th steps "look good".

* Button 1 (GPIO 22):
  - Run the Pi-Hole system updater
    - Press this button when you see the display showing "Updates are available".
      The update function checks to see if an update is needed, and does nothing
      if the PiHole is already up-to-date.
      The display flashes while the updating is running.
      Results are logged in syslog, so check /var/log/messages for results.

* Button 2 (GPIO 23):
  - Run the Pi-Hole gravity updater
    - Press button when you have added or changed Ad-lists and need to update Pi-Hole DBs.
      The display flashes while the updating is running.
      Results are logged in syslog, so check /var/log/messages for results.

* Button 3 (GPIO 27):
  - Restart or Shutdown
    - To Restart Pi, press and hold for more than 2 seconds, but less than 5 seconds.
    - To Shutdown Pi, press and hold for more than 5 seconds.
    - NOTE: The display will "blink" to indicate what will happen when you release button.
            When you see:
      * one blink, releasing button will restart Pi
      * a second blink, releasing button will shutdown Pi


## Requirements

### Hardware

* A Raspberry Pi (tested on a model 3B and 3B+)

* Adafruit PiTFT Plus 320x240 2.8" TFT (assembled with four buttons on the side.)
  - I got the capacitive one
  - https://www.adafruit.com/product/2423

### Software

* Raspberry Pi OS Lite
  - Tested on: "Raspbian GNU/Linux 10 (buster)"
  - https://www.raspberrypi.org/software/operating-systems/

* Python 3

* git

* Adafruit Raspberry Pi Installer scripts
  - https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi

* Pi-Hole (optional, but this is what I'm using it for)
  - padd.sh for status display

* python3-gpiozero package
  - Tested on Version: 1.5.1
  - Homepage: http://gpiozero.readthedocs.io/

## Installation

### Hardware

#### PiTFT Plus 2.8" TFT connected to Pi 40-pin GPIO connector

TODO: insert image

### Software

#### PiHole
* Get PiHole up and running for your network
  - https://docs.pi-hole.net/main/basic-install/
* Then return here for the rest...

#### Git
If you don't have git, install it with
```
sudo apt install git
```

#### Get the Adafruit installer scripts for the PiTFT:
```
cd ~
sudo pip3 install --upgrade adafruit-python-shell click==7.0
sudo apt-get install -y git
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
```

#### Pick the appropriate installer
I'm using the PiTFT 2.8 Capacitive, so am using:
```
sudo python3 adafruit-pitft.py --display=28c --rotation=90 --install-type=console
```

#### Reboot and return to here
Once the PiTFT script is installed, reboot your Pi, and return to the next step below.

#### Install padd.sh
I'm using this for PiHole status display, so let's use padd.sh
```
cd ~
git clone https://github.com/pi-hole/PADD.git
```
Then have padd.sh launch at boot time.
Edit your ~/.bashrc and at the bottom put:
```
# Run PADD
# If we're on the PiTFT screen (ssh is xterm)
if [ "$TERM" == "linux" ] ; then
  while :
  do
    ./PADD/padd.sh
    sleep 1
  done
fi
```

#### Reboot and return to here
After this reboot, the dipslay should show the PADD status screen for your PiHole.

Now let's install the buttons code:

#### Install the buttons code
```
sudo apt install python3-gpiozero git
cd ~
git clone https://github.com/andersix/pitft_buttons.git
cd ~/pitft_buttons
chmod +x pitft_buttons.py
sudo ln -s ~/pitft_buttons/pitft_buttons.py /usr/local/bin/.
sudo ln -s ~/pitft_buttons/pitft_buttons.service /etc/systemd/system/.
sudo systemctl enable pitft_buttons.service
sudo systemctl start pitft_buttons.service
```
If there are updates to this project at any time, and you want them, just pull them.
```
cd ~/pitft_buttons
git pull
sudo systemctl stop pitft_buttons.service
sudo systemctl start pitft_buttons.service
```

## Troubleshooting

Check the status of the program at any time with the command:
```
sudo systemctl status pitft_buttons.service
```
This should produce output similar to:
```
● pitft_buttons.service - PiTFT GPIO buttons
   Loaded: loaded (/home/pi/PiTFT28_buttons/pitft_buttons.service; enabled; vendor preset: enabled)
   Active: active (running) since Wed 2020-12-02 21:33:39 MST; 21h ago
 Main PID: 609 (python3)
    Tasks: 5 (limit: 1601)
   CGroup: /system.slice/pitft_buttons.service
           └─609 /usr/bin/python3 /usr/local/bin/pitft_buttons.py
```
You should have "Active: active (running)".
If not check
 * for syntax errors in python code, if you modified it.
 * python file location
 * python and/or service file permissions

## Modifications

Go for it. You can do it.
