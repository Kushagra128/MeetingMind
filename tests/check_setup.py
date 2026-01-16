"""
Setup verification script
Checks if all dependencies and configurations are correct
"""

import os
import sys

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'flask_jwt_extended',
        'flask_sqlalchemy',
        'pyaudio',
        'vosk',
        'nltk',
        'sklearn',
        'numpy',
        'yaml',
        'reportlab'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            elif package == 'sklearn':
                __import__('sklearn')
            else:
                __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_vosk_model():
    """Check if Vosk model exists"""
    config_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'iot-meeting-minutes',
        'configs',
        'recorder_config.yml'
    )
    
    if not os.path.exists(config_path):
        print("❌ Config file not found")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        model_path = config.get('model_path', '')
        if not model_path:
            print("❌ Model path not configured")
            return False
        
        if not os.path.exists(model_path):
            print(f"❌ Vosk model not found at: {model_path}")
            return False
        
        print(f"✓ Vosk model found: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def check_microphone():
    """Check if microphone is available"""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        
        if device_count == 0:
            print("❌ No audio devices detected")
            p.terminate()
            return False
        
        print(f"✓ Found {device_count} audio device(s)")
        p.terminate()
        return True
    except Exception as e:
        print(f"❌ Error checking microphone: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", lambda: check_dependencies()[0]),
        ("Vosk Model", check_vosk_model),
        ("Microphone", check_microphone)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    if not all_passed:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        deps_ok, missing = check_dependencies()
        if not deps_ok:
            print(f"\nInstall missing packages with:")
            print(f"pip install {' '.join(missing)}")
    else:
        print("\n✅ All checks passed! You're ready to run the application.")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)



