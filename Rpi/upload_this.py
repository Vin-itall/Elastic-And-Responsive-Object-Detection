#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import threading
import boto3
from botocore.exceptions import ClientError
import random
import string
import subprocess
import re
import json

def add_SQS(obj):
    sqs = boto3.client('sqs')
    queue_url = \
        'https://sqs.us-east-1.amazonaws.com/*****************'
    try:
        sqs.send_message(QueueUrl=queue_url, MessageGroupId=obj[0],
                         MessageBody=obj)
    except e:
        logging.error(e)
        return False
    return True


def randomString():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))


def upload_file_output(dictt,file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3 = boto3.resource('s3')
    s3object = s3.Bucket(bucket).Object(str(file_name)+'.json')
    try:
        s3object.put(Body=(bytes(json.dumps(dictt).encode('UTF-8'))))
    except e:
        logging.error(e)
        return False
    return (True, object_name)

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_name,bucket,object_name)
    except e:
        logging.error(e)
        return False
    return (True, object_name)

def cloudIt(fn):
    print('Clouding video' + str(fn))
    BUCKET_NAME = 'videobucket-01'
    FILE_NAME = fn
    result, filename = upload_file(FILE_NAME, BUCKET_NAME)
    if result:
        add_SQS(filename)
    else:
        print ('ERROR')


def executeIt(fn):
    print('Executing on pi video' + str(fn))
    outfilepath = str('output-Pi(' + fn + ')')
    output = subprocess.run([
        './darknet',
        'detector',
        'demo',
        'cfg/coco.data',
        'cfg/yolov3-tiny.cfg',
        'yolov3-tiny.weights',
        fn,
        ], stdout=subprocess.PIPE, universal_newlines=True)
    parseit = str(output.stdout)
    clean = set()
    put = parseit.split('\n\x1b')
    for i in put:
        if i.endswith('%'):
            t = i.split('Objects:')
            for j in t:
                if j.find('FPS')== -1:
                    x = j.split(':')
                    for k in x:
                        clean.add(re.sub('[^A-Za-z]+', '', k))
    if '' in clean:
        clean.remove('')
    clean = list(clean)
    final = {}
    final['Video'] = str(fn)
    final['Objects'] = str(clean)
    BUCKET_NAME = 'output-01'
    result, filename = upload_file_output(final,outfilepath,BUCKET_NAME)





