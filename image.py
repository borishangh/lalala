from pathlib import Path
import os
from PIL import Image
from app import app


def save_img(image, image_path, size=(256, 256)):
    with Image.open(image) as img:
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.convert("RGB").save(image_path, "JPEG")
