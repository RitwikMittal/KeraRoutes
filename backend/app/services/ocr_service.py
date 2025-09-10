import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
from typing import Dict, List, Optional
import asyncio
import aiofiles
import os

class OCRService:
    def __init__(self):
        # Configure tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        pass
    
    async def extract_receipt_data(self, image_path: str) -> Dict:
        """Extract data from receipt image using OCR"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not read image"}
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(processed_image, lang='eng+hin')
            
            # Parse receipt data
            parsed_data = self._parse_receipt_text(text)
            
            return {
                "success": True,
                "raw_text": text,
                "extracted_data": parsed_data,
                "image_path": image_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def _parse_receipt_text(self, text: str) -> Dict:
        """Parse receipt text to extract structured data"""
        lines = text.strip().split('\n')
        
        # Initialize result
        result = {
            "total_amount": None,
            "items": [],
            "date": None,
            "merchant_name": None,
            "payment_method": None
        }
        
        # Patterns for different data
        amount_patterns = [
            r'total[\s:]*₹?[\s]*(\d+\.?\d*)',
            r'amount[\s:]*₹?[\s]*(\d+\.?\d*)',
            r'₹[\s]*(\d+\.?\d*)',
            r'rs[\s\.]*(\d+\.?\d*)'
        ]
        
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})'
        ]
        
        # Extract total amount
        for line in lines:
            line_lower = line.lower()
            for pattern in amount_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    try:
                        amount = float(match.group(1))
                        if result["total_amount"] is None or amount > result["total_amount"]:
                            result["total_amount"] = amount
                    except ValueError:
                        continue
        
        # Extract date
        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    result["date"] = match.group(1)
                    break
            if result["date"]:
                break
        
        # Extract merchant name (usually first few lines)
        for line in lines[:3]:
            if len(line.strip()) > 3 and not re.search(r'\d', line):
                result["merchant_name"] = line.strip()
                break
        
        # Extract items (lines with price patterns)
        for line in lines:
            if re.search(r'₹\s*\d+', line) or re.search(r'rs\s*\d+', line.lower()):
                # Clean up the line
                clean_line = re.sub(r'[^\w\s₹\d\.]', ' ', line)
                if len(clean_line.strip()) > 5:
                    result["items"].append(clean_line.strip())
        
        return result

    async def extract_food_photo_data(self, image_path: str) -> Dict:
        """Extract data from food photos for dish identification"""
        try:
            # For now, just return basic info
            # In production, this could use Google Vision API or custom ML model
            return {
                "success": True,
                "detected_food": "Unknown dish",
                "cuisine_type": "Unknown",
                "confidence": 0.5,
                "image_path": image_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }