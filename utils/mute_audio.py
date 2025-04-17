import subprocess
import json
import time
import tempfile
import os

class MuteAudio:
    def __init__(self, video_file, timestamps_file, output_video_file):
        self.video_file = video_file
        self.timestamps_file = timestamps_file
        self.output_video_file = output_video_file

    def load_flagged_timestamps(self):
        with open(self.timestamps_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [(item["start"], item["end"]) for item in data["flagged"]]

    def mute_segments(self, mute_ranges):
        start_time = time.time()

        filter_parts = []
        for start, end in mute_ranges:
            filter_parts.append(f"volume=enable='between(t,{start},{end})':volume=0")

        if not filter_parts:
            print("No segments to mute.")
            return

        filter_complex = ",".join(filter_parts)

        try:
            command = [
                "ffmpeg", "-y", "-i", self.video_file,
                "-filter:a", filter_complex,
                "-c:v", "copy",  # Keep video stream unchanged
                "-c:a", "aac",
                "-preset", "ultrafast",
                self.output_video_file
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("Muted video saved!")
        except Exception as e:
            print("Error during muting:")
            traceback.print_exc()

        print(f"[MuteAudio] Time taken: {time.time() - start_time:.2f} seconds")
