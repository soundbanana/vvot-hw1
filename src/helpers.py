from pathlib import Path
from constants import BUCKET_NAME

def get_object_from_bucket(object_key):
    try:
        with open(Path("/function/storage", BUCKET_NAME, object_key), "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print("File not found in bucket", {"object_key": object_key})
        return ""