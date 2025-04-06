import json
import base64
import asyncio
import time
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, AudioEvent

# Initialize Amazon Transcribe client
transcribe_client = TranscribeStreamingClient(region="eu-central-1")  # Adjust to your AWS region

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        print(f"Lenght of RESULTS is: {len(results)}")
        for result in results:
            for alt in result.alternatives:
                log_entry = {
                    "transcription": alt.transcript,
                    "is_partial": result.is_partial
                }
                print(json.dumps(log_entry))
                print(f"Transcript: {alt.transcript}")

async def transcribe_audio(audio_chunks):
    """
    Perform real-time transcription using Amazon Transcribe Streaming.
    """
    # Start transcription to generate our async stream
    stream = await transcribe_client.start_stream_transcription(
        language_code="en-US",  # Adjust to your language
        media_sample_rate_hz=16000,  # Audio sampling rate
        media_encoding="pcm"  # Audio format
    )
    print(f"Full decoded payload in TRANSCRIBE: {audio_chunks}")

    async def write_chunks():
        for chunk in audio_chunks:
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        time.sleep(1)
        await stream.input_stream.end_stream()  # Signal end of stream

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())

def lambda_handler(event, context):
    """
    AWS Lambda function to process audio from Kinesis Stream in real-time.
    """
    audio_chunks = []

    print(f"INITIAL PAYLOAD: {event}")

    # Extract audio from the Kinesis event
    for record in event['Records']:
        print(f"Decoded payload is: {base64.b64decode(record['kinesis']['data'])}")
        #print(f"Decoded payload fron JSON is: {base64.b64decode("SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=")}")
        payload = base64.b64decode(record['kinesis']['data'])
        print(f"Payload size: {len(payload)} bytes")
        audio_chunks.append(payload)

    combined_audio = [b"".join(audio_chunks)]
    print(f"Full decoded payload is: {combined_audio}")
    print(f"Total combined audio size: {len(combined_audio)} bytes")
    # Process transcription asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(transcribe_audio(combined_audio))

    return {
        'statusCode': 200,
        'body': json.dumps('Real-time transcription complete')
    }
