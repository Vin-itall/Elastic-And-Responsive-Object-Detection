import os
import time
import boto3
import logging
import subprocess
import json
import re


def upload_file_output(dictt, file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3o = boto3.resource('s3', region_name = 'us-east-1')
    s3object = s3o.Bucket(bucket).Object(str(file_name) + '.json')
    try:
        print('Trying..')
        s3object.put(Body=(bytes(json.dumps(dictt).encode('UTF-8'))))
    except Exception as e:
        logging.error(e)
        return False
    return (True, object_name)


def get_key():
    try:
        sqs = boto3.client('sqs',region_name = 'us-east-1')
        s3 = boto3.client('s3',region_name = 'us-east-1')
        key = sqs.receive_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/**********************')
        Receipt = key['Messages'][0]['ReceiptHandle']
        sqs.change_message_visibility(QueueUrl='https://sqs.us-east-1.amazonaws.com/*********************',
                           ReceiptHandle=Receipt, VisibilityTimeout = 240)
        print(key['Messages'][0]['Body'])
        key = str(key['Messages'][0]['Body'])
        with open(key, 'wb') as f:
            s3.download_fileobj('videobucket-01', key, f)
        subprocess.call(['Xvfb :1', '&', 'export', 'DISPLAY=:1'], shell=True)
        output = subprocess.run([
            './darknet',
            'detector',
            'demo',
            'cfg/coco.data',
            'cfg/yolov3-tiny.cfg',
            'yolov3-tiny.weights',
            key,
        ], stdout=subprocess.PIPE, universal_newlines=True)
        outfilepath = str('output-Slave(' + key + ')')
        parseit = str(output.stdout)
        clean = set()
        put = parseit.split('\n\x1b')
        for i in put:
            if i.endswith('%'):
                t = i.split('Objects:')
                for j in t:
                    if j.find('FPS') == -1:
                        x = j.split(':')
                        for k in x:
                            clean.add(re.sub('[^A-Za-z]+', '', k))
        if '' in clean:
            clean.remove('')
        clean = list(clean)
        final = {}
        final['Video'] = str(key)
        final['Objects'] = str(clean)
        BUCKET_NAME = 'output-01'
        result, filename = upload_file_output(final, outfilepath, BUCKET_NAME)
        if result:
            sqs.delete_message(QueueUrl = 'https://sqs.us-east-1.amazonaws.com/*********************', ReceiptHandle = Receipt)
            time.sleep(1)
            os.system("shutdown -h now");
    except Exception as e:
        logging.error(e)
        os.system("shutdown -h now");
        return False
    return True

get_key()