#!/usr/bin/python

########################################
#
# Scott's Kyma System
# Revision notes
# v160809 - Added support for keyboard triggering
# v150512 - Fixed bug causing volume increment and decrement issues
# v150222 - Fixed bug causing crash if volume is adjusted while a pygame.sound is not playing
# v150202 - Long press of right direction results in reload of kyma program and all songs (without reboot). Fixed case sensitiviy bug in new filename convention.
# v150129 - Added support for external flash drive. Songs must be stored in \kyma off root. Bug fixes in old naming conventions support.
# v150127 - implemented LSMS naming convention for files. Old method still works as a fallback.
# v150126 - added "Mix" mode.  Plays back on multiple channels, allowing sounds to overlap.  Useful for keyboard like implementations
#
# Filename convention:
# BBLM_Title.wav
# BB = 2 digit button number (01-12 valid)
# L = L=loop S=single
# M = M=mix S=solo
#######################################

import os

#import sys
#print sys.path
import pygame.mixer
import pygame.key
import sys
import subprocess
from pygame.locals import *
#from time import sleep
import time
import Adafruit_Trellis
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import glob
import re


#Path to sound data
#mypath = "/home/pi/data/"
mypath = "/root/data/"
mypathsd = "/media/usb0/kyma/"

# Keys on the trellis that should not be cleared
special_keys = [12,13,14,15]


# Would normally initialize pygame here
# pygame.init()


###########################################
# Define a function that displays a message on the LCD
def display(message,line):
	global message_line1
	global message_line2

	if line > 2: line=2
	if line < 1: line=1

	if line == 1: message_line1=message
	if line == 2: message_line2=message
 
	lcd.clear()
        lcd.message(message_line1 + "\n" + message_line2)

###########################################

message_line1=""
message_line2=""

###########################################
# Function to (re)Read all of the sounds for a song                                                                             
                                                  
def readsounds(song):
        global files 
	files = []
        dirs = []
        root = []

	# See if this is located on external drive (preceded by *)
	a=re.compile ("^\*(.*)")
	if (a.match(song)):
		m=a.match(song)
		tempsong=m.group(1)
		temppath=os.path.join(mypathsd,tempsong)
	else:
		temppath=os.path.join(mypath,song)

#	print "temppath is ",temppath

        for root, dirs, files in os.walk(temppath):
                path = root.split('/')
	files.sort()

        print "Sounds for ",temppath,": ", files

        # Light up the trellis buttons for the files available                                                                                                                   
        for (index,file) in enumerate(files):
                trellis.setLED(index)

	for i in range (len(files),numKeys):
		if i not in special_keys: trellis.clrLED(i)
#		trellis.clrLED(i)
        trellis.writeDisplay()

#	print "Total of ",len(files)
###########################################                                 





###########################################
# Function to do a sound or function (volume, etc.) triggered by trellis or keyboard
def do_sound_function (i):

				global song_length	# This info is used elsewhere

				if i <= (len(files)-1):
					# Play the file
#					print "mypath = ",mypath
					print "song_selection = ",songs[song_selection]
					print "files = ",files[i]
					# Playmode1 is loop or single (default loop)
					# Playmode2 is mix or solo (default solo)
					# See if this is loop, mix or single (default to loop)
					playmode1 = "Loop"
					playmode2 = "Solo"
					
					# Check to see if this file uses the new naming convention
					a = re.compile("^\d\d(\w)(\w)[_-]")
					if (a.match(files[i])):
						m=a.match(files[i])
						print files[i],"uses LSMS convention"
						if m.group(1) == "S" or m.group(1) == "s":
							playmode1 = "Single"
						if m.group(2) == "M" or m.group(2) == "m":
							playmode2 = "Mix"

					else:  # Use old method with lots of assumptions
						a = re.compile("^\d\d.*[Ss]ingle")
						if a.match(files[i]):
							playmode1="Single"
						a = re.compile("^\d\d.*[Mm]ix")
						if a.match(files[i]):
						       	playmode2="Mix"
       					# See if this is located on external drive (preceded by *)
					a=re.compile ("^\*(.*)")
					if (a.match(songs[song_selection])):
						m=a.match(songs[song_selection])
						tempsong=m.group(1)
						temppath=os.path.join(mypathsd,tempsong,files[i])
					else:
						temppath=os.path.join(mypath,songs[song_selection],files[i])			
