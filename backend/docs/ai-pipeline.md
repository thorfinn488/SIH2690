# SIH 26090 - AI Pipeline Integration Guide

This document explains the mock AI service layer, background pipeline execution, and the exact contract that a separate AI team must implement when replacing mock functions with real ML/AI models.

---

## Background Pipeline Orchestration Flow

When `POST /api/products/{id}/process` is called, `pipeline_service.py` executes the following sequence via `FastAPI.BackgroundTasks`:

```
[Start Pipeline]
      |
      v
1. step = "understanding_image"
   ---> analyze_image(image_bytes)
      |
      v
2. step = "understanding_voice"
   ---> transcribe(audio_bytes, language_hint)
   ---> translate_to_english(raw_text, detected_language)
      |
      v
3. step = "generating_catalogue"
   ---> understand_product(transcript, vision_data)
   ---> get_craft_context(craft_name)
      |
      v
4. step = "calculating_price"
   ---> calculate_price(material_cost, days_to_make, complexity, category_avg)
   ---> explain_price(price_breakdown)
      |
      v
5. step = "finding_opportunities"
   ---> find_opportunities(product)
      |
      v
6. step = "done"
   ---> Persist Catalogue, Pricing & Opportunities to DB
   ---> Update product.status = "READY"
```

If any step throws an error, the background task catches the exception, updates `product.status = "FAILED"`, and stores the error message so `GET /api/products/{id}/processing-status` reports an `AI_PROCESSING_FAILED` error.

---

## AI Function Contracts to Implement

The real AI team must implement the exact function signatures below in a `real_ai_services` module. Swapping the imports in `pipeline_service.py` will activate real AI without any backend alterations.

### 1. `analyze_image`
- **Signature**: `def analyze_image(image_bytes: bytes) -> dict:`
- **Expected Return Schema**:
  ```python
  {
      "category": str,
      "detected_material": str,
      "confidence": float,
      "enhanced_image_bytes": bytes
  }
  ```
- **Current implementation**: Reads the uploaded image from the configured storage backend,
  applies local Pillow enhancement (EXIF rotation, contrast, color, and sharpening), and
  persists the enhanced JPEG as a second product image.
- **Recommended Real AI Stack**: BLIP / CLIP / YOLOV8 + Real-ESRGAN image super-resolution.

### 2. `transcribe`
- **Signature**: `def transcribe(audio_bytes: bytes, language_hint: str = "auto") -> dict:`
- **Expected Return Schema**:
  ```python
  {
      "raw_text": str,
      "detected_language": str
  }
  ```
- **Recommended Real AI Stack**: OpenAI Whisper / IndicWhisper.

### 3. `translate_to_english`
- **Signature**: `def translate_to_english(text: str, source_language: str) -> dict:`
- **Expected Return Schema**:
  ```python
  {
      "translated_text": str,
      "source_language": str
  }
  ```
- **Recommended Real AI Stack**: IndicTrans2 / Meta NLLB-200.

### 4. `understand_product`
- **Signature**: `def understand_product(transcript: str, vision_data: dict) -> dict:`
- **Expected Return Schema**:
  ```python
  {
      "name": str,
      "category": str,
      "material": str,
      "craft": str,
      "description": str,
      "tags": list[str],
      "estimated_days_to_make": int,
      "material_cost_estimate": float
  }
  ```
- **Recommended Real AI Stack**: Groq Llama 3.3 / Gemini 1.5 Pro structured extraction.

### 5. `get_craft_context`
- **Signature**: `def get_craft_context(craft_name: str) -> dict:`
- **Expected Return Schema**:
  ```python
  {
      "craft": str,
      "region": str,
      "history": str,
      "typical_materials": list[str]
  }
  ```
- **Recommended Real AI Stack**: Vector DB RAG pipeline over Indian Handicraft Registry.

### 6. `explain_price`
- **Signature**: `def explain_price(price_breakdown: dict) -> str:`
- **Expected Return Schema**: Plain language string explaining pre-computed price breakdown.
- **Rule**: `explain_price` must NEVER generate price numbers; it only wraps calculated numbers in natural language explanations.

### 7. `generate_business_insight`
- **Signature**: `def generate_business_insight(sales_history: list, market_data: dict) -> list[str]:`
- **Expected Return Schema**: List of 2-3 insight strings.

---

## Backend-Owned Functions (Do Not Change in AI Layer)

- **`calculate_price`**: Pure Python formula logic remains strictly owned by the backend to guarantee 100% deterministic pricing calculations.
- **`find_opportunities`**: Database query matching products with buyer requirements based on craft category and match score.
