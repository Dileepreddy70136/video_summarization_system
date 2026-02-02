import asyncio
import edge_tts
import os

async def main():
    text = "Hello, narrated summary test successful"
    voice = "en-IN-PrabhatNeural"
    out_path = os.path.join("output", "audio", "test.mp3")

    await edge_tts.Communicate(text, voice).save(out_path)
    print("Audio created at:", out_path)

asyncio.run(main())
