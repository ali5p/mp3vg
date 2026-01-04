from tts_engine import LanguagePairConfig

# Default pause settings (will be overridden by UI values)
DEFAULT_PAUSE_WITHIN_PAIR = 1.1
DEFAULT_PAUSE_BETWEEN_PAIRS = 1.7

LANGUAGE_PROFILES = {
    "en-es": LanguagePairConfig(sequence=["en", "es"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Spanish
    "es-en": LanguagePairConfig(sequence=["es", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-fr": LanguagePairConfig(sequence=["en", "fr"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to French
    "fr-en": LanguagePairConfig(sequence=["fr", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-de": LanguagePairConfig(sequence=["en", "de"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to German
    "de-en": LanguagePairConfig(sequence=["de", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-it": LanguagePairConfig(sequence=["en", "it"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Italian
    "it-en": LanguagePairConfig(sequence=["it", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-pl": LanguagePairConfig(sequence=["en", "pl"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Polish
    "pl-en": LanguagePairConfig(sequence=["pl", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-ru": LanguagePairConfig(sequence=["en", "ru"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Russian
    "ru-en": LanguagePairConfig(sequence=["ru", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-cz": LanguagePairConfig(sequence=["en", "cz"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Czech
    "cz-en": LanguagePairConfig(sequence=["cz", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-sk": LanguagePairConfig(sequence=["en", "sk"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Slovak
    "sk-en": LanguagePairConfig(sequence=["sk", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-hu": LanguagePairConfig(sequence=["en", "hu"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Hungarian
    "hu-en": LanguagePairConfig(sequence=["hu", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-ro": LanguagePairConfig(sequence=["en", "ro"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Romanian
    "ro-en": LanguagePairConfig(sequence=["ro", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS),
    "en-ja": LanguagePairConfig(sequence=["en", "ja"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS), # English to Japanese
    "ja-en": LanguagePairConfig(sequence=["ja", "en"], pause_within_pair=DEFAULT_PAUSE_WITHIN_PAIR, pause_between_pairs=DEFAULT_PAUSE_BETWEEN_PAIRS) 
}    

ACTIVE_PROFILE = "ru-en"