from bs4 import BeautifulSoup
import re

def html_to_text(html: str) -> str:
    """
    Convert HTML to clean, meaningful text.
    Aggressive cleaning to extract ONLY business content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # STEP 1: Remove noise elements completely
    noise_tags = [
        'script', 'style', 'nav', 'footer', 'header',
        'aside', 'iframe', 'noscript', 'meta', 'link',
        'button', 'form', 'input', 'select', 'textarea'
    ]
    for tag in noise_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # STEP 2: Remove common cookie/GDPR banners by class/id
    banner_patterns = [
        'cookie', 'gdpr', 'privacy', 'consent', 
        'banner', 'popup', 'modal', 'overlay'
    ]
    for pattern in banner_patterns:
        for element in soup.find_all(class_=re.compile(pattern, re.I)):
            element.decompose()
        for element in soup.find_all(id=re.compile(pattern, re.I)):
            element.decompose()
    
    # STEP 3: Extract meaningful content from specific tags
    meaningful_content = []
    
    # Priority 1: Main content areas
    for tag in ['main', 'article', 'section']:
        for element in soup.find_all(tag):
            text = element.get_text(separator=' ', strip=True)
            if text:
                meaningful_content.append(text)
    
    # Priority 2: Headings and paragraphs if no main content found
    if not meaningful_content:
        for tag in ['h1', 'h2', 'h3', 'p']:
            for element in soup.find_all(tag):
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 20:  # Skip trivial text
                    meaningful_content.append(text)
    
    # Priority 3: Fallback to body if still empty
    if not meaningful_content:
        body = soup.find('body')
        if body:
            meaningful_content.append(body.get_text(separator=' ', strip=True))
    
    # STEP 4: Combine and clean
    text = ' '.join(meaningful_content)
    text = clean_text(text)
    
    return text

def clean_text(text: str) -> str:
    """
    Aggressively clean and normalize text content.
    """
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters (keep alphanumeric, basic punctuation)
    text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', ' ', text)
    
    # Remove repeated punctuation
    text = re.sub(r'([.,!?;:]){2,}', r'\1', text)
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text

def extract_keywords(text: str, context: str = "business") -> list:
    """
    Extract important sentences and keywords related to specific context.
    Context can be: business, products, industries, regions, jobs, news
    """
    # Simple keyword extraction based on context
    keywords_map = {
        "business": ["company", "business", "enterprise", "organization", "firm"],
        "products": ["product", "service", "solution", "offering", "platform"],
        "industries": ["industry", "sector", "market", "vertical"],
        "regions": ["region", "country", "global", "location", "area"],
        "jobs": ["hiring", "role", "position", "job", "career", "skill"],
        "news": ["announced", "launched", "released", "partnership", "acquisition"]
    }
    
    keywords = keywords_map.get(context, [])
    
    # Split into sentences
    sentences = text.split('.')
    
    # Find sentences containing keywords
    relevant_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in keywords):
            relevant_sentences.append(sentence.strip())
    
    return relevant_sentences[:10]  # Return top 10 relevant sentences
