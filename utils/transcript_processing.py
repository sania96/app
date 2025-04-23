import json
import traceback
import time

class TranscriptProcessor:
    def __init__(self, json_path, output_path):
        self.json_path = json_path
        self.output_path = output_path

    def extract_transcript(self):
        start_time = time.time()
        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)

            # Check if the transcription was successful
            if data["status"] != "completed":
                raise ValueError(f"Transcription not completed. Status: {data['status']}")

            # Extract the transcript text.  It's now directly in the "text" field.
            transcript = data["text"]

            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(transcript)

            print(f"Transcript saved to: {self.output_path}")

        except Exception as e:
            print("Failed to extract transcript:")
            traceback.print_exc()
        print(f"[TranscriptProcessor] Time taken: {time.time() - start_time:.2f} seconds")
