import fitz  # PyMuPDF
from pathlib import Path
import uuid


class PDFParser:
    def __init__(self, output_dir="extracted_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def parse_pdf(self, pdf_path: str):

        document = fitz.open(pdf_path)

        parsed_pages = []

        for page_number, page in enumerate(document, start=1):

            # -----------------------
            # Extract Text
            # -----------------------
            text = page.get_text("text")

            # -----------------------
            # Extract Images
            # -----------------------
            page_images = []

            image_list = page.get_images(full=True)

            for image_index, image in enumerate(image_list):

                xref = image[0]

                base_image = document.extract_image(xref)

                image_bytes = base_image["image"]

                image_ext = base_image["ext"]

                image_name = f"{uuid.uuid4()}.{image_ext}"

                image_path = self.output_dir / image_name

                with open(image_path, "wb") as img:
                    img.write(image_bytes)

                page_images.append(str(image_path))

            parsed_pages.append(
                {
                    "page": page_number,
                    "text": text,
                    "images": page_images,
                }
            )

        document.close()

        return parsed_pages