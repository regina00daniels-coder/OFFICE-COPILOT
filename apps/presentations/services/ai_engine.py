def generate_presentation_from_text(text: str):

    sentences = [s.strip() for s in text.split(".") if s.strip()]

    slides = []

    for sentence in sentences:
        slides.append({
            "title": sentence[:50],
            "content": sentence
        })

    return slides
