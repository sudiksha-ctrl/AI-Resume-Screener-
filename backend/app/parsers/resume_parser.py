import io
import re
from typing import Dict, Any, Optional

def clean_text(text: str) -> str:
    """Normalize whitespace and remove unprintable characters."""
    if not text:
        return ""
    # Normalize unicode spaces and quotes
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    text = re.sub(r'[\r\t]', ' ', text)
    # Remove multiple spaces while preserving single newlines
    lines = [re.sub(r'[ ]{2,}', ' ', line).strip() for line in text.split('\n')]
    # Collapse 3+ empty lines to 2
    cleaned_lines = []
    empty_count = 0
    for line in lines:
        if not line:
            empty_count += 1
            if empty_count <= 2:
                cleaned_lines.append("")
        else:
            empty_count = 0
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF (fitz) with fallback."""
    text_content = []
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text_content.append(page.get_text("text"))
        doc.close()
        return "\n".join(text_content)
    except Exception as e:
        # Fallback to pdfplumber or pypdf or raw decode if available
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
            return "\n".join(text_content)
        except Exception:
            # Fallback to ASCII string extraction
            decoded = file_bytes.decode("latin-1", errors="ignore")
            # Extract printable ascii runs
            printable = re.findall(r'[a-zA-Z0-9\s.,!?:;@_/\-+=#*()\[\]{}"\']{4,}', decoded)
            return "\n".join(printable)


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also check tables
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    paragraphs.append(" | ".join(row_text))
        return "\n".join(paragraphs)
    except Exception as e:
        # Fallback raw text decoding
        return file_bytes.decode("utf-8", errors="ignore")


def parse_txt(file_bytes: bytes) -> str:
    """Extract text from plain text file."""
    for enc in ["utf-8", "latin-1", "windows-1252"]:
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def parse_resume_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Parse resume file by extension and extract sections."""
    lower_name = filename.lower()
    raw_text = ""
    
    if lower_name.endswith(".pdf"):
        raw_text = parse_pdf(file_bytes)
    elif lower_name.endswith(".docx") or lower_name.endswith(".doc"):
        raw_text = parse_docx(file_bytes)
    else:
        raw_text = parse_txt(file_bytes)
        
    cleaned = clean_text(raw_text)
    sections = extract_sections(cleaned)
    
    return {
        "filename": filename,
        "raw_text": cleaned,
        "sections": sections,
        "word_count": len(cleaned.split())
    }


SECTION_HEADERS = {
    "experience": [
        r"(?:work\s+)?experience",
        r"employment\s+history",
        r"work\s+history",
        r"professional\s+experience",
        r"career\s+history",
        r"internships?"
    ],
    "education": [
        r"education",
        r"academic\s+background",
        r"academic\s+history",
        r"qualifications",
        r"academic\s+qualifications"
    ],
    "skills": [
        r"technical\s+skills",
        r"skills\s*(?:&|and)?\s*(?:abilities|competencies|technologies)?",
        r"core\s+competencies",
        r"technologies",
        r"tools\s*(?:&|and)?\s*technologies"
    ],
    "projects": [
        r"projects",
        r"personal\s+projects",
        r"academic\s+projects",
        r"key\s+projects",
        r"portfolio"
    ],
    "certifications": [
        r"certifications?",
        r"licenses?\s*(?:&|and)?\s*certifications?",
        r"courses?\s*(?:&|and)?\s*certifications?",
        r"accreditations?"
    ]
}


def extract_sections(text: str) -> Dict[str, str]:
    """Segment resume text into standard sections."""
    lines = text.split("\n")
    sections: Dict[str, list] = {
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "other": []
    }
    
    # Pre-compile header patterns
    header_regexes = {}
    for sec, patterns in SECTION_HEADERS.items():
        combined = r"^(?:[#*_\-\s]*)" + r"(?:" + "|".join(patterns) + r")" + r"[:\s*_\-]*$"
        header_regexes[sec] = re.compile(combined, re.IGNORECASE)

    current_section = "summary"
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        matched_section = None
        # Check if line looks like a header (short line, matches section names)
        if len(stripped) < 45:
            for sec, reg in header_regexes.items():
                if reg.match(stripped):
                    matched_section = sec
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}
