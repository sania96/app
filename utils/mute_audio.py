from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import json
from moviepy.editor import VideoFileClip, concatenate_audioclips, AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np

class MuteAudio:
    def __init__(self, video_file, timestamps_file, output_video_file):
        self.video_file = video_file
        self.timestamps_file = timestamps_file
        self.output_video_file = output_video_file

    def load_flagged_timestamps(self):
        with open(self.timestamps_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [(item["start"], item["end"]) for item in data["flagged"]]

    def get_silence(self, duration, fps=44100):
        silent_array = np.zeros((int(duration * fps), 2))  # stereo
        return AudioArrayClip(silent_array, fps=fps)

    def mute_segments(self, mute_ranges):
        video = VideoFileClip(self.video_file)
        original_audio = video.audio

        # Build audio timeline
        audio_clips = []
        current_time = 0

        for start, end in mute_ranges:
            # Add normal audio before mute segment
            if start > current_time:
                audio_clips.append(original_audio.subclip(current_time, start))
            # Add silent audio for mute segment
            if end > start:
                duration = end - start
                audio_clips.append(self.get_silence(duration))
            current_time = end

        # Add any remaining audio
        if current_time < original_audio.duration:
            audio_clips.append(original_audio.subclip(current_time))

        # Concatenate all audio segments
        final_audio = concatenate_audioclips(audio_clips)

        # Set the new audio to the video
        final_video = video.set_audio(final_audio)

        final_video.write_videofile(self.output_video_file, codec="libx264", audio_codec="aac")

        # Cleanup
        video.close()
        original_audio.close()
        final_audio.close()
