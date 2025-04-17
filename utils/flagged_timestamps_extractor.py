import json
import time

class FlaggedTimestampsExtractor:
    def __init__(self, hate_words_file, transcript_file, output_file):
        self.hate_words_file = hate_words_file
        self.transcript_file = transcript_file
        self.output_file = output_file

    def load_hate_words(self):
        with open(self.hate_words_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [word.strip().lower() for word in data["issues_detected"].split(",")]

    def load_transcript_words(self):
        with open(self.transcript_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["results"]["channels"][0]["alternatives"][0]["words"]

    def match_hate_words(self, hate_words, transcript_words):
        flagged = []
        for word_data in transcript_words:
            word_text = word_data["word"].lower()
            if word_text in hate_words:
                flagged.append({
                    "word": word_text,
                    "start": word_data["start"],
                    "end": word_data["end"],
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
