from src.parser import PDFParser

parser = PDFParser()

result = parser.parse_pdf("uploads/Sample Report.pdf")

print(result[0]["page"])
print(result[0]["text"][:500])
print(result[0]["images"])