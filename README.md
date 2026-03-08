# gemini-ocr

Batch OCR tool that uses Google Gemini to extract text and math notation from images.

Features:
- Select a parent folder and it processes all image subfolders
- Handles JPG and PNG
- Math notation support (superscripts, subscripts, fractions, roots)
- Progress bar and per-image logging
- Deduplicates images automatically
- Tries multiple Gemini models in priority order

## Setup

```
pip install google-generativeai Pillow
```

Set your API key:

```
export GEMINI_API_KEY=your_key_here
```

```
python gemini_ocr.py
```

Pick your folders, choose an output .txt file, hit start.
