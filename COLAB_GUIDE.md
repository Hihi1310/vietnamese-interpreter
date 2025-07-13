# Vietnamese Interpreter on Google Colab Guide

This guide shows how to run the Vietnamese Interpreter POC on Google Colab using free GPU resources.

## Prerequisites

1. **GitHub Repository**: Push your local project to a GitHub repository
2. **Google Account**: For accessing Google Colab
3. **Audio Files**: Vietnamese/English audio samples for testing

## Step-by-Step Setup

### 1. Prepare Your GitHub Repository

```bash
# In your local project directory
git init
git add .
git commit -m "Initial Vietnamese Interpreter POC"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/vietnamese-interpreter.git
git push -u origin main
```

### 2. Open Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Sign in with your Google account
3. Create a new notebook

### 3. Enable GPU Runtime

1. In Colab: `Runtime` → `Change runtime type`
2. Set **Hardware accelerator** to `GPU`
3. Set **GPU type** to `T4` (free tier)
4. Click `Save`

### 4. Clone and Setup Project

Add these cells to your Colab notebook:

#### Cell 1: Clone Repository
```python
# Clone your repository
!git clone https://github.com/YOUR_USERNAME/vietnamese-interpreter.git
%cd vietnamese-interpreter
```

#### Cell 2: Install Dependencies
```python
# Install required packages
!pip install -q transformers torch librosa pytz jiwer
!pip install -q accelerate  # For faster model loading

# Verify GPU is available
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

#### Cell 3: Verify Installation
```python
# Test system setup
!python test_system.py
```

### 5. Upload Audio Files

#### Option A: Upload from Local Computer
```python
from google.colab import files
import os

# Create input directory if it doesn't exist
os.makedirs('data/input', exist_ok=True)

# Upload files
print("Select audio files to upload (WAV, MP3, M4A):")
uploaded = files.upload()

# Move uploaded files to input directory
for filename in uploaded.keys():
    !mv "{filename}" data/input/
    print(f"Uploaded: {filename}")
```

#### Option B: Download Sample Files
```python
# Download sample audio files for testing
!mkdir -p data/input

# Example: Download sample Vietnamese audio (replace with actual URLs)
!wget -O data/input/vietnamese_sample.wav "https://example.com/vietnamese_audio.wav"
!wget -O data/input/english_sample.wav "https://example.com/english_audio.wav"

# Or create a simple test audio file
!python -c "
import numpy as np
import soundfile as sf
# Generate a simple tone for testing
sample_rate = 16000
duration = 3  # seconds
t = np.linspace(0, duration, int(sample_rate * duration))
audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
sf.write('data/input/test_tone.wav', audio, sample_rate)
print('Created test tone audio file')
"
```

### 6. Run the Interpreter

#### Single File Processing
```python
# Process a single audio file
!python src/main.py data/input/your_audio_file.wav
```

#### Batch Processing
```python
import os
import glob

# Process all audio files in input directory
audio_files = glob.glob('data/input/*.wav') + glob.glob('data/input/*.mp3') + glob.glob('data/input/*.m4a')

for audio_file in audio_files:
    print(f"\n{'='*60}")
    print(f"Processing: {audio_file}")
    print('='*60)
    !python src/main.py "{audio_file}"
```

#### Interactive Processing
```python
# Interactive file selection and processing
import os
from google.colab import files

def process_audio_interactive():
    # List available files
    audio_files = []
    for ext in ['*.wav', '*.mp3', '*.m4a']:
        audio_files.extend(glob.glob(f'data/input/{ext}'))
    
    if not audio_files:
        print("No audio files found in data/input/")
        print("Please upload files first using the upload cell above.")
        return
    
    print("Available audio files:")
    for i, file in enumerate(audio_files):
        print(f"{i+1}. {os.path.basename(file)}")
    
    # Get user selection
    try:
        choice = int(input(f"Select file (1-{len(audio_files)}): ")) - 1
        selected_file = audio_files[choice]
        
        print(f"\nProcessing: {selected_file}")
        !python src/main.py "{selected_file}"
        
    except (ValueError, IndexError):
        print("Invalid selection")

