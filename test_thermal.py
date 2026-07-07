from src.parser import PDFParser
from src.chunker import DocumentChunker
from src.extractor import AIExtractor

parser = PDFParser()
chunker = DocumentChunker()
extractor = AIExtractor()

pages = parser.parse_pdf("uploads/Thermal Images.pdf")

chunks = chunker.chunk_document(pages)

result = extractor.extract_thermal_chunk(chunks[0])

print(result)