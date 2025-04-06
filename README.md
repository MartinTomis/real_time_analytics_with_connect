




## Setting up live media streaming in Amazon Connect
0. https://docs.aws.amazon.com/connect/latest/adminguide/customer-voice-streams.html


1. https://docs.aws.amazon.com/connect/latest/adminguide/plan-live-media-streams.html
Kinesis Video Streams multi-track support so that what the customer says is on a separate track from what the customer hears.

2. Enabling Connect streams
https://docs.aws.amazon.com/connect/latest/adminguide/enable-live-media-streams.html
It needs to be enabled in Connect/Data Storage/Live media streaming

Prefix:

```
connect-stream-1
```

3. Accessing Connect streams

https://docs.aws.amazon.com/connect/latest/adminguide/access-media-stream-data.html

Refers to java demo https://github.com/amazon-connect/connect-kvs-consumer-demo

## Defining flow in connect

https://docs.aws.amazon.com/connect/latest/adminguide/use-media-streams-blocks.html




# Very useful repo:
https://github.com/amazon-connect/amazon-connect-realtime-transcription#Sample-trigger-Lambda-function

The Lambda code expects the:
- Kinesis Video Stream details provided by the Amazon Connect Contact Flow as well as the 
- Amazon Connect Contact Id. 

The handler function of the Lambda is present in KVSTranscribeStreamingLambda.java and it uses the GetMedia API of Kinesis Video Stream to fetch the InputStream of the customer audio call. The InputStream is processed using the AWS Kinesis Video Streams provided Parser Library.