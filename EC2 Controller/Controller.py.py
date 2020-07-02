import time

import boto3
from collections import deque

sqs = boto3.client('sqs', region_name='us-east-1')
ec2 = boto3.resource('ec2', region_name='us-east-1')
amiId = ''
Queue = 'https://sqs.us-east-1.amazonaws.com/**************'


def checkQueueSize():
    QSize = sqs.get_queue_attributes(
        QueueUrl=Queue,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    QSize = QSize['Attributes']['ApproximateNumberOfMessages']
    return QSize


def getInstances():
    instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['stopped']
    }])
    instance_list = []
    for instance in instances:
        instance_list.append(instance.id)
    return instance_list


def startInstances(queueSize, stoppedinstances):
    start = min(queueSize, len(stoppedinstances))
    ec2.instances.filter(InstanceIds=stoppedinstances[:start]).start()
    for i in stoppedinstances[:start]:
        print(str(i) + ' has been started')
        print(time.localtime())

while True:
    qsize = int(checkQueueSize())
    sinstances = getInstances()
    if qsize > 0:
        if len(sinstances) > 0:
            startInstances(qsize, sinstances)
            time.sleep(45)
        else:
            print('All occupied')
    else :
        print('Queue is empty')
        time.sleep(10)