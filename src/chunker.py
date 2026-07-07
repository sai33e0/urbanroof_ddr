class DocumentChunker:

    def __init__(self, max_chars=6000):
        self.max_chars = max_chars

    def chunk_document(self, parsed_pages):

        chunks = []

        current_chunk = {
            "pages": [],
            "text": "",
            "images": []
        }

        current_length = 0

        for page in parsed_pages:

            page_text = page["text"]
            page_images = page["images"]

            if current_length + len(page_text) > self.max_chars:

                chunks.append(current_chunk)

                current_chunk = {
                    "pages": [],
                    "text": "",
                    "images": []
                }

                current_length = 0

            current_chunk["pages"].append(page["page"])
            current_chunk["text"] += "\n\n" + page_text
            current_chunk["images"].extend(page_images)

            current_length += len(page_text)

        if current_chunk["pages"]:
            chunks.append(current_chunk)

        return chunks