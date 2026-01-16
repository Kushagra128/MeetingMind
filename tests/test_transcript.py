from recording_service import TranscriptAggregator
import os

SESSION_FOLDER = "test_session"
SESSION_NAME = "test_transcript"

os.makedirs(SESSION_FOLDER, exist_ok=True)

ta = TranscriptAggregator(SESSION_FOLDER, SESSION_NAME)

ta.add_segment("Hello this is a test.")
ta.add_segment("This is the second line.")
ta.add_segment("Testing timestamps and saving.")

file_path = ta.save_transcript()

print("✔ Transcript saved:", file_path)
print("\nFull transcript:")
print(ta.get_full_transcript())
