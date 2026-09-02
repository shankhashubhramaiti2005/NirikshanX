import os
from PIL import Image, ImageStat, ImageFilter
from typing import Dict, Any, List

def check_image_quality(image_path: str) -> Dict[str, Any]:
    """
    Evaluates whether an uploaded image file is usable for AI compliance inspection.
    Checks resolution, exposure, blankness, and contrast/blur.
    """
    if not image_path or not os.path.exists(image_path):
        return {
            "is_usable": False,
            "quality_score": 0.0,
            "reason": "Image file not found or empty path",
            "suggestions": ["Please select and upload a valid image file."]
        }

    try:
        with Image.open(image_path) as img:
            img_conv = img.convert("RGB")
            width, height = img_conv.size
            total_pixels = width * height

            # 1. Resolution Check
            if width < 150 or height < 150 or total_pixels < 25000:
                return {
                    "is_usable": False,
                    "quality_score": 0.20,
                    "reason": f"Image resolution too low ({width}x{height} pixels)",
                    "details": {"width": width, "height": height, "pixels": total_pixels},
                    "suggestions": ["Upload a higher resolution image (at least 300x300 pixels)."]
                }

            # 2. Exposure Check (Mean luminance)
            gray = img.convert("L")
            gray_stat = ImageStat.Stat(gray)
            mean_luminance = gray_stat.mean[0] if gray_stat.mean else 128.0

            if mean_luminance < 15.0:
                return {
                    "is_usable": False,
                    "quality_score": 0.25,
                    "reason": "Image is extremely dark and unreadable",
                    "details": {"mean_luminance": round(mean_luminance, 2)},
                    "suggestions": ["Take photo in better lighting conditions."]
                }
            elif mean_luminance > 240.0:
                return {
                    "is_usable": False,
                    "quality_score": 0.25,
                    "reason": "Image is overexposed / washed out",
                    "details": {"mean_luminance": round(mean_luminance, 2)},
                    "suggestions": ["Reduce camera flash or glaring light reflections."]
                }

            # 3. Blank / Monochrome / Uniform Image Check
            stat = ImageStat.Stat(img_conv)
            std_devs = stat.stddev  # [std_r, std_g, std_b]
            avg_std_dev = sum(std_devs) / len(std_devs) if std_devs else 0.0

            if avg_std_dev < 8.0:
                return {
                    "is_usable": False,
                    "quality_score": 0.10,
                    "reason": "Image appears to be blank, solid color, or lacks visible features",
                    "details": {"std_dev": round(avg_std_dev, 2)},
                    "suggestions": ["Ensure the photo contains a clear, well-lit product packaging label."]
                }

            # 4. Blur / Sharpness Check (Laplacian edge magnitude proxy via PIL edge filter)
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            edge_variance = edge_stat.var[0] if edge_stat.var else 0.0

            if edge_variance < 10.0:
                return {
                    "is_usable": False,
                    "quality_score": 0.35,
                    "reason": "Image quality is blurred or lacks sharp details for OCR",
                    "details": {"edge_variance": round(edge_variance, 2)},
                    "suggestions": ["Hold the camera steady and focus clearly on the product label."]
                }

            # Calculate continuous quality score (0.50 to 1.0)
            resolution_factor = min(1.0, total_pixels / 300000.0)
            sharpness_factor = min(1.0, edge_variance / 200.0)
            quality_score = round(0.50 + 0.30 * resolution_factor + 0.20 * sharpness_factor, 2)

            return {
                "is_usable": True,
                "quality_score": min(1.0, quality_score),
                "reason": "Image quality is sufficient for AI analysis",
                "details": {
                    "dimensions": f"{width}x{height}",
                    "std_dev": round(avg_std_dev, 2),
                    "mean_luminance": round(mean_luminance, 2),
                    "edge_variance": round(edge_variance, 2)
                },
                "suggestions": []
            }

    except Exception as e:
        return {
            "is_usable": False,
            "quality_score": 0.0,
            "reason": f"Corrupted or invalid image file: {str(e)}",
            "suggestions": ["Upload a valid JPG, PNG, or WEBP image."]
        }
