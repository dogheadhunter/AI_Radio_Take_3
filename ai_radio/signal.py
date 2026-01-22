from typing import Iterable


def detect_signal(samples: Iterable[float], threshold: float = 0.5) -> bool:
    """Return True if any sample exceeds the threshold indicating a detected signal.

    Args:
        samples: An iterable of float samples (e.g., normalized audio/magnitude values).
        threshold: Value above which a sample is considered a signal.

    Returns:
        True if a sample > threshold, False otherwise.
    """
    for s in samples:
        try:
            if s > threshold:
                return True
        except TypeError:
            # ignore non-numeric values
            continue
    return False
