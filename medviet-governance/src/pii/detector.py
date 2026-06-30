# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """Build AnalyzerEngine với các recognizer tùy chỉnh cho tiếng Việt."""

    # TASK 2.2.1 — CCCD: đúng 12 chữ số
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{12}\b",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd"],
        supported_language="vi"
    )

    # TASK 2.2.2 — Phone: 0[3|5|7|8|9] + 8 chữ số
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b0[35789]\d{8}\b",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ"],
        supported_language="vi"
    )

    # Email recognizer cho tiếng Việt (built-in chỉ hỗ trợ "en")
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        patterns=[Pattern(
            name="email_vi",
            regex=r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
            score=0.9
        )],
        supported_language="vi"
    )

    # TASK 2.2.3 — NLP engine với spaCy Vietnamese model
    try:
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "vi", "model_name": "vi_core_news_lg"}]
        })
        nlp_engine = provider.create_engine()
        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["vi"]
        )
    except Exception:
        # Fallback nếu model chưa được cài đặt
        analyzer = AnalyzerEngine(supported_languages=["vi", "en"])

    # TASK 2.2.4 — Thêm recognizers vào registry
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(email_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """Detect PII trong text tiếng Việt, trả về list RecognizerResult."""
    results = analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results
