# Vietnamese Interpreter POC

A bilingual interpreter for Vietnamese and English using OpenAI Whisper large-v3-turbo (inspired by [this post](https://github.com/openai/whisper/discussions/2363#discussion-7264254)) for transcription and Google Gemini Flash 2.0 for a speedy translation. For more detail on project read Project guideline. Also system test on Google Colab is available with the notebook file.

## Current Project Summary

### Pros
- **Clean Architecture**: Modular design with clear separation of concerns
- **Smart Technology**: Gemini Flash 2.0 for fast translation, Whisper for accurate transcription
- **User Control**: Explicit language selection eliminates auto-detection errors
- **Production Ready**: GPU optimization, centralized logging, proper error handling
- **Cost Effective**: API-based translation, no local GPU needed for translation

### Cons
- **Internet Dependent**: Requires stable connection for Gemini API
- **File-Based Only**: No real-time microphone support
- **Limited Scope**: Only Vietnamese ↔ English, no other language pairs
- **No Caching**: Repeated phrases incur API costs
- **Cold Start**: 3-7 second model loading time (no model caching yet)

### Best For
Meeting recordings, interview transcripts, mixed-language documents

### Not Ideal For
Real-time conversations, offline environments where you talk fast

## Key Features

- **High-Speed Translation**: Powered by Gemini Flash 2.0 for fast, accurate translation
- **Bilingual Support**: Vietnamese ↔ English with manual language selection
- **Mixed Language Handling**: Handles code-switching and technical terms naturally
- **Centralized Logging**: Clean, organized logging system with GMT+7 timestamps
- **User-Controlled Language**: No auto-detection - users specify source language explicitly via `--source` flag

## Project Structure

```
vietnamese-interpreter/
├── data/
│   ├── input/          # Place audio files here for processing
│   └── output/         # Processed results saved here
├── logs/               # Centralized logging with separate files
│   ├── transcription.txt  # Audio processing logs
│   ├── translation.txt    # Translation logs
│   └── system.txt         # Main system logs
├── src/
│   ├── transcription.py   # Whisper transcription module
│   ├── translation.py     # Gemini translation module
│   ├── logger.py          # Centralized logging setup
│   └── main.py           # Main application
├── config.json          # Configuration with API keys
└── requirements.txt     # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt  # For Gemini support
```

### 2. Configure API Keys

Edit `config.json` and add your API keys:

```json
{
  "models": {
    "whisper": "openai/whisper-large-v3-turbo",
    "gemini": "gemini-2.0-flash"
  },
  "huggingface_token": "hf_your_token_here",
  "gemini_api_key": "AIzaSyC-your_gemini_api_key_here"
}
```

**Get API Keys:**
You will need account for both websites
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Hugging Face**: [HF Settings](https://huggingface.co/settings/tokens) (optional, for gated models)

### 3. Place Audio Files



### 4. Run the Interpreter

```bash
cd src
python main.py --file <audio_file> --source <language>
```

## Usage Examples

### Basic Usage (Required flags)
Make sure to put your audio files (WAV, MP3, M4A) to the `data/input/` directory.
```bash
# Vietnamese audio
python main.py --file ../data/input/vietnamese_speech.wav --source vi

# English audio  
python main.py --file ../data/input/english_speech.wav --source en

# Short flag version
python main.py -f ../data/input/speech.wav -s vi
```

### Advanced Options
```bash
# Don't save results to file
python main.py -f speech.wav -s vi --no-save

# Verbose output with detailed timing
python main.py -f speech.wav -s en --verbose

# Mixed language (Vietnamese with English tech terms)
python main.py -f mixed_speech.wav -s vi --verbose
```

## Translation API

The translation module supports explicit language selection:

```python
from translation import TextTranslator

translator = TextTranslator()

# Method 1: Direct calls
result = translator.translate("Xin chào", "vi")  # Vietnamese to English
result = translator.translate("Hello", "en")     # English to Vietnamese

# Method 2: Helper methods
vi_result = translator.translate_vietnamese_to_english("Tôi học programming")
en_result = translator.translate_english_to_vietnamese("I love phở")
```

## Output Format

Results are saved to `data/output/interpreter_result_TIMESTAMP.json`:

```json
{
  "input_file": "path/to/audio.wav",
  "transcription": {
    "text": "Transcribed text here",
    "processing_time": 1.23,
    "timestamp": "2025-01-13T10:30:00+07:00"
  },
  "translation": {
    "raw_transcript": "Original text",
    "translated_text": "Translated text",
    "source_language": "vi",
    "target_language": "en",
    "processing_time": 0.85,
    "timestamp": "2025-01-13T10:30:01+07:00"
  },
  "total_processing_time": 2.08
}
```

## Configuration

### Key Settings in `config.json`:

```json
{
  "models": {
    "whisper": "openai/whisper-large-v3-turbo",
    "gemini": "gemini-2.0-flash-exp"
  },
  "huggingface_token": "",
  "gemini_api_key": "",
  "audio": {
    "sample_rate": 16000,
    "supported_formats": [".wav", ".mp3", ".m4a"]
  },
  "logging": {
    "log_level": "INFO"
  }
}
```

## Troubleshooting
- Check logs in `./logs/` directory
- Use `INFO` log level for detailed processing info
- Translation errors are logged in `translation.txt`

## Example Mixed Language Scenarios

```bash
# Vietnamese with English programming terms
python main.py --file tech_talk.wav --source vi

# English with Vietnamese cultural terms  
python main.py --file food_review.wav --source en

# Business meeting with code-switching
python main.py --file meeting.wav --source vi  # Primary language is Vietnamese

# Verbose debugging output
python main.py -f mixed_content.wav -s vi --verbose --no-save
```


