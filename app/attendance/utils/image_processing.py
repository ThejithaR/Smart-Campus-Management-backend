import cv2
import numpy as np
import base64
from typing import Tuple, Optional

def decode_base64_image(base64_string: str) -> Optional[np.ndarray]:
    """Convert a base64 image string to a numpy array"""
    try:
        # Remove header if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 string
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode the image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None

def encode_image_to_base64(image: np.ndarray) -> Optional[str]:
    """Convert a numpy array image to base64 string"""
    try:
        # Encode the image to jpg format
        success, encoded_image = cv2.imencode('.jpg', image)
        if not success:
            return None
        
        # Convert to base64
        base64_string = base64.b64encode(encoded_image).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_string}"
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None

def resize_image(image: np.ndarray, max_size: int = 800) -> np.ndarray:
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    # Calculate new dimensions
    if height > width:
        if height > max_size:
            ratio = max_size / height
            new_height = max_size
            new_width = int(width * ratio)
        else:
            return image
    else:
        if width > max_size:
            ratio = max_size / width
            new_width = max_size
            new_height = int(height * ratio)
        else:
            return image
    
    # Resize image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized