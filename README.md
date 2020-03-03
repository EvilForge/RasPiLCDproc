# RasPiLCDProc
Implementation and saved config files on Raspberry Pi 4/3b+ LCDProc installation.

## Overview:
I want to use my RasPi as a desktop and not have to spin up my gaming system, while I work from my corporate laptop. Lots of reasons.. noise, power use, etc, and I share monitors. But all I really do is watch email and browse on the desktop during work hours. So a small RasPi makes perfect sense. And, since I have a couple and I like to tinker.. I can make things more useful if I had a separate simple LCD screen driven by the RasPi, that showed me email status, let me control MP3 players, and showed the time.  

Enter LCDproc. A client server software thing for Linux. A software daemon/service runs (LCDd) that connects to the LCD panel, and waits for clients. Clients (lcdproc) connect and send info to the daemon which then manages display and rotation of the info through screens.

Kind of old fashioned. But I happen to have lots of LCD char screens laying around too. ANd yeah, I get I could just buy a DEX setup for my phone, or prop up the tablet, but I like running on the 4k monitor, and having a real keyboard and mouse, and... well phones take up too much of people's lives anyhow right?

So, I am trying to set up one of my RRaspberry Pi 3B+/4 devices with LCDProc, and a LCD screen I got from Banggood. My configuration is the LCD is 4x20 with a PCF8574 16 pin surface mount chip, and it uses the "alternate" wiring config.

I found lots of references to how to set all this up but nothing appeared complete for a guide. I am trying to document what I have working here, and what all I needed, in one place, because I know that at some point, I'll need it again.

If you feel like it, feel free to [buy me a coffee!](https://www.buymeacoffee.com/rbef)

## Links:
Awesome link about how the whole custom pin thing was added to LCDProc. BUT watch out - that last example uses 0x80 for both the back-light and D7. That got me for a while.. see my configs for what worked for me.  https://sourceforge.net/p/lcdproc/discussion/312/thread/00298b2f/

Source for updated HD4470 drive and files:
https://github.com/wilberforce/lcdproc

Good general guide, but the version of LCDProc is now updated. I still cant apt-install it because all the RasPian repositories are missing libtk sources! So manual install, it is..:
https://www.rototron.info/lcdproc-tutorial-for-raspberry-pi/

## Before you follow this explicitly, make sure you're set up the same way for hardware:
- RasPi3b+ (thats all I have to test with, other RasPi version may work also)
- I2C interface through a level converter (bidirectional) to the display, using I2c-1 (pins 2 & 3 on the RasPi)
- I don't know if the pull-up resistors are already there on the LCD (high logic) side, so I put a 5K resistor to VSS (+5V) on the high side SDA and SCL lines for safety.)
- i2c is enabled on he RasPi
- Your hardware is wired like this:
```
PCF8574 PIN:                 8   9      4  5 6              9 10 11 12 16
LCD PIN:       (1, leftmost)VSS VDD V0 RS RW E D0 D1 D2 D3 D4 D5 D6 D7 A  K
PFC8574 Port:                          P0 P1 P2            P4 P5 P6 P7
```
(my back-light is address 0x08, or P3 I think but a simple continuity test from the LCD pin to the chip expander isn't a good test as there is a NPN or PNP driver circuit in between. I think the first 3 pins on the expander can be jumped with solder bridges as well, according to the chip docs, to change the chip address.)

## General config and setup steps:
1. Build RasPian and set up your SD card. (I am using Buster). If you're using an existing install, take an image of your SD card or at least find a way to revert if needed.
2. Run apt-get Update, apt-get upgrade, and if your File Manager immediately closes or starts crashing on open after this, reinstall pcfileman using apt or do sudo apt full-upgrade. Known issue, just have to dig to find the posts on it however.
3. I installed the same aps I use on my RasPi desktop device as my dev RasPi (qmmp, claws mail, notification plugins for claws, vscode from code.headmelted.com)
4. If you haven't done the steps in the Rotron link, like enabling i2c and setting up WiFi and device name and environment, get to it! Following are what I used in combo with the Rotron site
5. These console commands:
```
cd ~
wget http://sourceforge.net/projects/lcdproc/files/lcdproc/0.5.7/lcdproc-0.5.7.tar.gz/download -O lcdproc.tar.gz
tar xzf lcdproc.tar.gz
cd lcdproc-0.5.7
```

6. Dont configure it yet (dont run ./configure). Instead, go grab the hd44780 files from github/wilberforce. Get the hd44780.so, hd44780-i2c.c, hd44780-low.h down to your downloads folder.
7. Copy those files to the right folder.. in my case it extracted to my home folder in a lcdproc-0.5.7 folder. Under that put those 3 files into the server\drivers folder. since you have the zip downloaded you can just overwrite, or be more cautious and rename the existing files first so you save them.. (easier I guess to revert).
8. In the lcdproc-0.5.7 folder there is a LCDd.conf file, edit it to change things as appropriate. 
9. I found I needed to set DriverPath=/usr/local/lib/lcdproc/ (after installing it and figuring out where it went to), the Drive=hd44780, uncomment the hello and goodbye lines, and set up a lot of hd44780 settings. My LCD sits at address 0x3f. I have uploaded my LCDd.conf to github as well. (Watch the i2c_line values, dont duplicate any ports like I did).
10. OK, NOW you can configure by running this in the console at the lcdproc-0.5.7 folder:
```
./configure --enable-seamless-hbars --enable-drivers=hd44780
```

11. Now follow the Rotron guide.. namely:
```
make
sudo make install
```

12. I now have LCDproc installed in the /usr/local folders. In particular, verify the LCDd.conf has your settings (make should have copied from your source in the home folder I think). LCDd.conf and the other config files are at /usr/local/etc for me. you can always search for it using "whereis LCDd.conf"
13. I run it with:
```
sudo LCDd
```
14. I stop it with:
```
pidof LCDd (take the result and use it below)
sudo kill -15 #### (whatever process id you get, send the kill 15 signal to it using this)
```

So, I get the hello and goodbye now. So LCDd is talking correctly to the display. And some further configuration settings in the lcdproc.conf file and now I have a functional system! (Remember, you have to launch lcdproc like you did LCDd... LCDd = listener, lcdproc = client sending stuff to be displayed.) Claws mail even has a plugin for LCDProc, and there are some supposedly easy to implement scripts for qmmp to send track changes to the LCD. 

Update 2/3/20 - I moved over to a 4GB RasPi4, and this proces works still for me to set the new RasPi up. This time I will not set the LCD and lcdproc to start automatically at boot. Instead I have a GPIO monitoring script I will use, to control power to the system fan, LCD, and watch buttons or start/halt, and it will launch the LCDproc stuff. I have provided the script and service file for it in the GPIO service files folder.
