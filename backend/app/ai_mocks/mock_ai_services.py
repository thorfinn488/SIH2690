from io import BytesIO
import json
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from app.config.settings import settings


def analyze_image(image_bytes: bytes) -> dict:
    """
    Mock: return a fixed realistic sample regardless of input.
    Returns: {"category": str, "detected_material": str, "confidence": float, "enhanced_image_bytes": bytes}
    """
    enhanced_image_bytes = _enhance_image(image_bytes)
    return {
        "category": "Handicrafts & Textiles",
        "detected_material": "Cotton & Silk Thread",
        "confidence": 0.94,
        "enhanced_image_bytes": enhanced_image_bytes,
    }


def _enhance_image(image_bytes: bytes) -> bytes:
    """Improve a product photo locally while keeping the AI service contract stable."""
    if not image_bytes:
        return b""

    try:
        with Image.open(BytesIO(image_bytes)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image = ImageEnhance.Contrast(image).enhance(1.12)
            image = ImageEnhance.Color(image).enhance(1.08)
            image = ImageEnhance.Sharpness(image).enhance(1.2)
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=3))
            output = BytesIO()
            image.save(output, format="JPEG", quality=92, optimize=True)
            return output.getvalue()
    except (OSError, ValueError):
        # Keep non-image test fixtures and future providers compatible with the mock contract.
        return image_bytes


def transcribe(audio_bytes: bytes, language_hint: str = "auto") -> dict:
    """
    Mock: return a fixed sample transcript.
    Returns: {"raw_text": str, "detected_language": str}
    """
    return {
        "raw_text": "Yeh handmade Phulkari dupatta cotton aur silk threads se banaya gaya hai. Isme 5 din lage hain.",
        "detected_language": "hi",
    }


def translate_to_english(text: str, source_language: str) -> dict:
    """
    Mock: return input unchanged or translated with a note.
    Returns: {"translated_text": str, "source_language": str}
    """
    translated = "This handmade Phulkari dupatta is crafted from fine cotton and silk threads. It took 5 days of artisan labor to weave."
    return {
        "translated_text": translated,
        "source_language": source_language,
    }


def understand_product(transcript: str, vision_data: dict) -> dict:
    """
    Generate a structured product with Gemini or Groq when configured.
    Falls back to a realistic hardcoded product if the provider is unavailable.
    Returns: {"name": str, "category": str, "material": str, "craft": str,
              "description": str, "tags": list[str],
              "estimated_days_to_make": int, "material_cost_estimate": float}
    """
    fallback = {
        "name": "Handcrafted Phulkari Silk Embroidery Dupatta",
        "category": "Textiles & Apparel",
        "material": "Pure Cotton with Silk Embroidery",
        "craft": "Phulkari",
        "description": "Authentic traditional Phulkari dupatta intricately hand-embroidered by rural women artisans using geometric floral patterns and vibrant silk threads.",
        "tags": ["phulkari", "handmade", "dupatta", "embroidered", "artisan", "traditional"],
        "estimated_days_to_make": 5,
        "material_cost_estimate": 650.0,
    }

    prompt = f"""
You are a product cataloging assistant for Indian artisans. Use the artisan's transcript
and image analysis below to infer a truthful product listing. Do not invent specific
claims that are not supported by the input.

Transcript:
{transcript or "(none provided)"}

Image analysis:
- category: {vision_data.get("category", "")}
- detected material: {vision_data.get("detected_material", "")}

Return only one valid JSON object, with no Markdown fences or extra text, matching this
exact schema and types:
{{
  "name": "string",
  "category": "string",
  "material": "string",
  "craft": "string",
  "description": "string",
  "tags": ["string"],
  "estimated_days_to_make": 0,
  "material_cost_estimate": 0.0
}}
""".strip()

    try:
        if settings.GEMINI_API_KEY:
            if httpx is None:
                raise RuntimeError("httpx is not installed")
            response = httpx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": settings.GEMINI_API_KEY},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"},
                },
                timeout=20.0,
            )
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return _parse_product_response(text)

        if settings.GROQ_API_KEY:
            if httpx is None:
                raise RuntimeError("httpx is not installed")
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "Return only valid JSON matching the requested schema."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                },
                timeout=20.0,
            )
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            return _parse_product_response(text)
    except Exception:
        pass

    return fallback


def _parse_product_response(raw_response: str) -> dict[str, Any]:
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    product = json.loads(cleaned)
    required_fields = {
        "name",
        "category",
        "material",
        "craft",
        "description",
        "tags",
        "estimated_days_to_make",
        "material_cost_estimate",
    }
    if set(product) != required_fields:
        raise ValueError("LLM response did not match the product schema")
    if not all(isinstance(product[field], str) for field in required_fields - {"tags", "estimated_days_to_make", "material_cost_estimate"}):
        raise ValueError("LLM response contains invalid text fields")
    if not isinstance(product["tags"], list) or not all(isinstance(tag, str) for tag in product["tags"]):
        raise ValueError("LLM response contains invalid tags")
    if isinstance(product["estimated_days_to_make"], bool) or not isinstance(product["estimated_days_to_make"], int):
        raise ValueError("LLM response contains invalid production days")
    if isinstance(product["material_cost_estimate"], bool) or not isinstance(product["material_cost_estimate"], (int, float)):
        raise ValueError("LLM response contains invalid material cost")

    product["material_cost_estimate"] = float(product["material_cost_estimate"])
    return product


