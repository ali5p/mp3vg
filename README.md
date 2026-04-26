# MP3 Vocabulary Generator

**MP3VG** is a lightweight desktop application that converts vocabulary word pairs into spoken MP3 audio files.
It is designed for language learners who want to practice vocabulary through listening with configurable pauses between translations.

---

## What This App Does

- Converts vocabulary **word or phrase pairs** into spoken audio
- Generates natural-sounding speech using Google Text-to-Speech
- Accepts simple text input: one pair per line, separated by a comma
- Supports multiple playback orders:
  - **L1 → L2**
  - **L2 → L1 → L2** (repetition for reinforcement)
- Creates a single **MP3 lesson file** from all pairs
- Allows adjustable pauses:
  - between items inside a pair
  - between pairs
- **L1** and **L2** gTTS language codes are chosen separately (see `language_catalog.py`)
- Normalizes audio volume for consistent playback

---

## What This App Does NOT Do

- It does **not** require Google Chrome
- It does **not** require a Google account
- It does **not** store or upload your data
- It does **not** work offline (internet connection is required)

---

## Development / How to Run

### Requirements

- Python 3.10+
- FFmpeg (either local `ffmpeg/bin` next to the app, or available on PATH)
- Internet connection (gTTS)

### Setup

```bash
git clone https://github.com/ali5p/mp3vg.git
cd mp3vg

python -m venv venv

# Activate environment (PowerShell)
venv\Scripts\activate

pip install -r requirements.txt
```

### Language list

Supported gTTS codes live in **`language_catalog.py`** (`SUPPORTED_LANGUAGE_CODES`). Add or remove short codes there to change the L1/L2 dropdowns. The UI shows codes only (e.g. `en`, `cs`).

**L1 / L2** define the word-column → language binding (first column = L1, second = L2). **Playback Order** controls role playback (e.g. L1→L2, L2→L1→L2).

### Run
```bash
python main.py
```
### Build Executable (Optional)
```bash
pyinstaller mp3vg.spec
```
Output:

dist/MP3_Vocabulary_Generator/

---

## First-Time Setup (FFmpeg)

Before using the application for the first time, install **FFmpeg**.

1. Download FFmpeg from the official builds page:  
   https://www.gyan.dev/ffmpeg/builds/#release-builds

2. Download **ffmpeg-release-essentials.zip**

3. Extract the archive into the **same folder** 
   where `MP3_Vocabulary_Generator.exe` is located.

4. Rename the extracted folder (for example 
   `ffmpeg-8.0.1-essentials_build`) to: ffmpeg

---

## Folder Structure

Your MP3VG folder should look like this:

MP3VG/
├── MP3_Vocabulary_Generator.exe
└── ffmpeg/
    └── bin/
        └── ffmpeg.exe

---

## How to Use

1. Launch the MP3VG app
2. Choose **L1** and **L2** language codes (both are required)
3. Enter word pairs into the text field
    - One pair per line
    - Words separated by a comma

## Input Format

Enter one pair per line using a comma as a separator:

L1 text, L2 text

Examples:

big cat, velká kočka
house, dům
it was a beautiful day, byl to krásný den

4. Adjust pause settings:
    - Pause inside a word pair (default: 0.8 seconds)
    - Pause between word pairs (default: 1.4 seconds)
5. Choose the location and filename for the generated MP3 file
6. Click **Generate**
7. The app creates an MP3 file containing all word pairs

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
- **Audio Engine**: ffmpeg (external dependency; see installation instructions above)

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
- Try again after a short pause (rate limits may apply)

### Audio quality issues

- Ensure a stable internet connection
- Adjust pause durations
- Check that the output folder is writable

---

## Third-Party Software

This application uses the following third-party components:

- **FFmpeg** (LGPL 2.1+, external binary) – https://ffmpeg.org
- **gTTS** (MIT License) – https://github.com/pndurette/gTTS
- **pydub** (MIT License) – https://github.com/jiaaro/pydub
- **PyInstaller** (GPL v2 + special exception) – https://www.pyinstaller.org
- **Qt for Python (PySide6)** (LGPL v3) – https://www.qt.io/qt-for-python

See `THIRD_PARTY_LICENSES.txt` for full license information.

---

## License

This project is licensed under the GPL-3.0 License — see the LICENSE file for details.

---

## Project Status

This project is a completed personal project developed for learning and portfolio purposes.

---

## Author

© 2026 Aliona Sîrf