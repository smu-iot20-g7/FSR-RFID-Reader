#!/usr/bin/env python

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from datetime import datetime
from pymongo import MongoClient

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

db = MongoClient("mongodb+srv://root:0NqePorN2WDm7xYc@cluster0.fvp4p.mongodb.net/iot?retryWrites=true&w=majority")

# Welcome message
print("RFID Detected!")
print("FSR Detected")

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
try:
    while continue_reading:
        # Scan for cards
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        # If a card is found
        rfid_status = 0 # default for rfid
        if status == MIFAREReader.MI_OK:
            print("RFID Tag detected")
            rfid_status = 1 # rfid tag detected
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        current_time = datetime.now()
        print("Time is: " + str(current_time))
        fsr_status = GPIO.input(7)
        print("Weight sensor: " + str(fsr_status))

        if rfid_status == 1 and fsr_status == 1:
            print("RFID and Weight Detected")
            posts = db.fsr_rfid.tray_in
            post_data = {
                'timestamp': current_time,
                'rfid_status': rfid_status,
                'fsr_status': fsr_status
            }
            result = posts.insert_one(post_data)
            print("Inserted with ID: " + str(result))
        time.sleep(3)
except:
  print("Something went wrong")