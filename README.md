# Vietnamese Real-time Interpreter

A real-time bilingual interpreter for Vietnamese and English using Google Speech Recognition for transcription and Gemini Flash 2.0 for translation.

## Key Features

- **Real-Time Mode**: Live microphone interpretation with audio feedback
- **Fast Translation**: Powered by Gemini Flash 2.0
- **Audio Playback**: Text-to-speech output in both languages
- **Conversation Logging**: Daily conversation logs with timestamps
- **Simple Setup**: Minimal dependencies, no GPU required

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `config.json` and add your Gemini API key and pick your model:

```json
  "models": {
    "gemini": "gemini-2.0-flash"
  },

  "gemini_api_key": "", 
```

Get API key: [Google AI Studio](https://makersuite.google.com/app/apikey)
<br>
Model list: [List](https://ai.google.dev/gemini-api/docs/models)

### 3. Usage

#### Real-Time Mode
```bash
cd src
python main.py --source vi     # Vietnamese to English
python main.py --source en     # English to Vietnamese
```

## Project Structure

```
vietnamese-interpreter/
├── data/
│   └── conversations/    # Daily conversation logs
├── logs/                 # System logs  
├── src/
│   ├── transcription.py   # Speech recognition setup
│   ├── translation.py     # Gemini translation module
│   ├── logger.py          # Centralized logging
│   └── main.py           # Main application
├── config.json           # Configuration and API keys
└── requirements.txt      # Dependencies
```

## How It Works

### Real-Time Mode
1. Start interpreter with source language
2. Speak into microphone
3. System transcribes speech using Google Speech Recognition
4. Translates text using Gemini Flash 2.0
5. Plays translation via text-to-speech
6. Saves conversation to daily log in `data/conversations/`
7. Press 'q' on keyboard to quit anytime

## Usage Examples

### Real-Time Interpretation
```bash
cd src

# Start Vietnamese to English interpreter
python main.py --source vi

# Start English to Vietnamese interpreter  
python main.py --source en

# Verbose output for debugging
python main.py --source vi --verbose
```

## Configuration

Basic `config.json` structure:

```json
{
  "gemini_api_key": "your-gemini-api-key-here",
  "models": {
    "gemini": "gemini-2.0-flash"
  },
  "paths": {
    "logs_dir": "../logs"
  },
  "logging": {
    "log_level": "INFO"
  }
}
```

## System Requirements

- **Python**: 3.9+
- **Internet**: Required for Google APIs
- **Microphone**: For real-time mode
- **Audio Drivers**: For text-to-speech playback

## Controls

- **Speak**: Just talk into the microphone
- **Quit**: Press 'q' on keyboard anytime
- **Pause**: Stop speaking to pause recognition

## Cost Analysis

- **Gemini Flash 2.0**: ~$1 per 1M tokens
- **Gemini Tokenizer**: 100 character ≈ 25 token

## Troubleshooting

1. **API errors**: Verify Gemini API key in config.json
2. **TTS not working**: Install pygame audio drivers
3. **Poor recognition**: Speak clearly, check microphone quality

## Project Summary

### Strengths
- Real-time conversation support with audio feedback
- Simple setup and keyboard controls
- Cost-effective API-based architecture
- Clean conversation logging

### Limitations
- Internet required for all operations
- Only Vietnamese ↔ English supported
- Real-time mode only (remove file processing)

## System use cases
Perfect for: Live conversations, meetings
<br>
Not ideal for: Offline use, audio file processing


