import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

from app.voice.gemini_live import GeminiLiveSession
from app.voice.audio import AudioProcessor

async def main():
    # 1. Connect session 1 to generate speech: "I have a skin rash on my arm, please help me."
    s1 = GeminiLiveSession(is_mock=False)
    await s1.connect()
    print("Session 1 connected. Requesting spoken phrase...")

    collected_audio = bytearray()
    async def s1_listener():
        async for event in s1.receive_events():
            if event.event_type == "audio" and event.audio_pcm:
                collected_audio.extend(event.audio_pcm)
            elif event.event_type == "turn_complete":
                break

    s1_task = asyncio.create_task(s1_listener())
    await asyncio.sleep(0.5)
    await s1.send_text("Say: 'Hello doctor, I have a skin rash on my arm.'")
    await s1_task
    await s1.close()
    print(f"Captured {len(collected_audio)} bytes of 24kHz speech audio.")

    # Convert 24kHz to 16kHz PCM (what Gemini Live expects for input)
    pcm16k = AudioProcessor.pcm24k_to_pcm16k(bytes(collected_audio))
    print(f"Converted to {len(pcm16k)} bytes of 16kHz audio.")

    # 2. Connect session 2 as the AI receptionist and feed this audio into it!
    s2 = GeminiLiveSession(is_mock=False)
    await s2.connect()
    print("Session 2 (Receptionist) connected.")

    async def listener():
        print("Listener running on Session 2...")
        turns = 0
        async for event in s2.receive_events():
            print("Session 2 received event:", event.event_type, "text:", event.text)
            if event.event_type == "turn_complete":
                turns += 1
                print(f"Session 2 finished turn {turns}!")
                if turns >= 2:
                    break

    task = asyncio.create_task(listener())

    # Send initial greeting
    await s2.send_text("Greet the patient as Apollo Hospital receptionist.")
    await asyncio.sleep(4)

    # Now stream the 16kHz patient speech in 20ms chunks (640 bytes per chunk)
    print("Streaming patient speech to receptionist...")
    chunk_size = 640
    for i in range(0, len(pcm16k), chunk_size):
        chunk = pcm16k[i:i + chunk_size]
        await s2.send_audio(chunk)
        await asyncio.sleep(0.02)

    # Send 1 second of silence to trigger Gemini VAD end-of-speech
    print("Sending trailing silence for VAD...")
    silence = b"\x00\x00" * 320
    for _ in range(50):
        await s2.send_audio(silence)
        await asyncio.sleep(0.02)

    print("Finished streaming patient speech. Waiting for receptionist response...")

    # Wait up to 10 seconds for response
    await asyncio.sleep(8)
    await s2.close()
    await task

if __name__ == "__main__":
    asyncio.run(main())
