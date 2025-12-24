# MP3 Vocabulary Generator

**MP3 Vocabulary Generator** is a simple desktop application for generating MP3 audio files from vocabulary word pairs.

It is designed for language learners who want to listen to word translations with natural pronunciation and adjustable pauses.

---

## What This App Does

- Converts word pairs into spoken audio
- Supports **Czech → English** vocabulary
- Generates **MP3 files** suitable for phones and audio players
- Uses natural-sounding speech
- Allows adjustable pauses:
    - between words inside a pair
    - between word pairs

---

## What This App Does NOT Do

- It does **not** require Google Chrome
- It does **not** require a Google account
- It does **not** store or upload your data
- It does **not** work offline (internet connection is required)

---

## How to Use

1. Launch the application
2. Enter word pairs into the text field
    - One pair per line
    - Words separated by a comma

### Input Format

```
Czech,English
```

### Example

```
pes,dog
kočka,cat
dům,house
```

1. Adjust pause settings:
    - Pause inside a word pair (default: 1.1 seconds)
    - Pause between word pairs (default: 1.7 seconds)
2. Click **Generate**
3. The app creates an MP3 file containing all word pairs

---

## Output

- Format: **MP3**
- Quality: **192 kbps**
- Suitable for smartphones, tablets, and audio players

---

## Technical Details

- **Platform**: Windows desktop application
- **GUI Framework**: PySide6 (Qt for Python)
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Audio Processing**: pydub
- **Audio Engine**: ffmpeg (included in the application)

**Important:**

ffmpeg is bundled with the application.

Users do **not** need to install ffmpeg separately.

---

## Limitations

- An active internet connection is required for audio generation
- Audio generation speed may vary
- Very large word lists may take longer to process
- The application depends on third-party TTS availability
- Voice characteristics are determined automatically by the Google Text-to-Speech service and cannot be configured within the application.

---

## Common Errors & Troubleshooting

### “Failed to generate speech”

- Check your internet connection
- Verify spelling of words
- Try again after a short pause (rate limits may apply)

### Audio quality issues

- Ensure a stable internet connection
- Adjust pause durations
- Check that the output folder is writable

---

## Third-Party Software

This application uses third-party open-source software, including:

- Google Text-to-Speech (gTTS)
- pydub
- ffmpeg

Details can be found in `THIRD_PARTY_LICENSES.txt`.

---

## License Notice

This software is licensed for **personal use only**.

Redistribution, resale, or commercial use is prohibited unless explicitly permitted by the author.

---

## Author

**Aliona Sîrf**