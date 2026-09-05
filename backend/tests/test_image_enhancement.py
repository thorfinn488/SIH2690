from io import BytesIO

from PIL import Image

from app.ai_mocks.mock_ai_services import analyze_image


def test_analyze_image_returns_enhanced_jpeg_bytes():
    source = BytesIO()
    Image.new("RGB", (32, 24), (120, 80, 40)).save(source, format="PNG")

    result = analyze_image(source.getvalue())

    assert result["category"] == "Handicrafts & Textiles"
    assert result["confidence"] > 0
    with Image.open(BytesIO(result["enhanced_image_bytes"])) as enhanced:
        assert enhanced.format == "JPEG"
        assert enhanced.size == (32, 24)