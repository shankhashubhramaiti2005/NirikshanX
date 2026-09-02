import os
import math
from PIL import Image, ImageStat, ImageFilter
from typing import Dict, Any, List, Tuple

PRODUCT_DETECTION_THRESHOLD = 0.60

class ProductDetectionService:
    """
    Service for determining whether an uploaded image contains a valid packaged commodity
    or product label versus random/unrelated images (landscapes, people, animals, documents, etc.).
    """

    @staticmethod
    def detect_product(image_path: str, threshold: float = PRODUCT_DETECTION_THRESHOLD) -> Dict[str, Any]:
        if not image_path or not os.path.exists(image_path):
            return {
                "is_product_detected": False,
                "product_confidence": 0.0,
                "label_confidence": 0.0,
                "detected_objects": [],
                "label_regions": [],
                "model_available": True,
                "reason": "Image file not found.",
                "warnings": ["Image path is missing or invalid."]
            }

        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                width, height = img_rgb.size

                # Analyze visual features
                skin_ratio = ProductDetectionService._detect_skin_tone_ratio(img_rgb)
                nature_ratio = ProductDetectionService._detect_nature_landscape_ratio(img_rgb)
                doc_ratio = ProductDetectionService._detect_document_paper_ratio(img_rgb)
                grid_edge_score, high_contrast_cells = ProductDetectionService._analyze_grid_edge_density(img_rgb)
                label_box = ProductDetectionService._estimate_label_region(img_rgb)

                # Base detection scoring
                confidence = 0.50

                # 1. Deduct score for non-product features
                if skin_ratio > 0.20:
                    # High skin tone presence (person / face photo without product)
                    confidence -= min(0.45, (skin_ratio - 0.15) * 1.6)
                
                if nature_ratio > 0.25:
                    # High sky/vegetation presence (landscape photo)
                    confidence -= min(0.45, (nature_ratio - 0.20) * 1.5)

                if doc_ratio > 0.75:
                    # Plain document / text page / paper scan (not packaged commodity label box)
                    confidence -= 0.45

                # 2. Reward score for packaging features
                # Commercial product packages have concentrated high-contrast text/logo grid cells
                if high_contrast_cells >= 4:
                    confidence += min(0.35, high_contrast_cells * 0.05)
                elif high_contrast_cells >= 2:
                    confidence += 0.10
                else:
                    confidence -= 0.20

                if grid_edge_score > 25.0:
                    confidence += min(0.15, (grid_edge_score - 20.0) * 0.005)
                elif grid_edge_score < 12.0:
                    confidence -= 0.25

                # Clamp confidence between 0.02 and 0.98
                product_confidence = round(max(0.02, min(0.98, confidence)), 2)
                is_detected = product_confidence >= threshold

                label_confidence = round(max(0.0, product_confidence - 0.05), 2) if is_detected else 0.05

                detected_objects = []
                label_regions = []
                warnings = []

                if is_detected:
                    detected_objects.append({
                        "class": "packaged_commodity",
                        "confidence": product_confidence,
                        "box": [10, 10, width - 10, height - 10]
                    })
                    if label_box:
                        label_regions.append({
                            "type": "mandatory_declaration_panel",
                            "confidence": label_confidence,
                            "box": label_box
                        })
                    reason = f"Recognizable packaged commodity label detected (Confidence: {product_confidence:.0%})"
                else:
                    if skin_ratio > 0.20:
                        reason = "Image appears to contain a person or portrait rather than a packaged product."
                        warnings.append("Detected portrait/person features. No packaged commodity found.")
                    elif nature_ratio > 0.25:
                        reason = "Image appears to be an outdoor landscape or nature photo."
                        warnings.append("Detected landscape features. No packaged commodity found.")
                    elif doc_ratio > 0.70 and grid_edge_score < 30.0:
                        reason = "Image appears to be a document/paper document rather than packaged commodity packaging."
                        warnings.append("Detected plain document layout. Mandatory commodity packaging panel not present.")
                    elif grid_edge_score < 12.0:
                        reason = "Image lacks structured product packaging or label declarations."
                        warnings.append("No distinct packaging edges or product declarations detected.")
                    else:
                        reason = "No packaged commodity or product label could be reliably detected."
                        warnings.append("The uploaded image does not appear to contain a recognizable packaged commodity.")

                return {
                    "is_product_detected": is_detected,
                    "product_confidence": product_confidence,
                    "label_confidence": label_confidence,
                    "detected_objects": detected_objects,
                    "label_regions": label_regions,
                    "model_available": True,
                    "reason": reason,
                    "warnings": warnings,
                    "metrics": {
                        "skin_ratio": round(skin_ratio, 2),
                        "nature_ratio": round(nature_ratio, 2),
                        "doc_ratio": round(doc_ratio, 2),
                        "grid_edge_score": round(grid_edge_score, 2),
                        "high_contrast_cells": high_contrast_cells
                    }
                }

        except Exception as e:
            return {
                "is_product_detected": False,
                "product_confidence": 0.0,
                "label_confidence": 0.0,
                "detected_objects": [],
                "label_regions": [],
                "model_available": False,
                "reason": f"Error analyzing product image: {str(e)}",
                "warnings": ["Failed to evaluate product packaging detection."]
            }

    @staticmethod
    def _get_pixel_list(sample: Image.Image) -> List[Tuple[int, int, int]]:
        sample_rgb = sample.convert("RGB")
        w, h = sample_rgb.size
        return [sample_rgb.getpixel((x, y)) for y in range(h) for x in range(w)]

    @staticmethod
    def _detect_skin_tone_ratio(img: Image.Image) -> float:
        """Calculates proportion of skin-tone colored pixels (human photo detector)."""
        sample = img.resize((100, 100))
        pixels = ProductDetectionService._get_pixel_list(sample)
        skin_count = 0

        for r, g, b in pixels:
            # Common skin-tone RGB color bounding heuristic
            if r > 95 and g > 40 and b > 20:
                if (max(r, g, b) - min(r, g, b)) > 15:
                    if abs(r - g) > 15 and r > g and r > b:
                        skin_count += 1

        return skin_count / len(pixels)

    @staticmethod
    def _detect_nature_landscape_ratio(img: Image.Image) -> float:
        """Calculates proportion of sky blue / vegetation green pixels (landscape detector)."""
        sample = img.resize((100, 100))
        pixels = ProductDetectionService._get_pixel_list(sample)
        nature_count = 0

        for r, g, b in pixels:
            # Sky Blue
            is_sky = (b > 140 and b > r + 20 and b > g + 10)
            # Vegetation / Grass Green
            is_green = (g > 100 and g > r + 25 and g > b + 25)
            if is_sky or is_green:
                nature_count += 1

        return nature_count / len(pixels)

    @staticmethod
    def _detect_document_paper_ratio(img: Image.Image) -> float:
        """Calculates proportion of paper-like white/light pixels (flat document detector)."""
        sample = img.resize((100, 100))
        pixels = ProductDetectionService._get_pixel_list(sample)
        paper_count = 0

        for r, g, b in pixels:
            # Flat light white/grey background typical of paper document scan/screenshot
            if r > 210 and g > 210 and b > 210:
                if abs(r - g) < 15 and abs(r - b) < 15:
                    paper_count += 1

        return paper_count / len(pixels)

    @staticmethod
    def _analyze_grid_edge_density(img: Image.Image) -> Tuple[float, int]:
        """Divides image into an 8x8 grid and checks edge variance across cells."""
        gray = img.convert("L").resize((160, 160))
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        cell_size = 20  # 8x8 cells
        cell_variances = []
        high_contrast_cells = 0

        for cy in range(8):
            for cx in range(8):
                box = (cx * cell_size, cy * cell_size, (cx + 1) * cell_size, (cy + 1) * cell_size)
                cell_crop = edges.crop(box)
                stat = ImageStat.Stat(cell_crop)
                var = stat.var[0] if stat.var else 0.0
                cell_variances.append(var)
                if var > 500.0:
                    high_contrast_cells += 1

        avg_var = sum(cell_variances) / len(cell_variances) if cell_variances else 0.0
        return avg_var, high_contrast_cells

    @staticmethod
    def _estimate_label_region(img: Image.Image) -> List[int]:
        w, h = img.size
        # Simple estimated bounding box for central product label panel
        return [int(w * 0.15), int(h * 0.15), int(w * 0.85), int(h * 0.85)]
