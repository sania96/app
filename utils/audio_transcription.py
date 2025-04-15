from deepgram import DeepgramClient, PrerecordedOptions
import traceback

class AudioTranscriber:
    def __init__(self, api_key, audio_path, output_path):
        self.api_key = api_key
        self.audio_path = audio_path
        self.output_path = output_path

    def transcribe_audio(self):
        try:
            deepgram = DeepgramClient(self.api_key)
            options = PrerecordedOptions(model="nova-3", language="en")

            with open(self.audio_path, 'rb') as audio:
                source = { "buffer": audio }
                response = deepgram.listen.prerecorded.v("1").transcribe_file(source, options)

            with open(self.output_path, "w") as f:
                f.write(response.to_json(indent=4))

            print(f"Transcription saved to: {self.output_path}")

        except Exception as e:
            print("Exception during transcription:")
            traceback.print_exc()
