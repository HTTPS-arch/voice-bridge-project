# VoiceBridge

VoiceBridge is an voice translation pipeline that transforms spoken English into translated speech using modern AI models. It captures spoken input, transcribes it into text, translates it into a target language, and plays the translated result back as natural-sounding speech. The system also reports confidence scores for both speech recognition and translation, providing insight into the reliability of each stage.

## Features

* **Speech Recognition** — Captures microphone audio and transcribes spoken English using the Faster-Whisper ASR model.
* **Machine Translation** — Translates English text into the selected target language using Meta's NLLB-200 model.
* **Multi-Language Support** — Select your target language at runtime. Currently supports French and German, with additional languages planned.
* **Text-to-Speech Playback** — Converts translated text into natural-sounding speech using free Microsoft Edge Neural Voices, with a choice of male or female voice.
* **Confidence Scoring** — Reports confidence scores for both speech recognition and translation using each model's own output probabilities rather than fixed or estimated values.
* **Offline-First Pipeline** — Speech recognition and translation run entirely offline after the initial model download. Only the text-to-speech stage requires an internet connection.

## Technologies Used

| Component      | Technology                                  |
| -------------- | ------------------------------------------- |
| Speech-to-Text | Faster-Whisper (Whisper Base model)         |
| Translation    | NLLB-200 (facebook/nllb-200-distilled-600M) |
| Text-to-Speech | edge-tts (Microsoft Edge Neural Voices)     |
| Audio Playback | pygame                                      |
| Audio Capture  | SpeechRecognition, NumPy, SciPy             |

## Project Structure

```text
voice-bridge-project/
├── main.py              # Orchestrates the complete translation pipeline
├── speech_to_text.py    # Microphone capture and speech transcription
├── whisper_model.py     # Loads the Whisper model at startup
├── translator.py        # NLLB-200 translation logic
├── text_to_speech.py    # Converts translated text to speech
├── config.py            # Model settings and supported languages
├── requirements.txt     # Project dependencies
└── README.md
```

## Installation

1. Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd voice-bridge-project
```

2. *(Optional but recommended)* Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

When the application starts, you will:

1. Select a target language (French or German).
2. Speak into your microphone when prompted.
3. View the recognized text, translated text, and confidence scores.
4. Choose a male or female voice to hear the translated speech.

## Pipeline Overview

```text
Microphone
     │
     ▼
Speech Recognition (Faster-Whisper)
     │
     ▼
English Text
     │
     ▼
Machine Translation (NLLB-200)
     │
     ▼
Translated Text
     │
     ▼
Text-to-Speech (Edge TTS)
     │
     ▼
Spoken Translation
```

## Example Output

```text
Recognized Text : Hello, my name is xyz zxy.
Translated Text : Bonjour, je m'appelle xyz zxy.

Speech Recognition Confidence : 92.4%
Translation Confidence        : 88.1%
Overall System Confidence     : 90.3%
```

## Notes

* The first run downloads the Whisper and NLLB-200 models (several GB in total). Subsequent runs use the locally cached models and start significantly faster.
* Confidence scores are calculated directly from each model's output probabilities. As a result, scores naturally vary depending on factors such as audio quality, pronunciation, background noise, and sentence complexity.

## Roadmap

* Support for additional target languages.
* Improved noise handling for speech recognition.
* Optional fully offline text-to-speech support.
* Real-time streaming translation.
