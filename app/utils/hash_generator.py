import hashlib

def base62_encode(num: int) -> str:
    """
    Encode integer to base62 string (0-9, a-z, A-Z).
    """
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return charset[0]
    
    result = []
    while num > 0:
        num, remainder = divmod(num, 62)
        result.append(charset[remainder])
    
    return ''.join(reversed(result))

def generate_short_id(full_url: str) -> str:
    """
    Generate a 7-character hash-based short ID.
    Uses full_url + user_id (if provided) for uniqueness.
    """
    # Combine full_url with user_id for better distribution
    data = full_url
    # if user_id:
    #     data = f"{full_url}:{user_id}"
    
    # Create SHA-256 hash
    hash_obj = hashlib.sha256(data.encode('utf-8'))
    hash_digest = hash_obj.digest()
    
    # Convert first 8 bytes to integer
    hash_int = int.from_bytes(hash_digest[:8], byteorder='big')
    
    # Encode to base62
    short_id = base62_encode(hash_int)
    
    # Take first 7 characters
    return short_id[:7]