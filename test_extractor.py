from src.parser import PDFParser
from src.chunker import DocumentChunker
from src.extractor import AIExtractor

print("Initializing...")

parser = PDFParser()
chunker = DocumentChunker()
extractor = AIExtractor()

print("Parsing PDF...")

pages = parser.parse_pdf("uploads/Sample Report.pdf")

print(f"Pages: {len(pages)}")

chunks = chunker.chunk_document(pages)

print(f"Chunks: {len(chunks)}")

print("Sending first chunk to Gemini...")

result = extractor.extract_inspection_chunk(chunks[0])

print("\n===== GEMINI OUTPUT =====\n")
print(result)