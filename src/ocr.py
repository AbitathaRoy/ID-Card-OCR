# src/ocr.py

from pathlib import Path
from PIL import Image
import pytesseract
import cv2


def extract_text(image_path: str) -> str:
    """
    Runs OCR on an image and returns raw extracted text.
    """
    img_path = Path(image_path)

    # Load image using OpenCV
    image = cv2.imread(str(img_path))
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Light denoising / thresholding
    gray = cv2.threshold(
        gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # OCR
    text = pytesseract.image_to_string(gray)

    return text