# Run interactive processor
process_audio_interactive()
```

### 7. View Results

#### Display Results
```python
import json
import glob
from datetime import datetime

# Find latest result file
result_files = glob.glob('data/output/interpreter_result_*.json')
if result_files:
    latest_result = max(result_files, key=os.path.getctime)
    
    with open(latest_result, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print("="*60)
    print("LATEST PROCESSING RESULT")
    print("="*60)
    print(f"Input File: {result['input_file']}")
    print(f"Processing Time: {result['total_processing_time']:.2f} seconds")
    print(f"Timestamp: {result['processing_timestamp']}")
    
    print(f"\n--- TRANSCRIPTION ---")
    print(f"Detected Language: {result['transcription']['language']}")
    print(f"Text: {result['transcription']['text']}")
    
    print(f"\n--- TRANSLATION ---")
    print(f"Language Direction: {result['translation']['source_language']} -> {result['translation']['target_language']}")
    print(f"Translated Text: {result['translation']['translated_text']}")
else:
    print("No results found. Process an audio file first.")
```

#### Download Results
```python
# Download all results to your computer
from google.colab import files
import zipfile

# Create zip file of all results
!zip -r results.zip data/output/ logs/

# Download the zip file
files.download('results.zip')
```

### 8. View Logs

```python
# View system logs
print("=== SYSTEM LOGS ===")
!tail -20 logs/system.txt

print("\n=== TRANSCRIPTION LOGS ===")
!tail -20 logs/transcription.txt

print("\n=== TRANSLATION LOGS ===")
!tail -20 logs/translation.txt
```

## Performance Optimization for Colab

### Memory Management
```python
# Clear GPU memory between runs
import torch
torch.cuda.empty_cache()

# Monitor GPU memory usage
!nvidia-smi
```

### Model Caching
```python
# Models will be cached automatically in /root/.cache/huggingface/
# To clear cache if needed:
# !rm -rf /root/.cache/huggingface/transformers/

# To see cache size:
!du -sh /root/.cache/huggingface/ 2>/dev/null || echo "Cache not found"
```

## Troubleshooting

### Common Issues

1. **GPU Not Available**
   ```python
   # Check GPU status
   !nvidia-smi
   # If no GPU, change runtime type to GPU
   ```

2. **Out of Memory**
   ```python
   # Use smaller Whisper model in config.json
   # Change "openai/whisper-large" to "openai/whisper-base"
   ```

3. **Model Loading Slow**
   ```python
   # First run takes longer due to model downloads
   # Subsequent runs use cached models
   ```

4. **Audio Upload Issues**
   ```python
   # Check supported formats
   !file data/input/*
   # Convert if needed using ffmpeg
   !apt-get install -y ffmpeg
   !ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 output.wav
   ```

## Complete Colab Notebook Template

Save this as a template for quick setup:

```python
# Cell 1: Setup
!git clone https://github.com/YOUR_USERNAME/vietnamese-interpreter.git
%cd vietnamese-interpreter
!pip install -q transformers torch librosa pytz jiwer accelerate

# Cell 2: Upload Audio
from google.colab import files
import os
os.makedirs('data/input', exist_ok=True)
uploaded = files.upload()
for filename in uploaded.keys():
    !mv "{filename}" data/input/

# Cell 3: Process Audio
!python src/main.py data/input/YOUR_FILE.wav

# Cell 4: View Results
import json, glob
latest = max(glob.glob('data/output/*.json'), key=os.path.getctime)
with open(latest, 'r', encoding='utf-8') as f:
    result = json.load(f)
print(f"Original: {result['transcription']['text']}")
print(f"Translated: {result['translation']['translated_text']}")
```

## Tips for Free GPU Usage

1. **Session Limits**: Free Colab has ~12 hours session limit
2. **Memory Limits**: Keep sessions under 12GB RAM usage
3. **Model Size**: Use smaller models if you hit memory limits
4. **Save Progress**: Download results regularly as sessions can disconnect
5. **Reconnect**: If disconnected, just re-run the setup cells

This setup gives you access to free GPU processing for your Vietnamese Interpreter POC!
