from recording_service import Summarizer

text = """
Artificial intelligence is transforming industries worldwide. 
It enhances automation, improves data-driven decision making, 
and powers new types of human–computer interactions. 
Machine learning models continue to advance rapidly.
"""

print("🧠 Testing summarizer...")

summarizer = Summarizer(mode="textrank", num_sentences=2)

summary = summarizer.generate_summary(text)

print("\n✔ Summary:")
print(summary)
