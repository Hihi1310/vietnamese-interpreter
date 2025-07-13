import os
import sys
import json

# Add src to path
sys.path.append('src')

def test_configuration():
    """Test if configuration is valid"""
    print("Testing configuration...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ Configuration file loaded successfully")
        
        # Check required directories
        for dir_key, dir_path in config['paths'].items():
            if os.path.exists(dir_path):
                print(f"✓ Directory exists: {dir_path}")
            else:
                print(f"✗ Directory missing: {dir_path}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("\nTesting dependencies...")
    dependencies = [
        'transformers',
        'torch', 
        'librosa',
        'soundfile',
        'webrtcvad',
        'pytz',
        'jiwer'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} is available")
        except ImportError:
            print(f"✗ {dep} is missing")
            missing.append(dep)
    
    if missing:
        print(f"\nTo install missing dependencies:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def test_components():
    """Test if main components can be imported"""
    print("\nTesting components...")
    try:
        from transcription import AudioTranscriber
        print("✓ Transcription module imported")
        
        from translation import TextTranslator
        print("✓ Translation module imported")
        
        from main import VietnameseInterpreter
        print("✓ Main interpreter module imported")
        
        return True
    except Exception as e:
        print(f"✗ Component import error: {e}")
        return False

def main():
    print("Vietnamese Interpreter POC - System Test")
    print("=" * 45)
    
    # Change to project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    config_ok = test_configuration()
    deps_ok = test_dependencies()
    components_ok = test_components()
    
    print("\n" + "=" * 45)
    if config_ok and deps_ok and components_ok:
        print("✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Place audio files in ./data/input/")
        print("2. Run: python src/main.py data/input/your_file.wav")
    else:
        print("✗ Some tests failed. Please check the issues above.")
        print("Run 'pip install -r requirements.txt' if dependencies are missing.")

if __name__ == "__main__":
    main()
