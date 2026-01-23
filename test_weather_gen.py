from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.services.weather import WeatherService
import traceback
import sys

print("Starting weather generation test...")
sys.stdout.flush()

try:
    print("Creating weather service...")
    sys.stdout.flush()
    ws = WeatherService()
    
    print("Fetching weather data...")
    sys.stdout.flush()
    wd = ws.get_current_weather()
    print(f'Got weather: {wd.temperature}°F, {wd.conditions}')
    sys.stdout.flush()
    
    print("Creating pipeline...")
    sys.stdout.flush()
    pipeline = GenerationPipeline()
    
    print("Generating weather announcement (text only)...")
    sys.stdout.flush()
    result = pipeline.generate_weather_announcement(hour=6, minute=0, dj='julie', weather_data=wd, text_only=True)
    
    print(f'Success: {result.success}')
    sys.stdout.flush()
    if not result.success:
        print(f'Error: {result.error}')
    else:
        print(f'Generated text file successfully')
except Exception as e:
    print(f"Exception occurred: {e}")
    sys.stdout.flush()
    traceback.print_exc()
