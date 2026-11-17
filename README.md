# Machine Translation Module

## Overview

This module performs text translation using the **Google Cloud Translation API v3**. It supports translation between English and German and is integrated into the real-time voice translation pipeline.

The module receives transcribed text from the Speech-to-Text module, translates it into the target language, and passes the translated text to the Text-to-Speech module.

## Translation Service

- Google Cloud Translation API v3
- Python Client Library: `google-cloud-translate`

## Features

- English-to-German Translation
- German-to-English Translation
- Configurable Source and Target Languages
- Google Cloud Translation API Integration
- Integration with Speech-to-Text and Text-to-Speech Modules
- Python-Based Translation Module

## Project Files

- `translator.py` – Text translation module
- `config.py` – Project and translation configuration
- `agent.py` – Voice translation pipeline integration
- `speech_to_text.py` – Speech recognition module
- `text_to_speech.py` – Speech synthesis module
- `whisper_model.py` – Faster-Whisper model integration
- `requirements.txt` – Project dependencies

## Requirements

- Python 3.x
- Internet Connection
- Google Cloud Project
- Google Cloud Translation API enabled
- Google Cloud Service Account Credentials

### Main Dependencies

- `google-cloud-translate==3.28.0`
- `faster-whisper==1.2.1`
- `livekit-agents==1.8.8`
- `piper-tts==1.8.0`
- `torch==2.15.0`

## Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

Configure the Google Cloud project settings in `config.py`.

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your Google Cloud service account JSON file.

For Windows PowerShell:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"
```

**Security Note:** Do not upload service account JSON files, API keys, or other credentials to GitHub.

## Supported Languages

| Language | Code |
|---|---|
| English | `en` |
| German | `de` |

The translation module supports both English-to-German and German-to-English text translation.

## Translation Workflow

1. Speech is captured from the audio input.
2. Faster-Whisper converts speech into text.
3. Google Cloud Translation API translates the recognized text.
4. Piper TTS converts the translated text into speech.
5. The translated audio is played through the voice translation pipeline.

**Pipeline:**

Speech Input → Speech-to-Text → Google Cloud Translation API → Piper TTS → Translated Audio Output

## Running the Application

Activate the Python virtual environment and configure Google Cloud credentials.

Start the voice translation agent:

```powershell
python agent.py start
```

## Current Implementation Status

- English-to-German translation tested with a single caller.
- German-to-English translation tested with a single caller.
- Integration with Faster-Whisper, Google Cloud Translation API, and Piper TTS.
- Two-caller audio routing and simultaneous translation are planned for further development.