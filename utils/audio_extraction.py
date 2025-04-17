import subprocess
import traceback
import time

class AudioExtractor:
    def __init__(self, video_path, audio_path):
        self.video_path = video_path
        self.audio_path = audio_path

    def extract_audio(self):
        start_time = time.time()
        try:
            command = [
                "ffmpeg", "-y", "-i", self.video_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
                self.audio_path
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("Audio extraction successful!")
        except Exception as e:
            print("Exception during audio extraction:")
            traceback.print_exc()
        print(f"[AudioExtractor] Time taken: {time.time() - start_time:.2f} seconds")
