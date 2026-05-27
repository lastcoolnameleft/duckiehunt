"""Utility functions for duck number validation."""
from .models import Duck


def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def is_valid_duck_number(n):
    """A valid duck number is > 1 and not prime."""
    return n > 1 and not is_prime(n)


def next_available_duck_id():
    """Find the next available non-prime duck ID not already in use."""
    existing = set(Duck.objects.values_list('duck_id', flat=True))
    candidate = 4  # Start at 4 (first non-prime > 1)
    while True:
        if not is_prime(candidate) and candidate not in existing:
            return candidate
        candidate += 1
