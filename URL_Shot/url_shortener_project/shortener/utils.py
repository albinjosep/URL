import re
from hashlib import sha256

def generate_short_url(original_url):
    hash_object = sha256(original_url.encode('utf-8'))
    return hash_object.hexdigest()[:8]

def is_valid_url(url):
    url_regex = re.compile(r'^(https?|ftp)://\\S+$')
    return url_regex.match(url) is not None
