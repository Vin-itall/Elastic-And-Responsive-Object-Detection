#!/usr/bin/python

'''
SETUP:

    -   -->     GND     -->     PIN6
    +   -->     5V      -->     PIN4
    S   -->     GPIO18  -->     PIN12

'''

import RPi.GPIO as GPIO
import subprocess
import time
import sys
from picamera import PiCamera
import sys
import upload_this
import threading
from datetime import datetime

count = 0
flag = True



def record(filepath):
    print('Recording Now...')
    camera = PiCamera()
    camera.resolution = (608, 608)
    camera.start_recording(filepath)
    camera.wait_recording(3)
    camera.stop_recording()
    camera.close()
    print('Record Complete...')
    flag = False
    

    
sensor =12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor, GPIO.IN)

videoqueue = []

localthread = None
on = 0
off = 0
while True:
    i=GPIO.input(sensor)
    if i == 0:
        off = time.time()
        diff = off - on
        print ('time: ' + str(diff%60) + ' sec')
        print ('')
        print ("No intruders")
        if localthread is None or not localthread.is_alive():
                if len(videoqueue)>0:
                    fname = videoqueue.pop(0)
                    localthread = threading.Thread(name='darknet',target=upload_this.executeIt,args=(fname,))
                    localthread.start()
        time.sleep(1)
    elif i == 1:
        if flag:
            print ("---------------------------------------Intruder detected-------------------------------------")
            count+=1
            print("----------------------------------------Change Image" +" Will Record " + str(count)+ " ------------------------------------------")
            time.sleep(3)
            on = time.time()
            filepath = str(str(count)+'-'+'{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())+'.h264')
            record(filepath)
            if len(videoqueue)<3:
                videoqueue.append(filepath)
            else:
                upload_this.cloudIt(filepath)
            if localthread is None or not localthread.is_alive():
                if len(videoqueue)>0:
                    fname = videoqueue.pop(0)
                    localthread = threading.Thread(name='darknet',target=upload_this.executeIt,args=(fname,))
                    localthread.start()


