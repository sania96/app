from openai import OpenAI
import json
import traceback

class HateSpeechDetector:
    def __init__(self, api_key, transcript_path, output_path, model_name="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.transcript_path = transcript_path
        self.output_path = output_path
        self.model_name = model_name

    def generate_response(self, user_input):
        try:
            system_prompt = (
                "Detect hate speech, slangs, and offensive language in the text provided. "
                "Always consider one word at a time, it should be not space separated, one entry is ONE WORD ONLY. "
                "*fuck* is also considered as hate word. "
                "Just return the shortlisted words in a comma-separated list."
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=1.0,
                top_p=0.95,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content: {e}")
            traceback.print_exc()
            return None

    def detect_issues_in_transcript(self):
        try:
            with open(self.transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()

            issues = self.generate_response(transcript)

            if issues:
                detected_data = {
                    "issues_detected": issues
                }

                with open(self.output_path, "w", encoding="utf-8") as f:
                    json.dump(detected_data, f, indent=4)

                print(f"Detected issues saved to {self.output_path}")
            else:
                print("No issues detected or there was an error processing the input.")
        except Exception as e:
            print("Failed to process transcript:")
            traceback.print_exc()
