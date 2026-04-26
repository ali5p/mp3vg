"""
gTTS language codes available in the UI (union of the former hardcoded pair presets).

Display in the app is the short code only (e.g. en, cs). Extend this tuple to add
languages gTTS supports that you want to expose.
"""

# Sorted for stable QComboBox order; must match gTTS-supported tld/lang codes in practice
SUPPORTED_LANGUAGE_CODES: tuple[str, ...] = (
    "cs",
    "de",
    "en",
    "es",
    "fr",
    "hu",
    "it",
    "ja",
    "ua",
    "pl",
    "ro",
    "ru",
    "sk",
)
