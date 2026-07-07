import streamlit as st
from pathlib import Path

from src.parser import PDFParser
from src.chunker import DocumentChunker
from src.extractor import AIExtractor
from src.merger import ObservationMerger
from src.validator import DDRValidator
from src.ddr_generator import DDRGenerator


# --------------------------------------------------
# Helper
# --------------------------------------------------
def save_uploaded_file(uploaded_file, folder="uploads"):
    folder = Path(folder)
    folder.mkdir(exist_ok=True)

    file_path = folder / uploaded_file.name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def format_pages(page_numbers):
    if not page_numbers:
        return "Not Available"

    if len(page_numbers) == 1:
        return f"Page {page_numbers[0]}"

    pages = ", ".join(str(page) for page in page_numbers)
    return f"Pages {pages}"


def backfill_observation_pages(result, chunk_pages, observation_key):
    if not isinstance(result, dict):
        return result

    fallback_page = format_pages(chunk_pages)
    observations = result.get(observation_key, [])

    for observation in observations:
        if observation.get("page") in [None, "", "Not Available"]:
            observation["page"] = fallback_page

    return result


# --------------------------------------------------
# Streamlit Config
# --------------------------------------------------
st.set_page_config(
    page_title="UrbanRoof AI DDR Generator",
    page_icon="🏠",
    layout="wide",
)

# --------------------------------------------------
# Create Required Folders
# --------------------------------------------------
for folder in [
    "uploads",
    "outputs",
    "logs",
    "extracted_images",
]:
    Path(folder).mkdir(exist_ok=True)

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🏠 UrbanRoof AI DDR Generator")

st.markdown("""
Generate a **Detailed Diagnostic Report (DDR)** from:

- Inspection Report
- Thermal Report
""")

st.divider()

# --------------------------------------------------
# Upload Section
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    inspection_pdf = st.file_uploader(
        "📄 Inspection Report",
        type="pdf"
    )

with col2:
    thermal_pdf = st.file_uploader(
        "🌡 Thermal Report",
        type="pdf"
    )

st.divider()

generate = st.button(
    "🚀 Generate DDR",
    use_container_width=True
)

# ==================================================
# MAIN PIPELINE
# ==================================================
if generate:

    # -----------------------------
    # Validate Uploads
    # -----------------------------
    if inspection_pdf is None or thermal_pdf is None:
        st.error("Please upload both PDF reports.")
        st.stop()

    # -----------------------------
    # Save Files
    # -----------------------------
    inspection_path = save_uploaded_file(inspection_pdf)
    thermal_path = save_uploaded_file(thermal_pdf)

    st.success("✅ Files Uploaded")

    # -----------------------------
    # Parse PDFs
    # -----------------------------
    with st.spinner("Parsing PDFs..."):

        parser = PDFParser()

        inspection_pages = parser.parse_pdf(
            inspection_path
        )

        thermal_pages = parser.parse_pdf(
            thermal_path
        )

    st.success("✅ Parsing Complete")

    st.write(f"Inspection Pages : {len(inspection_pages)}")
    st.write(f"Thermal Pages : {len(thermal_pages)}")

    # -----------------------------
    # Chunk Documents
    # -----------------------------
    with st.spinner("Chunking Documents..."):

        chunker = DocumentChunker()

        inspection_chunks = chunker.chunk_document(
            inspection_pages
        )

        thermal_chunks = chunker.chunk_document(
            thermal_pages
        )

    st.success("✅ Chunking Complete")

    st.write(f"Inspection Chunks : {len(inspection_chunks)}")
    st.write(f"Thermal Chunks : {len(thermal_chunks)}")

    with st.expander("Inspection Chunk Preview"):
        st.write(inspection_chunks[0]["pages"])
        st.write(inspection_chunks[0]["text"][:1000])

    with st.expander("Thermal Chunk Preview"):
        st.write(thermal_chunks[0]["pages"])
        st.write(thermal_chunks[0]["text"][:1000])

    # -----------------------------
    # AI Extraction
    # -----------------------------
    extractor = AIExtractor()

    inspection_json = {
        "property": {},
        "observations": []
    }

    thermal_json = {
        "thermal_observations": []
    }

    with st.spinner("Extracting Inspection Report..."):

        for chunk in inspection_chunks:

            result = extractor.extract_inspection_chunk(chunk)

            if result is None:
                st.error("Inspection extraction failed.")
                st.stop()

            result = backfill_observation_pages(
                result,
                chunk.get("pages", []),
                "observations"
            )

            if result.get("property"):
                inspection_json["property"] = result["property"]

            inspection_json["observations"].extend(
                result.get("observations", [])
            )

    with st.spinner("Extracting Thermal Report..."):

        for chunk in thermal_chunks:

            result = extractor.extract_thermal_chunk(chunk)

            if result is None:
                st.error("Thermal extraction failed.")
                st.stop()

            result = backfill_observation_pages(
                result,
                chunk.get("pages", []),
                "thermal_observations"
            )

            thermal_json["thermal_observations"].extend(
                result.get("thermal_observations", [])
            )

    st.success("✅ AI Extraction Complete")

    with st.expander("Inspection JSON"):
        st.json(inspection_json)

    with st.expander("Thermal JSON"):
        st.json(thermal_json)

    # -----------------------------
    # Merge
    # -----------------------------
    merger = ObservationMerger()

    merged = merger.merge(
        inspection_json,
        thermal_json,
        inspection_pages,
        thermal_pages
    )

    st.success("✅ Merge Complete")

    with st.expander("Merged JSON"):
        st.json(merged)

    # -----------------------------
    # Validation
    # -----------------------------
    validator = DDRValidator()
    st.write("Merged object:")
    st.write(merged)

    validated = validator.validate(
        merged,
        property_info=inspection_json.get("property", {})
    )

    st.success("✅ Validation Complete")

    with st.expander("Validated JSON"):
        st.json(validated)

    # -----------------------------
    # DDR Generation
    # -----------------------------
    ddr_generator = DDRGenerator()

    with st.spinner("Generating DDR..."):

        ddr = ddr_generator.generate(validated)
        from src.word_report import WordReportGenerator
        word = WordReportGenerator()
        output = word.generate(
            ddr,
            "outputs/final_ddr.docx"
        )
        with open(output, "rb") as f:
            st.download_button(
                "📄 Download DDR",
                f,
                file_name="UrbanRoof_DDR.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            st.success("✅ DDR Generated")
            st.subheader("Generated DDR")
            st.json(ddr)

    # -----------------------------
    # Debug Images
    # -----------------------------
    with st.expander("Extracted Images"):

        if inspection_chunks:
            st.write(inspection_chunks[0]["images"])

        if thermal_chunks:
            st.write(thermal_chunks[0]["images"])
            