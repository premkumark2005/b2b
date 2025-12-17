import ollama
from config import OLLAMA_MODEL
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_extraction_prompt(combined_context: str) -> str:
    """
    Create STRICT prompt for tinyllama to return ONLY valid JSON.
    No explanations, no markdown, no extra text.
    """
    # Limit context to ~2000 chars (TinyLlama optimal input)
    max_context_length = 2000
    if len(combined_context) > max_context_length:
        logger.info(f"⚠️  TRUNCATING context from {len(combined_context)} to {max_context_length} chars")
        combined_context = combined_context[:max_context_length] + "\n...[content truncated]"
    
    prompt = f"""You are a data extraction system. Extract structured information and output ONLY valid JSON.

INPUT DATA:
{combined_context}

OUTPUT FORMAT (copy this structure exactly):
{{
  "business_summary": "brief description of company",
  "product_lines": ["product A", "product B"],
  "target_industries": ["industry X", "industry Y"],
  "regions": ["North America", "Europe"],
  "hiring_focus": ["engineer", "analyst"],
  "key_recent_events": ["event 1", "event 2"]
}}

RULES:
1. Return ONLY the JSON object
2. NO explanations
3. NO markdown (no ```)
4. NO extra text

JSON:"""
    return prompt

def extract_with_tinyllama(combined_context: str) -> dict:
    """
    Send combined context to tinyllama using Ollama.
    Extract structured data in JSON format with defensive parsing.
    
    Args:
        combined_context: Combined text from all ChromaDB collections
    
    Returns:
        dict: Extracted fields in structured format
    """
    try:
        # Create prompt
        prompt = create_extraction_prompt(combined_context)
        
        logger.info("Calling Ollama/Llama3.2 for data extraction...")
        
        # Call Ollama with llama3.2 - better at following JSON instructions than tinyllama
        response = ollama.chat(
            model='llama3.2',  # Using llama3.2 (3B params) instead of tinyllama
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2,  # Low temperature for more deterministic output
                "num_predict": 500   # Limit response length
            }
        )
        
        # Extract response content
        response_text = response['message']['content']
        
        # DEBUG: Log raw LLM output
        print("\n" + "="*80)
        print("RAW LLM OUTPUT:")
        print("="*80)
        print(response_text[:800])  # First 800 chars
        if len(response_text) > 800:
            print("...")
        print("="*80)
        print(f"Total LLM output length: {len(response_text)} characters")
        print("="*80 + "\n")
        
        logger.info(f"Raw LLM response: {response_text[:300]}...")
        
        # DEFENSIVE PARSING: Extract JSON from potentially messy LLM output
        extracted_data = parse_llm_json_response(response_text)
        
        # Validate and normalize the extracted data
        extracted_data = validate_and_normalize(extracted_data)
        
        logger.info("Successfully extracted structured data from LLM")
        return extracted_data
        
    except Exception as e:
        logger.error(f"Tinyllama extraction failed: {str(e)}")
        # Return safe fallback structure
        return get_fallback_structure()

def parse_llm_json_response(response_text: str) -> dict:
    """
    Robust JSON extraction using stack-based parsing.
    Handles markdown, extra text, and nested JSON.
    
    Args:
        response_text: Raw text from LLM
        
    Returns:
        dict: Parsed JSON or fallback structure
    """
    try:
        # Step 1: Remove markdown code blocks
        cleaned = response_text.strip()
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        # Step 2: Try direct parsing
        try:
            return json.loads(cleaned)
        except:
            pass
        
        # Step 3: Stack-based JSON extraction (handles nesting)
        stack = []
        start_idx = None
        
        for i, char in enumerate(cleaned):
            if char == '{':
                if not stack:  # First opening brace
                    start_idx = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:  # Matching closing brace found
                        json_str = cleaned[start_idx:i+1]
                        
                        # Clean and try to parse
                        json_str = re.sub(r'//.*?\n', '\n', json_str)  # Remove comments
                        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
                        
                        try:
                            parsed = json.loads(json_str)
                            logger.info("Successfully extracted JSON from LLM response")
                            return parsed
                        except:
                            continue  # Try next JSON object
        
        # Step 4: Fallback
        logger.warning("JSON extraction failed, using fallback structure")
        return get_fallback_structure()
        
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return get_fallback_structure()

def validate_and_normalize(data: dict) -> dict:
    """
    Ensure all required fields exist with correct types.
    Convert any non-list fields to lists where needed.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        dict: Validated and normalized data
    """
    schema = {
        "business_summary": str,
        "product_lines": list,
        "target_industries": list,
        "regions": list,
        "hiring_focus": list,
        "key_recent_events": list
    }
    
    validated = {}
    
    for key, expected_type in schema.items():
        if key in data:
            value = data[key]
            
            # Normalize to expected type
            if expected_type == list:
                if isinstance(value, list):
                    # Filter out empty strings and ensure all items are strings
                    validated[key] = [str(item).strip() for item in value if item]
                elif isinstance(value, str):
                    # Convert string to list (split by comma or newline)
                    if value.strip():
                        validated[key] = [item.strip() for item in re.split(r'[,\n]', value) if item.strip()]
                    else:
                        validated[key] = []
                else:
                    validated[key] = []
            elif expected_type == str:
                validated[key] = str(value).strip() if value else ""
        else:
            # Field missing, use default
            if expected_type == list:
                validated[key] = []
            else:
                validated[key] = ""
    
    return validated

def get_fallback_structure() -> dict:
    """
    Return a safe fallback structure when LLM extraction fails.
    
    Returns:
        dict: Default structure with empty values
    """
    return {
        "business_summary": "Data extraction failed. Please try uploading data again.",
        "product_lines": [],
        "target_industries": [],
        "regions": [],
        "hiring_focus": [],
        "key_recent_events": []
    }
