# processor.py
import os
from dotenv import load_dotenv
from app.utils.audio_extraction import AudioExtractor
from app.utils.audio_transcription import AudioTranscriber
from app.utils.transcript_processing import TranscriptProcessor
from app.utils.hate_speech_detection import HateSpeechDetector
from app.utils.flagged_timestamps_extractor import FlaggedTimestampsExtractor
from app.utils.mute_audio import MuteAudio

load_dotenv()

def process_video(video_path):
    base_name = os.path.splitext(os.path.basename(video_path))[0]

    uploads_dir = "uploads"
    outputs_dir = "outputs"

    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    audio_path = os.path.join(uploads_dir, f"{base_name}.wav")
    transcript_json = os.path.join(outputs_dir, f"{base_name}_transcript.json")
    transcript_text = os.path.join(outputs_dir, f"{base_name}_transcript.txt")
    detected_issues = os.path.join(outputs_dir, f"{base_name}_issues.json")
    flagged_timestamps = os.path.join(outputs_dir, f"{base_name}_flagged.json")
    output_video = os.path.join(outputs_dir, f"{base_name}_censored.mp4")

    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    hate_speech_api_key = os.getenv("HATE_SPEECH_API_KEY")

    try:
        audio_extractor = AudioExtractor(video_path, audio_path)
        audio_extractor.extract_audio()

        audio_transcriber = AudioTranscriber(deepgram_api_key, audio_path, transcript_json)
        audio_transcriber.transcribe_audio()

        transcript_processor = TranscriptProcessor(transcript_json, transcript_text)
        transcript_processor.extract_transcript()

        hate_speech_detector = HateSpeechDetector(hate_speech_api_key, transcript_text, detected_issues)
        hate_speech_detector.detect_issues_in_transcript()

        flagged_timestamps_extractor = FlaggedTimestampsExtractor(detected_issues, transcript_json, flagged_timestamps)
        flagged_timestamps_extractor.extract_flagged_timestamps()

        mute_audio = MuteAudio(video_path, flagged_timestamps, output_video)
        mute_audio.mute_segments(mute_audio.load_flagged_timestamps())

        os.remove(audio_path) # Clean up temporary audio file
        os.remove(transcript_json) # Clean up temporary transcript json
        os.remove(transcript_text) # Clean up temporary transcript text
        os.remove(detected_issues) # Clean up temporary detected issues
        os.remove(flagged_timestamps) # Clean up temporary flagged timestamps

        return output_video
    except Exception as e:
        print(f"Error in process_video: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(transcript_json):
            os.remove(transcript_json)
        if os.path.exists(transcript_text):
            os.remove(transcript_text)
        if os.path.exists(detected_issues):
            os.remove(detected_issues)
        if os.path.exists(flagged_timestamps):
            os.remove(flagged_timestamps)
        if os.path.exists(output_video):
            os.remove(output_video) # Remove potentially corrupted output
        raise