from docx import Document

from src.styles import create_styles


class DOCXBuilder:

    def __init__(self):

        self.document = Document()

        create_styles(self.document)

    def build(self, ddr_json):

        self.add_cover_page(ddr_json)

        self.add_property_summary(ddr_json)

        self.add_area_sections(ddr_json)

        self.add_notes(ddr_json)

        return self.document

    def save(self, filename):

        self.document.save(filename)
        