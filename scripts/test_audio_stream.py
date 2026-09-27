import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

from app.voice.gemini_live import GeminiLiveSession

async def main():
    s = GeminiLiveSession(is_mock=False)
    await s.connect()
    print("Connected to Gemini!")

    async def listener():
        print("Listener active...")
        async for event in s.receive_events():
            print("Received event:", event.event_type, "text:", event.text)
            if event.event_type == "turn_complete":
                print("Turn completed!")
                break

    task = asyncio.create_task(listener())

    # Send silent/tone audio or audio chunk
    print("Sending greeting prompt...")
    await s.send_text("Say 'Hello! I am listening.' in one short sentence.")
    
    # Wait for greeting to finish
    await asyncio.sleep(3)

    # Now let's send some audio chunks
    print("Now streaming 1 second of 16kHz audio...")
    dummy_audio = b"\x00\x00" * 320 # 20ms of 16kHz 16-bit PCM
    for _ in range(50):
        await s.send_audio(dummy_audio)
        await asyncio.sleep(0.02)
    print("Audio streamed!")

    await asyncio.sleep(3)
    await s.close()
    await task

if __name__ == "__main__":
    asyncio.run(main())
