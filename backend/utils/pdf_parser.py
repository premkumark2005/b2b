from PyPDF2 import PdfReader
from utils.html_parser import clean_text

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF file using PyPDF2.
    Returns cleaned text content.
    """
    try:
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Clean the extracted text
        text = clean_text(text)
        
        return text
    except Exception as e:
        raise Exception(f"PDF parsing failed: {str(e)}")

def extract_product_content(text: str) -> str:
    """
    Extract product-related content from text.
    Focus on product descriptions, features, specifications.
    """
    # Look for product-related keywords and sentences
    product_keywords = [
        "product", "feature", "specification", "benefits", 
        "capabilities", "solution", "technology", "offering"
    ]
    
    lines = text.split('\n')
    product_lines = []
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in product_keywords):
            product_lines.append(line.strip())
    
    return '\n'.join(product_lines) if product_lines else text
