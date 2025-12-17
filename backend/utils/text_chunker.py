"""
Intelligent text chunking utility for vector database storage.
Splits text into overlapping chunks to preserve context.
"""

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks for better semantic preservation.
    
    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk (default 400 chars)
        overlap: Number of characters to overlap between chunks (default 50)
    
    Returns:
        List of text chunks
    """
    if not text or len(text) == 0:
        return []
    
    # Clean text
    text = text.strip()
    
    # If text is shorter than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = min(start + chunk_size, len(text))
        
        # If this is not the last chunk, try to break at natural boundaries
        if end < len(text):
            # Look for sentence boundaries (. ! ?)
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('! ', start, end),
                text.rfind('? ', start, end)
            )
            
            if sentence_end > start:
                end = sentence_end + 1  # Include the punctuation
            else:
                # Look for paragraph/line breaks
                line_break = text.rfind('\n', start, end)
                if line_break > start:
                    end = line_break
                else:
                    # Look for word boundaries (spaces)
                    space = text.rfind(' ', start, end)
                    if space > start:
                        end = space
        
        # Extract chunk
        chunk = text[start:end].strip()
        
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position (with overlap)
        # CRITICAL: Ensure we always move forward
        next_start = max(end - overlap, start + 1)
        
        # If we're at the end, break
        if next_start >= len(text) or end >= len(text):
            break
            
        start = next_start
    
    return chunks
