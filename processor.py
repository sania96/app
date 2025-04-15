import os
from dotenv import load_dotenv
from app.utils.audio_extraction import AudioExtractor
from app.utils.audio_transcription import AudioTranscriber
from app.utils.transcript_processing import TranscriptProcessor
from app.utils.hate_speech_detection import HateSpeechDetector
from app.utils.flagged_timestamps_extractor import FlaggedTimestampsExtractor
from app.utils.mute_audio import MuteAudio

# Load environment variables from .env file
load_dotenv()

def process_video(video_path):
    base_name = os.path.splitext(os.path.basename(video_path))[0]

    audio_path = f"uploads/{base_name}.wav"
    transcript_json = f"outputs/{base_name}_transcript.json"
    transcript_text = f"outputs/{base_name}_transcript.txt"
    detected_issues = f"outputs/{base_name}_issues.json"
    flagged_timestamps = f"outputs/{base_name}_flagged.json"
    output_video = f"outputs/{base_name}_censored.mp4"

    # Retrieve API keys from environment variables
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    hate_speech_api_key = os.getenv("HATE_SPEECH_API_KEY")

    # Call pipeline
    AudioExtractor(video_path, audio_path).extract_audio()
    AudioTranscriber(deepgram_api_key, audio_path, transcript_json).transcribe_audio()
    TranscriptProcessor(transcript_json, transcript_text).extract_transcript()
    HateSpeechDetector(hate_speech_api_key, transcript_text, detected_issues).detect_issues_in_transcript()
    FlaggedTimestampsExtractor(detected_issues, transcript_json, flagged_timestamps).extract_flagged_timestamps()
    MuteAudio(video_path, flagged_timestamps, output_video).mute_segments(
        MuteAudio(video_path, flagged_timestamps, output_video).load_flagged_timestamps()
    )

    return output_video
