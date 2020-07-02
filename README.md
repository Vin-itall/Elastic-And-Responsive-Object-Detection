# Elastic-And-Responsive-Object-Detection
Object Detection Appllication Using AWS EC2(Cloud Computing) and Rpi(Edge Computing) 

![alt Architecture](https://github.com/Vin-itall/Elastic-And-Responsive-Object-Detection/blob/master/Architecture.JPG?raw=true)



+ Rpi 
  -> Surveillance: Uses proximity sensor to detect intrusion and starts recording whenever it detects one. It also makes the important decision about whether to upload            the video to S3 bucket to be processed for object detection on the cloud or to do the object detection on the Raspberry Pi itself. If the video needs to be processed on the Rpi itself, it performs object detection on it and uploads the results to output S3 bucket.
  
  -> Upload_this : This file has the utilities that are required to upload the video to a bucket in S3 and puts a message in SQS queue to show that a video is available  for object detection.

+ EC2 Controller
  -> Controller : This runs on an AWS EC2 instance and checks SQSS queue at regular intervals to check if there's any new video that has to be processed. If there is/are new videos available on the queue, it spawns new workers to process them.
 
+ EC2 Worker 
  -> Worker : This runs on an AWS EC2 instance that is spawned by the master and takes a video from the input video S3 bucket and performs object detection on it and uploads the results to output S3 bucket and turns itself of minimizing  wastage of resources.
