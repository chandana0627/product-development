from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
import os


def save_to_pdf(text, project_folder, filename="Formatted_Design_Document.pdf"):
    """
    Converts structured text into a readable PDF format.
    - Uses bold headers, spacing, and monospace for code sections.
    
    Args:
        text (str): The text content to convert to PDF
        project_folder (str): The project folder path where to save the PDF
        filename (str): Name of the PDF file (default: Formatted_Design_Document.pdf)
    """
    # Create docs folder inside project folder
    docs_folder = os.path.join(project_folder, "docs")
    os.makedirs(docs_folder, exist_ok=True)
    
    # Full path for the PDF file
    pdf_path = os.path.join(docs_folder, filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []
    lines = text.split("\n")

    for line in lines:
        if line.startswith("# "):  # Main Title
            elements.append(Paragraph(f"<b><font size=18>{line[2:]}</font></b>", styles["Title"]))
            elements.append(Spacer(1, 12))

        elif line.startswith("## "):  # Section Headers
            elements.append(Paragraph(f"<b><font size=14>{line[3:]}</font></b>", styles["Heading2"]))
            elements.append(Spacer(1, 10))

        elif line.startswith("### "):  # Subsection Headers
            elements.append(Paragraph(f"<b><font size=12>{line[4:]}</font></b>", styles["Heading3"]))
            elements.append(Spacer(1, 8))

        elif line.startswith("- "):  # Bullet Points
            elements.append(Paragraph(f"• {line[2:]}", styles["Normal"]))
            elements.append(Spacer(1, 5))

        elif line.startswith("```"):  # Code Blocks (Monospace Font)
            continue  # Skip Markdown-style ``` delimiters

        elif "@startuml" in line or "+---" in line:  # PlantUML & ASCII Diagrams
            elements.append(Preformatted(line, styles["Code"]))
            elements.append(Spacer(1, 8))

        else:
            elements.append(Paragraph(line, styles["Normal"]))

    doc.build(elements)
    print(f"\n✅ PDF saved as: {pdf_path}")
    return pdf_path
