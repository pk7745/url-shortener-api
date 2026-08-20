import secrets
import string

# Base62 character set: uppercase letters, lowercase letters, digits
BASE62_ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length: int = 6) -> str:
    """Generate a random, URL-safe short code of specified length using Base62 characters.
    
    Args:
        length: The length of the generated code (default 6 characters).
        
    Returns:
        A random string of Base62 characters.
    """
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))
