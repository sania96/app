import requests
import time
import traceback
import json  # Import the json module

class AudioTranscriber:
    def __init__(self, api_key, audio_path, output_path):
        self.api_key = api_key
        self.audio_path = audio_path
        self.output_path = output_path
        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {
            "authorization": self.api_key,
        }

    def transcribe_audio(self):
        start_time = time.time()
        try:
            # 1. Upload the audio file
            with open(self.audio_path, "rb") as f:
                upload_response = requests.post(self.base_url + "/upload", headers=self.headers, data=f)

            if upload_response.status_code != 200:
                raise RuntimeError(f"Upload failed with status {upload_response.status_code}: {upload_response.text}")
            
            upload_url = upload_response.json()["upload_url"]

            # 2. Submit the transcription job
            data = {
                "audio_url": upload_url,  # Use the uploaded URL
            }
            transcript_response = requests.post(self.base_url + "/transcript", json=data, headers=self.headers)

            if transcript_response.status_code != 200:
                raise RuntimeError(f"Transcription submission failed with status {transcript_response.status_code}: {transcript_response.text}")

            transcript_id = transcript_response.json()['id']
            polling_endpoint = self.base_url + "/transcript/" + transcript_id

            # 3. Poll for the transcription result
            while True:
                polling_response = requests.get(polling_endpoint, headers=self.headers)
                transcription_result = polling_response.json()

                if transcription_result['status'] == 'completed':
                    # 4. Save the transcription to a file
                    with open(self.output_path, "w") as f:
                        json.dump(transcription_result, f, indent=4)  # Save as formatted JSON

                    print(f"Transcription saved to: {self.output_path}")
                    break

                elif transcription_result['status'] == 'error':
                    raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

                else:
                    print("Transcription is still in progress. Checking again in 3 seconds.")
                    time.sleep(3)

        except Exception as e:
            print("Exception during transcription:")
            traceback.print_exc()
        print(f"[AudioTranscriber] Time taken: {time.time() - start_time:.2f} seconds")