def get_craft_context(craft_name: str) -> dict:
    """
    Mock: look up from a small hardcoded dict of ~5 Indian crafts
    (Phulkari, Madhubani, Bamboo craft, Wooden handicrafts, Handwoven textiles).
    Returns: {"craft": str, "region": str, "history": str, "typical_materials": list[str]}
    """
    crafts_db = {
        "Phulkari": {
            "craft": "Phulkari",
            "region": "Punjab",
            "history": "Traditional folk embroidery of Punjab, historically crafted by women for festive ceremonies.",
            "typical_materials": ["Cotton fabric", "Untwisted silk floss (pat)"],
        },
        "Madhubani": {
            "craft": "Madhubani",
            "region": "Mithila, Bihar",
            "history": "Ancient wall art tradition featuring nature and mythological themes with natural pigments.",
            "typical_materials": ["Handmade paper", "Canvas", "Natural dyes"],
        },
        "Bamboo craft": {
            "craft": "Bamboo craft",
            "region": "Assam & North East",
            "history": "Eco-friendly utility and decorative craft deeply woven into northeastern cultural heritage.",
            "typical_materials": ["Natural bamboo", "Cane"],
        },
        "Wooden handicrafts": {
            "craft": "Wooden handicrafts",
            "region": "Saharanpur, Uttar Pradesh",
            "history": "Intricate wood carving traditions renowned for floral mesh lattice and brass inlay work.",
            "typical_materials": ["Sheesham wood", "Brass wire"],
        },
        "Handwoven textiles": {
            "craft": "Handwoven textiles",
            "region": "Varanasi / Pochampally",
            "history": "Heritage loom weaving celebrated for rich textures, intricate brocades, and geometric ikat patterns.",
            "typical_materials": ["Mulberry silk", "Organic cotton"],
        },
    }

    # Case-insensitive lookup fallback
    for key, val in crafts_db.items():
        if key.lower() in craft_name.lower():
            return val

    return {
        "craft": craft_name,
        "region": "India",
        "history": "Heritage Indian handicraft preserving cultural legacy and sustainable artisan livelihoods.",
        "typical_materials": ["Natural fibers", "Local raw materials"],
    }


def calculate_price(
    material_cost: float,
    days_to_make: int,
    complexity: str = "medium",
    category_avg: float = 1500.0,
) -> dict:
    """
    THIS IS NOT MOCKED — pure Python deterministic pricing formula implementation.
    complexity is one of "low" | "medium" | "high".
    Formula:
      REGIONAL_DAILY_WAGE = 400 (configured)
      labour = days_to_make * REGIONAL_DAILY_WAGE
      complexity_add = {"low": 0, "medium": 200, "high": 500}[complexity]
      base = material_cost + labour + complexity_add
      suggested = round(base * 1.25, -1)   # 25% margin, rounded to nearest 10
      price_range = (round(suggested * 0.9, -1), round(suggested * 1.15, -1))
    Returns: {"suggested_price": float, "price_range": [float, float]}
    """
    wage = getattr(settings, "REGIONAL_DAILY_WAGE", 400.0)
    labour = float(days_to_make) * float(wage)
    
    complexity_map = {"low": 0.0, "medium": 200.0, "high": 500.0}
    comp_norm = str(complexity).lower()
    complexity_add = complexity_map.get(comp_norm, 200.0)

    base = float(material_cost) + labour + complexity_add
    suggested = float(round(base * 1.25, -1))
    low_price = float(round(suggested * 0.9, -1))
    high_price = float(round(suggested * 1.15, -1))

    return {
        "suggested_price": suggested,
        "price_range": [low_price, high_price],
    }


def explain_price(price_breakdown: dict) -> str:
    """
    Mock: return a template-filled plain-language string wrapping the computed price numbers.
    """
    s_price = price_breakdown.get("suggested_price", 0.0)
    low_p, high_p = price_breakdown.get("price_range", [0.0, 0.0])
    return (
        f"The recommended price of ₹{s_price:,.0f} (suggested market range ₹{low_p:,.0f} - ₹{high_p:,.0f}) "
        f"fairly accounts for raw material costs, artisan craft labor time, and complexity, ensuring a sustainable 25% profit margin."
    )


def generate_business_insight(sales_history: list, market_data: dict) -> list[str]:
    """
    Mock: return 2-3 realistic hardcoded insight strings.
    """
    return [
        "High seasonal demand detected for handwoven textile craft in urban retail markets.",
        "Bundling complementary dupatta designs increases buyer order value by 18%.",
        "Consider highlighting eco-friendly natural dye certifications to premium export buyers.",
    ]


def find_opportunities(product: dict) -> list[dict]:
    """
    Mock: return 2-3 fixed sample opportunities regardless of input.
    Returns: [{"buyer_name": str, "match_score": int, "location": str, "requirement": str}]
    """
    return [
        {
            "buyer_name": "Craftsvilla Heritage Retails",
            "match_score": 92,
            "location": "New Delhi, India",
            "requirement": "Bulk requirement of 50 hand-embroidered silk dupattas for festive collection.",
        },
        {
            "buyer_name": "Ethical Artisans Global Exports",
            "match_score": 86,
            "location": "Mumbai, India",
            "requirement": "Seeking authentic regional textile products with craft story for export catalogs.",
        },
        {
            "buyer_name": "FabIndia Sustainable Sourcing",
            "match_score": 81,
            "location": "Bengaluru, India",
            "requirement": "Sourcing natural cotton Phulkari handicrafts directly from artisan clusters.",
        },
    ]
