# Vietnamese Interpreter POC

A proof-of-concept near-real-time AI interpreter for Vietnamese and English using OpenAI Whisper and NLLB translation models.

## Project Structure

```
vietnamese-interpreter/
├── data/
│   ├── input/          # Place audio files here for testing
│   └── output/         # Processed results will be saved here
├── models/             # Downloaded model cache
├── logs/               # Log files with GMT+7 timestamps
├── src/
│   ├── transcription.py  # Audio transcription module
│   ├── translation.py    # Text translation module
│   └── main.py          # Main application
├── config.json         # Configuration settings
└── requirements.txt    # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Place Audio Files

Copy your Vietnamese or English audio files (WAV, MP3, M4A) to the `data/input/` directory.

### 3. Run the Interpreter

```bash
cd src
python main.py ../data/input/your_audio_file.wav
```

## Example Usage

```bash
# Process a Vietnamese audio file
python main.py ../data/input/vietnamese_speech.wav

# Process an English audio file  
python main.py ../data/input/english_speech.wav
```

## Output

The system will:
1. Transcribe the audio to text
2. Detect the language (Vietnamese or English)
3. Translate to the opposite language
4. Display results on screen
5. Save detailed results to `data/output/interpreter_result_TIMESTAMP.json`

## Configuration

Edit `config.json` to modify:
- Model selections
- Audio processing settings
- Logging preferences
- File paths

## Logs

All operations are logged with GMT+7 timestamps in the `logs/` directory:
- `transcription.txt` - Audio transcription logs
- `translation.txt` - Text translation logs  
- `system.txt` - Main system logs

## System Requirements

- Python 3.8+
- CUDA-compatible GPU (optional, but recommended for better performance)
- At least 4GB RAM
- Internet connection for first-time model downloads

## Supported Formats

- Audio: WAV, MP3, M4A
- Languages: Vietnamese ↔ English

## Performance Targets (POC)

- Word Error Rate (WER): < 10%
- Processing time: < 3 seconds per file
- Translation quality: Basic functional level

## Troubleshooting

1. **Model loading errors**: Ensure stable internet connection for first download
2. **Audio format errors**: Convert audio to WAV format if issues occur
3. **Memory errors**: Try using CPU instead of GPU in config
4. **Import errors**: Install all requirements with `pip install -r requirements.txt`

Check log files in `./logs/` for detailed error information.
