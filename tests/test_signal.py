from ai_radio.signal import detect_signal
from src.ai_radio.config import SIGNAL_THRESHOLD


def test_detect_signal_true():
    samples = [0.1, 0.4, 0.8, 0.2]
    assert detect_signal(samples, threshold=SIGNAL_THRESHOLD) is True


def test_detect_signal_false():
    samples = [0.01, 0.1, 0.3]
    assert detect_signal(samples, threshold=SIGNAL_THRESHOLD) is False


def test_detect_signal_empty():
    assert detect_signal([], threshold=0.1) is False


def test_detect_signal_non_numeric():
    samples = [0.1, 'a', None, 0.6]
    assert detect_signal(samples, threshold=SIGNAL_THRESHOLD) is True
