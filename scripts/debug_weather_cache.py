import sys
from pathlib import Path
# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ai_radio.services.weather import WeatherService, WeatherData
from datetime import datetime, timedelta
from src.ai_radio.services.cache import cache_get


def ok_client():
    return WeatherData(temperature=55, conditions='sunny')


def failing_client():
    raise Exception('API error')

svc = WeatherService(api_client=ok_client)
print('Before fetch, current in cache:', 'current' in svc._cache._entries)
svc._fetch_and_cache()
print('After fetch, current in cache:', 'current' in svc._cache._entries)
entry = svc._cache._entries.get('current')
print('entry.value.temperature=', entry.value.temperature)
print('entry.created=', entry.created)
# expire
svc._cache._entries['current'].created = datetime.now() - timedelta(minutes=60)
print('expired entry.created=', svc._cache._entries['current'].created)
svc._api_client = failing_client
try:
    w = svc.get_current_weather()
    print('get_current_weather returned', w.temperature)
except Exception as e:
    print('get_current_weather raised', e)

import inspect
print('\n--- cache_get source ---')
print(inspect.getsource(cache_get))
print('defaults:', cache_get.__defaults__)
print('arg names:', cache_get.__code__.co_varnames)

cached = cache_get(svc._cache, 'current', ignore_expiry=True)
print('cache_get ignore_expiry returned', cached.temperature if cached else None)
