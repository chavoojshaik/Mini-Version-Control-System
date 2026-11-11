import hashlib


def generate_hash(content):

    return hashlib.sha256(content).hexdigest()
