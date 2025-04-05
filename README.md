# Sanskrit Search Engine

A command-line Sanskrit search tool that indexes Devanagari text from PDF documents using a Trie data structure. It supports exact word search and prefix-based autocomplete functionality. Outputs are optionally saved to JSON for later use.

---

## Features

- Extracts text from PDFs using `pdfplumber` or OCR fallback via `pytesseract`
- Normalizes and tokenizes Sanskrit (Devanagari) words
- Indexes words into a persistent Trie structure with document references
- Supports:
  - **Exact word search** (with document and position metadata)
  - **Autocomplete suggestions** for Devanagari prefixes
- Results are printed to terminal and optionally written to file

---

## Architecture

- **Trie Node Structure**: Stores word segments, flags for complete words, and document references
- **Text Extraction**:
  - First attempts to extract text using `pdfplumber`
  - Falls back to OCR using `pytesseract` if no text is found
- **Preprocessing**: Unicode normalization and Devanagari-only filtering
- **Persistent Indexing**: Trie can be saved and reused, avoiding reprocessing PDFs
- **Interactive CLI**: Menu-driven system with numeric input mapped to actions

---

## Usage

### Prepare Your Environment

Install dependencies:

```bash
pip install -r requirements.txt
```

### Install System Dependencies
Ensure Tesseract and Poppler are installed on your system:
Tesseract: https://github.com/tesseract-ocr/tesseract
Poppler: https://github.com/oschwartz10612/poppler-windows

### Add Your Documents
Place all Sanskrit PDFs in the ./docs directory.

4. Run the Engine
```bash
python search_engine.py

📚 Sanskrit Search Engine Ready
[1] Search Word
[2] Autocomplete
[3] Exit

1 – Search for an exact word and get document references
2 – Get autocomplete suggestions based on prefix
3 – Exit

```

### Output Details

#### Exact Word Search

```bash
Printed in the console:

Found 3 matches for 'धर्म':
 - Document: file1.pdf, Position: 45
 - Document: file2.pdf, Position: 11
 - Document: file3.pdf, Position: 99
Autocomplete Results
Printed compactly in the terminal and saved to output.json:
```
#### output.json

```json
[
  {
    "prefix": "ध",
    "word": "धर्म",
    "is_end_of_word": true,
    "references": [
      {
        "doc_id": "file1.pdf",
        "position": 45
      }
    ]
  },
  ...
]
```
#### requirements.txt

```
pdfplumber
pytesseract
pdf2image
Pillow
```