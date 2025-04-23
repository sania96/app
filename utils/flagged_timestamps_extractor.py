import json
import time
import traceback
import re  # Import the regular expression module

class FlaggedTimestampsExtractor:
    def __init__(self, hate_words_file, transcript_file, output_file):
        self.hate_words_file = hate_words_file
        self.transcript_file = transcript_file
        self.output_file = output_file

    def load_hate_words(self):
        with open(self.hate_words_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            print("hate words---------------", json.dumps(data, indent=4))
            return [word.strip().lower() for word in data["issues_detected"].split(",")]

    def load_transcript_words(self):
        try:
            with open(self.transcript_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                print("transcript file-------------", json.dumps(data, indent=4))
            # Check for "words" key at the top level
            if "words" in data:
                return data["words"]
            else:
                raise KeyError("'words' key not found in the transcript JSON. The JSON structure is different than expected.")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading transcript words: {e}")
            traceback.print_exc()
            return []  # Return an empty list to avoid further errors

    def match_hate_words(self, hate_words, transcript_words):
        flagged = []
        for word_data in transcript_words:
            # Remove punctuation from the word before comparison
            word_text = re.sub(r'[^\w\s]', '', word_data["text"]).lower()
            if word_text in hate_words:
                start_seconds = word_data["start"] / 1000.0  # Convert ms to seconds
                end_seconds = word_data["end"] / 1000.0  # Convert ms to seconds
                flagged.append({
                    "word": word_text,
                    "start": start_seconds,
                    "end": end_seconds,
                    "confidence": word_data.get("confidence", None)
                })
        return flagged

    def save_flagged_words(self, flagged_words):
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump({"flagged": flagged_words}, f, indent=4)
        print(f"Flagged timestamps saved to {self.output_file}")

    def extract_flagged_timestamps(self):
        start_time = time.time()
        hate_words = self.load_hate_words()
        transcript_words = self.load_transcript_words()
        flagged = self.match_hate_words(hate_words, transcript_words)
        self.save_flagged_words(flagged)
        print(f"[FlaggedTimestampsExtractor] Time taken: {time.time() - start_time:.2f} seconds")
