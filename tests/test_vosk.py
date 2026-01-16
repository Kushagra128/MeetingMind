import os
import wave
import json
from vosk import Model, KaldiRecognizer

# Paths
MODEL_PATH = os.path.join("..", "vosk-model-small-en-in-0.4")
AUDIO_FILE = "mic_test.wav"   # the file you just recorded with test_mic.py


def main():
    print("🎤 Loading Vosk model...")
    if not os.path.isdir(MODEL_PATH):
        print(f"❌ Model folder not found at: {MODEL_PATH}")
        return

    if not os.path.isfile(AUDIO_FILE):
        print(f"❌ Audio file not found: {AUDIO_FILE}")
        return

    model = Model(MODEL_PATH)

    wf = wave.open(AUDIO_FILE, "rb")

    # Basic sanity check
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        print("⚠️ Expected 16-kHz 16-bit mono WAV.")
        print(f"   Channels:  {wf.getnchannels()}")
        print(f"   SampleWidth: {wf.getsampwidth()}")
        print(f"   SampleRate:  {wf.getframerate()}")
        print("You may need to re-record with the same settings as your app.")
        return

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    print("🎧 Processing audio...")

    full_chunks = []  # <- we accumulate all final pieces here

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            # We got a FINAL chunk for everything up to here
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()
            if text:
                print("Final chunk:", text)
                full_chunks.append(text)
        else:
            # Streaming partial – just for debugging / live display
            partial = json.loads(rec.PartialResult())
            ptext = partial.get("partial", "").strip()
            if ptext:
                print("Partial:", ptext)

    # Get final tail after EOF
    last = json.loads(rec.FinalResult())
    tail_text = last.get("text", "").strip()
    if tail_text:
        print("Final tail:", tail_text)
        full_chunks.append(tail_text)

    # Join everything
    full_transcript = " ".join(full_chunks).strip()

    print("\n" + "✔ FULL TRANSCRIPT".ljust(20, " ") + ":")
    print(full_transcript if full_transcript else "(no speech recognized)")


if __name__ == "__main__":
    main()
