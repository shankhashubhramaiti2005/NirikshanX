import os
import re
from typing import Dict, Any, List
from PIL import Image, ImageFilter, ImageStat

class OCRService:
    """
    Enhanced RapidOCR & Legal Metrology declaration text extraction service.
    Processes product label images using deep learning OCR and parses all mandatory declarations.
    """

    _rapid_ocr_engine = None

    @classmethod
    def get_ocr_engine(cls):
        if cls._rapid_ocr_engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                cls._rapid_ocr_engine = RapidOCR()
            except Exception as e:
                cls._rapid_ocr_engine = False
        return cls._rapid_ocr_engine

    @staticmethod
    def extract_declarations(image_path: str, category: str = "FOOD") -> Dict[str, Any]:
        if not image_path or not os.path.exists(image_path):
            return {
                "raw_text": "",
                "ocr_confidence": 0.0,
                "text_density": 0.0,
                "declarations": {},
                "evidence_found": 0,
                "warnings": ["Image path invalid for OCR extraction."]
            }

        try:
            # 1. Inspect image text features and estimate OCR text density
            with Image.open(image_path) as img:
                gray = img.convert("L").resize((300, 300))
                edges = gray.filter(ImageFilter.FIND_EDGES)
                stat = ImageStat.Stat(edges)
                var = stat.var[0] if stat.var else 0.0

            # 2. Run RapidOCR Engine
            raw_text = ""
            lines: List[str] = []
            scores: List[float] = []
            engine = OCRService.get_ocr_engine()

            if engine:
                try:
                    ocr_res, elapse = engine(image_path)
                    if ocr_res:
                        for box, txt, score in ocr_res:
                            if txt and txt.strip():
                                lines.append(txt.strip())
                                scores.append(float(score))
                        raw_text = "\n".join(lines)
                except Exception as e:
                    pass

            # Fallback to pytesseract if RapidOCR was empty
            if not raw_text:
                try:
                    import pytesseract
                    raw_text = pytesseract.image_to_string(Image.open(image_path))
                    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
                    scores = [0.85] * len(lines)
                except Exception:
                    pass

            # 3. Parse Legal Metrology fields from text
            declarations = OCRService._parse_fields_from_text(raw_text, lines, category)
            
            # Count fields successfully extracted
            found_fields = sum(1 for f in declarations.values() if f.get("value") is not None)
            
            # Calculate overall OCR confidence
            avg_ocr_score = sum(scores) / len(scores) if scores else 0.0
            if found_fields > 0:
                final_ocr_conf = round(max(0.70, min(0.98, avg_ocr_score + (found_fields * 0.04))), 2)
            else:
                final_ocr_conf = round(min(0.40, avg_ocr_score), 2)

            return {
                "raw_text": raw_text,
                "ocr_confidence": final_ocr_conf,
                "text_density": round(min(1.0, var / 250.0), 2),
                "declarations": declarations,
                "evidence_found": found_fields,
                "warnings": [] if found_fields > 0 else ["No mandatory regulatory declarations could be parsed from image text."]
            }

        except Exception as e:
            return {
                "raw_text": "",
                "ocr_confidence": 0.0,
                "text_density": 0.0,
                "declarations": {},
                "evidence_found": 0,
                "warnings": [f"OCR extraction failure: {str(e)}"]
            }

    @staticmethod
    def _parse_fields_from_text(text: str, lines: List[str], category: str) -> Dict[str, Dict[str, Any]]:
        text_upper = text.upper()
        res: Dict[str, Dict[str, Any]] = {}

        # 1. Product Name Extraction
        prod_name = None
        # Check lines for brand keywords or top prominent lines
        for line in lines:
            l_up = line.upper()
            if any(k in l_up for k in ["DAIRY MILK", "CADBURY", "COOKIES", "FLOUR", "BISCUITS", "CHIPS", "CHOCOLATE", "OATS", "TEA", "COFFEE", "MILK", "JUICE", "ATTA", "SNACK", "NOODLES", "OIL", "SOAP", "SHAMPOO", "CREAM", "TABLET", "CAPSULE", "SYRUP"]):
                prod_name = line.strip()
                break
        if not prod_name and lines:
            for l in lines[:3]:
                if len(l) > 3 and not any(c in l.upper() for c in ["MRP", "NET QTY", "PKD", "MFD", "FSSAI", "INGREDIENTS"]):
                    prod_name = l.strip()
                    break

        res["product_name"] = {"value": prod_name, "confidence": 0.90 if prod_name else 0.0}

        # 2. Net Quantity Extraction
        net_qty = None
        net_match = re.search(r'(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT)?|WEIGHT|NET)\s*:?\s*(\d+(?:\.\d+)?\s*(?:G|KG|ML|L|GRAMS|KILOGRAMS|LITRES|LITER|UNITS|PCS|N\.W\.?)\b)', text_upper)
        if net_match:
            net_qty = net_match.group(1).title()
        else:
            # Fallback regex for quantity numbers followed by g/kg/ml/l
            net_standalone = re.search(r'\b(\d+(?:\.\d+)?\s*(?:G|KG|ML|L|GRAMS|KILOGRAMS|LITRES|LITER))\b', text_upper)
            if net_standalone:
                net_qty = net_standalone.group(1).title()

        res["net_quantity"] = {"value": net_qty, "confidence": 0.92 if net_qty else 0.0}

        # 3. Maximum Retail Price (MRP) Extraction
        mrp_val = None
        mrp_match = re.search(r'(?:MRP|MAX\.?\s*RETAIL\s*PRICE|PRICE|RS\.?|₹)\s*:?\s*(?:RS\.?|₹)?\s*(\d+(?:\.\d{1,2})?)', text_upper)
        if mrp_match:
            mrp_val = f"Rs. {mrp_match.group(1)} (Incl. of all taxes)"
        else:
            mrp_standalone = re.search(r'\b(?:RS\.?|₹)\s*(\d+(?:\.\d{1,2})?)\b', text_upper)
            if mrp_standalone:
                mrp_val = f"Rs. {mrp_standalone.group(1)} (Incl. of all taxes)"

        res["mrp"] = {"value": mrp_val, "confidence": 0.94 if mrp_val else 0.0}

        # 4. FSSAI License Extraction (14-digit number)
        fssai_val = None
        fssai_match = re.search(r'\b(\d{14})\b', text_upper)
        if fssai_match:
            fssai_val = fssai_match.group(1)
        res["fssai_license"] = {"value": fssai_val, "confidence": 0.96 if fssai_val else 0.0}

        # 5. Country of Origin
        country_val = None
        country_match = re.search(r'(?:COUNTRY OF ORIGIN|MADE IN|PRODUCED IN|ORIGIN)\s*:?\s*([A-Z ]{3,20})', text_upper)
        if country_match:
            country_val = country_match.group(1).strip().title()
        elif fssai_val or "INDIA" in text_upper:
            country_val = "India"

        res["country_of_origin"] = {"value": country_val, "confidence": 0.91 if country_val else 0.0}

        # 6. Month & Year of Manufacture / Packing
        mfd_val = None
        mfd_match = re.search(r'(?:MFD|PKD|MFG|PACKED|DATE OF MFG|MFG DATE|MFD DATE|PACKED ON)\s*:?\s*([0-9/\.\-]+|\b[A-Z]{3,9}\s*\d{2,4}\b)', text_upper)
        if mfd_match:
            mfd_val = mfd_match.group(1).strip()
        res["month_year_of_manufacture"] = {"value": mfd_val, "confidence": 0.88 if mfd_val else 0.0}

        # 7. Best Before / Expiry Date
        exp_val = None
        exp_match = re.search(r'(?:BEST BEFORE|USE BY|EXP|EXPIRY|EXPIRY DATE)\s*:?\s*([A-Z0-9/\.\-\s]{3,25})', text_upper)
        if exp_match:
            val = exp_match.group(1).split('\n')[0].strip().title()
            exp_val = re.sub(r'\s*MFG.*$', '', val, flags=re.IGNORECASE).strip()
        res["best_before"] = {"value": exp_val, "confidence": 0.88 if exp_val else 0.0}

        # 8. Manufacturer Name
        mfr_name = None
        mfr_match = re.search(r'(?:MFG BY|PACKED BY|MANUFACTURED BY|MARKETED BY|IMPORTED BY)\s*:?\s*([A-ZA-Z0-9\s\.,&\'\-]{3,60})', text)
        if mfr_match:
            mfr_name = mfr_match.group(1).strip()
        else:
            for line in lines:
                if any(k in line.upper() for k in ["PVT LTD", "LIMITED", "FOODS", "INDUSTRIES", "PRIVATE LIMITED", "CORP", "CO."]):
                    mfr_name = line.strip()
                    break

        res["manufacturer_name"] = {"value": mfr_name, "confidence": 0.86 if mfr_name else 0.0}

        # 9. Manufacturer Address
        mfr_addr = None
        for line in lines:
            if any(k in line.upper() for k in ["IND AREA", "INDUSTRIAL AREA", "ROAD", "PLOT", "SECTOR", "PHASE", "NAGAR", "STREET", "CITY", "STATE", "PIN", "MUMBAI", "PUNE", "DELHI", "BANGALORE", "HYDERABAD", "CHENNAI", "KOLKATA"]):
                mfr_addr = line.strip()
                break
        if not mfr_addr:
            addr_match = re.search(r'(?:ADDRESS|FACTORY AT|UNIT AT|REGD OFF)\s*:?\s*([A-ZA-Z0-9\s\.,\-\/]{8,80})', text)
            if addr_match:
                mfr_addr = addr_match.group(1).strip()

        res["manufacturer_address"] = {"value": mfr_addr, "confidence": 0.85 if mfr_addr else 0.0}

        # 10. Ingredients List
        ing_val = None
        ing_match = re.search(r'(?:INGREDIENTS|COMPOSITION|CONTAINS)\s*:?\s*([A-ZA-Z0-9\s\.,%\(\)\-]{5,120})', text)
        if ing_match:
            ing_val = ing_match.group(1).strip()
        res["ingredients"] = {"value": ing_val, "confidence": 0.85 if ing_val else 0.0}

        # 11. Nutritional Information
        nut_val = None
        nut_match = re.search(r'(?:NUTRITIONAL|NUTRITION FACTS|ENERGY|PROTEIN|FAT)\s*:?\s*([A-ZA-Z0-9\s\.,%\(\)\-]{5,120})', text)
        if nut_match:
            nut_val = nut_match.group(1).strip()
        res["nutritional_info"] = {"value": nut_val, "confidence": 0.84 if nut_val else 0.0}

        # 12. Allergen Information
        all_val = None
        all_match = re.search(r'(?:ALLERGEN|CONTAINS GLUTEN|CONTAINS MILK|CONTAINS SOY|CONTAINS NUTS)\s*:?\s*([A-ZA-Z0-9\s\.,%\(\)\-]{5,80})', text)
        if all_match:
            all_val = all_match.group(0).strip()
        res["allergen_info"] = {"value": all_val, "confidence": 0.85 if all_val else 0.0}

        # 13. Batch Number
        batch_val = None
        batch_match = re.search(r'(?:BATCH|LOT|B\.NO|LOT NO)\s*:?\s*([A-ZA-Z0-9\-]{3,20})', text_upper)
        if batch_match:
            batch_val = batch_match.group(1)
        res["batch_number"] = {"value": batch_val, "confidence": 0.88 if batch_val else 0.0}

        # 14. BIS License Number
        bis_val = None
        bis_match = re.search(r'(?:BIS|ISI|CM/L)\s*:?\s*([A-ZA-Z0-9\-]{5,20})', text_upper)
        if bis_match:
            bis_val = bis_match.group(1)
        res["bis_license"] = {"value": bis_val, "confidence": 0.90 if bis_val else 0.0}

        # 15. Customer Care Details
        care_val = None
        care_match = re.search(r'(?:CUSTOMER CARE|HELPLINE|TOLL FREE|CARE NO|FEEDBACK)\s*:?\s*([A-ZA-Z0-9\s\.,@\-]{5,80})', text)
        if care_match:
            care_val = care_match.group(1).strip()
        res["customer_care"] = {"value": care_val, "confidence": 0.86 if care_val else 0.0}

        return res
