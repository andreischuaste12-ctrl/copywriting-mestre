"""Local deterministic copy validation. No network, generation, or telemetry."""
from .validation import InputError, validate_copy

__all__ = ['InputError', 'validate_copy']
