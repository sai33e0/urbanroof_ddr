from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE


def create_styles(document):

    styles = document.styles

    # -----------------------
    # Title
    # -----------------------
    if "DDRTitle" not in styles:

        title = styles.add_style(
            "DDRTitle",
            WD_STYLE_TYPE.PARAGRAPH
        )

        title.font.name = "Calibri"
        title.font.size = Pt(22)
        title.font.bold = True

    # -----------------------
    # Heading
    # -----------------------
    if "DDRHeading" not in styles:

        heading = styles.add_style(
            "DDRHeading",
            WD_STYLE_TYPE.PARAGRAPH
        )

        heading.font.name = "Calibri"
        heading.font.size = Pt(16)
        heading.font.bold = True

    # -----------------------
    # Body
    # -----------------------
    if "DDRBody" not in styles:

        body = styles.add_style(
            "DDRBody",
            WD_STYLE_TYPE.PARAGRAPH
        )

        body.font.name = "Calibri"
        body.font.size = Pt(11)