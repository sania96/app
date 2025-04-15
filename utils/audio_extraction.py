from moviepy.editor import VideoFileClip
import traceback

class AudioExtractor:
    def __init__(self, video_path, audio_path):
        self.video_path = video_path
        self.audio_path = audio_path

    def extract_audio(self):
        try:
            video_clip = VideoFileClip(self.video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(self.audio_path)
            audio_clip.close()
            video_clip.close()
            print("Audio extraction successful!")
        except Exception as e:
            print("Exception during audio extraction:")
            traceback.print_exc()
