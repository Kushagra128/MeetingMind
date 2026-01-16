import pyaudio
import wave
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 9
OUTPUT_FILE = "mic_test.wav"

print("🎤 Testing microphone... Speak for 5 seconds...")

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

frames = []

start = time.time()
while time.time() - start < RECORD_SECONDS:
    data = stream.read(CHUNK)
    frames.append(data)

print("✔ Recording finished")

stream.stop_stream()
stream.close()
audio.terminate()

with wave.open(OUTPUT_FILE, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"✔ Saved test audio → {OUTPUT_FILE}")