#      	       				temppath=os.path.join(mypath,songs[song_selection],files[i])			
					print "Playing "+playmode1+" "+playmode2+": ",temppath
					display(files[i],1)

					if playmode2 == "Mix":
						currentsound = pygame.mixer.Sound(temppath)
						if playmode1 == "Single":
							currentsound.play()
						if playmode1 == "Loop":
							currentsound.play(-1)
					elif playmode2 == "Solo":
						if playmode1 == "Single":
							pygame.mixer.music.load(temppath)
							pygame.mixer.music.play(0)
						elif playmode1 == "Loop":
							pygame.mixer.music.load(temppath)
							pygame.mixer.music.play(-1)


					# Get the length of the song for later reference
					a = pygame.mixer.Sound(temppath)
					song_length=a.get_length()
#					print("length",a.get_length())

				elif i==12:
					current_volume_music = round(pygame.mixer.music.get_volume(), 1)
#	       				try:
#				       	    current_volume_sound = round(currentsound.get_volume(), 1)
#					except:
#						print "Could not get volume of current sound."
		       			if not (current_volume_music <= 0): 
						pygame.mixer.music.set_volume(current_volume_music-.1)
						print "Volume dec\n";
#		       			try:
#						if not (current_volume_sound <= 0): currentsound.set_volume(current_volume_sound-.1)
#					except:
#						 print "Attempted to adjust sound volume when no sound is playing."
					current_volume_music = round(pygame.mixer.music.get_volume(), 1)
					display ("Vol: " + str(int(current_volume_music*100)) + "%",1)
				elif i==13:
					current_volume_music = round(pygame.mixer.music.get_volume(), 1)
#					try:
#						current_volume_sound = round(currentsound.get_volume(), 1)
#					except:
#						print "Could not get volume of current sound."
					if not (current_volume_music >= 1): 
						pygame.mixer.music.set_volume(current_volume_music+.1)
						print "Volume inc\n"
#					try:
#						if not (current_volume_sound >= 1): currentsound.set_volume(current_volume_sound+.1)
#					except:
#						print "Attempted to adjust sound volume when no sound is playing."
					current_volume_music = round(pygame.mixer.music.get_volume(), 1)
					display ("Vol: " + str(int(current_volume_music*100)) + "%",1)	
				elif i==14:
					print "Stopping"
					display ("Stopped",1)
					pygame.mixer.stop()
					pygame.mixer.music.stop()
				elif i==15:
					print "Fadeout"
					display ("Fadeout",1)
					pygame.mixer.fadeout(3000)
					pygame.mixer.music.fadeout(3000)

# End of do_sound_function
###########################################








###########################################
# Main "function" starts here


# Setup the trellis
MOMENTARY = 0
LATCHING = 1
# Set the mode here:
MODE = LATCHING
matrix0 = Adafruit_Trellis.Adafruit_Trellis()
# Just one
trellis = Adafruit_Trellis.Adafruit_TrellisSet(matrix0)
# set to however many you're working with here, up to 8 per I2C bus
NUMTRELLIS = 1
numKeys = NUMTRELLIS * 16
# Set this to the number of the I2C bus that the Trellises are attached to:
I2C_BUS = 1
# begin() with the I2C addresses and bus numbers of each panel in order
# I find it easiest if the addresses are in order
trellis.begin((0x70, I2C_BUS))   # begin the i2c bus for one trellis

# light up all the LEDs in order
for i in range(numKeys):
        trellis.setLED(i)
        trellis.writeDisplay()
        time.sleep(0.01)
# then turn them off
for i in range(numKeys):
        trellis.clrLED(i)
        trellis.writeDisplay()
        time.sleep(0.01)

#print "numKeys is ",numKeys

# Turn on the special buttons
for i in special_keys:
	trellis.setLED(i)
trellis.writeDisplay()

# Clear out any buffered commands in the trellis
trellis.readSwitches()

# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate()

# Setup the LCD buttons as an array
btn = (lcd.LEFT,lcd.UP,lcd.DOWN,lcd.RIGHT,lcd.SELECT)

# Clear display and show greeting, pause 1 sec
lcd.clear()
lcd.backlight(lcd.RED)

#lcd.message("Kyma\nby Scott McGrath")
#sleep(1)
lcd.message ("Loading sounds..")

songs = []
sounds = []


# Read in all of the songs from internal storage
for root, dirs, files in os.walk(mypath):
    path = root.split('/')
    songs.append (os.path.basename(root))
#    songs.sort()

# Read in all of the songs from external storage                                                                                                                                                                                                                              
for root, dirs, files in os.walk(mypathsd):
    path = root.split('/')
    if os.path.basename(root):
	    songs.append ("*" + os.path.basename(root))
	    
