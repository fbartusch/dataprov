import logging
import sys
from hashlib import sha1, sha256
from typing import Tuple


def hash_file(filepath: str) -> Tuple[str, str]:
    sha_1 = sha1()
    sha_256 = sha256()
    try:
        with open(filepath, "rb") as file:
            while True:
                data = file.read(sha_1.block_size)
                if not data:
                    break
                sha_1.update(data)
        with open(filepath, "rb") as file:
            while True:
                data = file.read(sha_256.block_size)
                if not data:
                    break
                sha_256.update(data)
        return (sha_1.hexdigest(), sha_256.hexdigest())
    except FileNotFoundError:
        logging.error(f"File {filepath} not found")
        logging.error("Aborting")
        sys.exit(1)
