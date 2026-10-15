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
    Generate a 7-character short ID from the SHA-256 of the URL.
    Deterministic: the same input always gives the same ID.
    """
    hash_obj = hashlib.sha256(full_url.encode('utf-8'))
    hash_digest = hash_obj.digest()
    
    # 8 bytes (64 bits) is far more than 7 Base62 characters can hold, so the truncation below is what limits the ID space
    hash_int = int.from_bytes(hash_digest[:8], byteorder='big')
    
    short_id = base62_encode(hash_int)
    
    return short_id[:7]