songs.sort()

print "Songs: ",songs
print "Songs is ",len(songs)

prev = -1
song_selection = 1
sound_selection = 0


# Setup pygame mixer
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

#print "About to init pygame"
#init_Pygame()
#print "Init pygame done"

#pygame.key.init()
pygame.init()
screen = pygame.display.set_mode((200,200))
pygame.mixer.init()

pygame.mixer.music.set_volume(.6)

# Display the initial song
readsounds(songs[song_selection])
display (songs[song_selection],1)



########  The main loop

button_delay = 10
debounce_timer = button_delay
longpress_timer = 50
recompute_progress = 10

while True:
	time.sleep(0.03)
	if debounce_timer > 0: debounce_timer -= 1

	# Update the song position if playing
	if pygame.mixer.music.get_busy(): 
       		recompute_progress -= 1 # Only update every 10 cycles
	       	if recompute_progress <= 0:
	       		current_pos = pygame.mixer.music.get_pos()
	       		play_percentage = int (((round(((current_pos/1000) % song_length),1)) / song_length) * 100)
	       		progress = ""
			for i in range (0, (play_percentage/13)):
				progress = progress + chr(219)
		       	#display ("Play: " + str(current_pos/1000),2)
			display (str(play_percentage),2)
			display ("Playing: "+ progress,2)
			recompute_progress = 10
	else: display ("",2)



	# Handle the keyboard input
	for event in pygame.event.get():
		if (event.type == KEYDOWN):
			if (event.key == K_1):
				print "1"
				do_sound_function(0)
			if (event.key == K_2):
				print "2"
				do_sound_function(1)
			if (event.key == K_3):
				print "3"
				do_sound_function(2)
			if (event.key == K_4):
				print "4"
				do_sound_function(3)
			if (event.key == K_5):
				print "5-vol dec"
				do_sound_function(12)
			if (event.key == K_6):
				print "6 vol inc"
				do_sound_function(13)
			if (event.key == K_7):
				print "7 stop"
				do_sound_function(14)
			if (event.key == K_8):
				print "8 fadeout"
				do_sound_function(15)










	# Handle the trellis buttons
	# If a button was just pressed or released...
	try:
		switch_pressed=trellis.readSwitches()
	except:
		print "Lost I2C communications (trellis)!"
		time.sleep (1)

       	if switch_pressed:
#		if trellis.readSwitches():
		# go through every button
		for i in range(numKeys):
			# if it was pressed...
			if trellis.justPressed(i):
				print 'v{0}'.format(i)
#				print files[i]
#				print "files is ",len(files)
				do_sound_function(i)

			
	# Handle the Pi Plate buttons	
	for b in btn:
		if lcd.buttonPressed(b):
			if b is lcd.SELECT:
				longpress_timer-=1
				print "Shutdown ",longpress_timer
				if longpress_timer < 1:
					display ("Shutdown",1)
					#os.system("shutdown -h now")
					subprocess.Popen(["/sbin/shutdown"])   # We now launch this as a separate process
					os._exit(-1)  # Must terminate the program or the shutdown doesn't happen.
					
				
			if b is prev and debounce_timer is not 0:
#				print "debounce_timer is ",debounce_timer
				break

			if b is not prev:				
				# Reset debounce timer
				debounce_timer = button_delay

			if b is lcd.UP: 
				if song_selection < (len(songs)-1): song_selection+=1
				else: song_selection=1
				print "song_selection = ",song_selection,"len(songs) = ",len(songs)
				display(songs[song_selection],1)
				readsounds(songs[song_selection])
				prev = b
				debounce_timer = button_delay
				break
			if b is lcd.DOWN: 
				if song_selection > 1: song_selection-=1
				else: song_selection=len(songs)-1
				display(songs[song_selection],1)
				readsounds(songs[song_selection])
				prev = b
				debounce_timer = button_delay
				break
			if b is lcd.RIGHT:
                                longpress_timer-=1
                                print "Reload ",longpress_timer
                                if longpress_timer < 1:
                                        display ("Reload",1)
					sys.exit()				
			if b is lcd.LEFT:
				longpress_timer-=1
				print "Network ",longpress_timer
				if longpress_timer < 1:
					display ("Network",1)
					os.system("systemctl enable networking")
					#os.system("shutdown -r now")
					subprocess.Popen(["/sbin/reboot"])
					os._exit(-1)

			




