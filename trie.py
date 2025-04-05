import os
import re
import json
import pdfplumber
import pytesseract
import warnings
from PIL import Image
from pdf2image import convert_from_path
import unicodedata
from collections import defaultdict
import logging

logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.references = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, doc_id, position):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.references.append((doc_id, position))

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.references if node.is_end_of_word else []

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_words(node, prefix)

    def _collect_words(self, node, prefix):
        results = []
        if node.is_end_of_word:
            results.append((prefix, node))
        for char, child in node.children.items():
            results.extend(self._collect_words(child, prefix + char))
        return results

class SanskritSearchEngine:
    def __init__(self):
        self.trie = Trie()
        self.documents = {}

    def load_text_from_pdf(self, file_path):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            text = self.ocr_extract_text(file_path)
        return text

    def ocr_extract_text(self, file_path):
        images = convert_from_path(file_path)
        return "\n".join(pytesseract.image_to_string(img, lang='san') for img in images)

    def preprocess_text(self, text):
        text = unicodedata.normalize('NFC', text)
        text = text.lower()
        text = re.sub(r'[^\u0900-\u097F\s]', '', text)
        return text.split()

    def index_document(self, doc_id, text):
        words = self.preprocess_text(text)
        print(f"Indexing document: {doc_id} - Extracted {len(words)} words")
        for position, word in enumerate(words):
            self.trie.insert(word, doc_id, position)
        self.documents[doc_id] = text

    def index_documents_in_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(folder_path, filename)
                text = self.load_text_from_pdf(file_path)
                self.index_document(filename, text)

    def search_word(self, query):
        return self.trie.search(query)

    def autocomplete(self, prefix):
        return self.trie.starts_with(prefix)

def format_node_output(word, node, compact=False):
    if compact:
        return {
            "word": word,
            "ref_count": len(node.references),
            "doc_ids": list({doc_id for doc_id, _ in node.references})
        }
    else:
        return {
            "prefix": word,
            "children": list(node.children.keys()),
            "is_end_of_word": node.is_end_of_word,
            "references": [{"doc_id": doc, "position": pos} for doc, pos in node.references]
        }

if __name__ == "__main__":
    search_engine = SanskritSearchEngine()
    search_engine.index_documents_in_folder("./docs")

    print("\n📚 Sanskrit Search Engine Ready")
    print("Select an action:")
    print("  [1] Search a word")
    print("  [2] Autocomplete a prefix")
    print("  [3] Exit")

    while True:
        try:
            action = int(input("Enter choice [1/2/3]: ").strip())
        except ValueError:
            print("❌ Invalid input. Enter 1, 2 or 3.\n")
            continue

        if action == 3:
            print("👋 Goodbye!")
            break
        elif action in (1, 2):
            query = input("Enter Devanagari word or prefix: ").strip()
            if not query:
                print("⚠️ Empty input. Try again.\n")
                continue

            if action == 1:
                results = search_engine.search_word(query)
                print(f"\n🔎 Found {len(results)} matches for '{query}':")
                for doc_id, pos in results:
                    print(f" - Document: {doc_id}, Position: {pos}")
                print()
            elif action == 2:
                suggestions = search_engine.autocomplete(query)
                if not suggestions:
                    print(f"❌ No suggestions found for prefix '{query}'.\n")
                    continue

                print(f"\n✨ Autocomplete suggestions for '{query}':")
                full_output = []
                for word, node in suggestions:
                    compact_result = format_node_output(word, node, compact=True)
                    print(json.dumps(compact_result, ensure_ascii=False))
                    full_output.append(format_node_output(word, node, compact=False))

                with open("autocomplete_full_output.json", "w", encoding="utf-8") as f:
                    json.dump(full_output, f, ensure_ascii=False, indent=2)
                print("📁 Full output written to 'autocomplete_full_output.json'\n")
        else:
            print("❌ Invalid action. Try again.\n")
