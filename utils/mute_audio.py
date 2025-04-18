import subprocess
import json
import time
import shutil
import traceback

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

        if not mute_ranges:
            print("No segments to mute. Copying input video as is...")
            shutil.copyfile(self.video_file, self.output_video_file)
            print("Video copied successfully!")
            print(f"[MuteAudio] Time taken: {time.time() - start_time:.2f} seconds")
            return

        filter_parts = [
            f"volume=enable='between(t,{start},{end})':volume=0" for start, end in mute_ranges
        ]
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
