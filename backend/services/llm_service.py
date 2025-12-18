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
    Create STRICT prompt that enforces CONTEXT-ONLY extraction.
    LLM must NOT use prior knowledge or hallucinate values.
    """
    # Limit context to ~2000 chars (optimal for llama3.2)
    max_context_length = 2000
    if len(combined_context) > max_context_length:
        logger.info(f"⚠️  TRUNCATING context from {len(combined_context)} to {max_context_length} chars")
        combined_context = combined_context[:max_context_length] + "\n...[content truncated]"
    
    prompt = f"""You are a STRICT INFORMATION EXTRACTOR. Your job is to extract facts ONLY from the provided context.

⚠️ CRITICAL RULES:
1. Use ONLY the provided context below as your source of truth
2. Do NOT use your prior knowledge or training data
3. Do NOT infer, guess, or assume any information
4. Do NOT use placeholder values like "Product A", "Industry X", etc.
5. If information is NOT explicitly present in the context, leave that field EMPTY ([] or "")
6. Every value you extract must appear verbatim (or near-verbatim) in the context text
7. Extract ONLY what is clearly stated - no interpretations

CONTEXT (your ONLY source of information):
{combined_context}

EXTRACT the following information from the context above:
- business_summary: Brief description of what the company does (1-2 sentences from context)
- product_lines: Specific product or service names mentioned (exact names from context)
- target_industries: Industries explicitly mentioned as targets/markets (from context only)
- regions: Geographic regions/countries mentioned for operations/markets (from context only)
- hiring_focus: Job roles/positions mentioned in hiring/job postings (from context only)
- key_recent_events: Recent events, announcements, or news (from context only)

OUTPUT FORMAT (return ONLY this JSON, no markdown, no explanations):
{{
  "business_summary": "extract from context or leave empty",
  "product_lines": ["exact name from context"],
  "target_industries": ["exact industry from context"],
  "regions": ["exact region from context"],
  "hiring_focus": ["exact role from context"],
  "key_recent_events": ["exact event from context"]
}}

REMEMBER: If you cannot find explicit information in the context above, return [] or "" for that field.
Do NOT make up, infer, or use external knowledge.

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
        
        # CRITICAL: Remove hallucinated values not found in context
        extracted_data = filter_hallucinations(extracted_data, combined_context)
        
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

def filter_hallucinations(extracted_data: dict, context: str) -> dict:
    """
    CRITICAL POST-PROCESSING: Remove any extracted values that don't appear in the context.
    This prevents hallucinated outputs from reaching the UI.
    
    Args:
        extracted_data: Data extracted by LLM
        context: Original context text
        
    Returns:
        dict: Filtered data with only verified values
    """
    # Convert context to lowercase for case-insensitive matching
    context_lower = context.lower()
    
    # Define placeholder patterns that indicate hallucination
    placeholder_patterns = [
        r'product\s*[a-z]\b',  # "Product A", "Product B", etc.
        r'industry\s*[a-z]\b',  # "Industry X", "Industry Y", etc.
        r'region\s*[a-z]\b',    # "Region A", etc.
        r'example',             # "Example", "example product"
        r'placeholder',         # "Placeholder"
        r'^[a-z]$',            # Single letters: "A", "B", "X", "Y"
    ]
    
    filtered = extracted_data.copy()
    
    # Filter list fields (product_lines, target_industries, etc.)
    for field in ['product_lines', 'target_industries', 'regions', 'hiring_focus', 'key_recent_events']:
        if field in filtered and isinstance(filtered[field], list):
            verified_items = []
            
            for item in filtered[field]:
                item_str = str(item).strip()
                
                # Skip empty items
                if not item_str:
                    continue
                
                # Check if item matches placeholder pattern
                is_placeholder = any(re.search(pattern, item_str.lower()) for pattern in placeholder_patterns)
                if is_placeholder:
                    logger.warning(f"❌ REMOVED PLACEHOLDER: {field} = '{item_str}'")
                    continue
                
                # Check if item appears in context (case-insensitive substring match)
                # For multi-word items, check if at least 50% of words appear
                words = item_str.lower().split()
                if len(words) == 1:
                    # Single word: must appear in context
                    if words[0] in context_lower:
                        verified_items.append(item_str)
                    else:
                        logger.warning(f"❌ REMOVED HALLUCINATION: {field} = '{item_str}' (not found in context)")
                else:
                    # Multi-word: at least 50% of words must appear
                    matching_words = sum(1 for word in words if word in context_lower)
                    if matching_words >= len(words) * 0.5:
                        verified_items.append(item_str)
                    else:
                        logger.warning(f"❌ REMOVED HALLUCINATION: {field} = '{item_str}' (insufficient match: {matching_words}/{len(words)} words)")
            
            filtered[field] = verified_items
    
    # Filter business_summary (check if it's too generic or contains placeholders)
    if 'business_summary' in filtered:
        summary = filtered['business_summary']
        is_placeholder = any(re.search(pattern, summary.lower()) for pattern in placeholder_patterns)
        
        if is_placeholder or len(summary) < 20:
            logger.warning(f"❌ REMOVED GENERIC SUMMARY: '{summary}'")
            filtered['business_summary'] = ""
    
    # Log filtering results
    removed_count = sum(
        len(extracted_data.get(field, [])) - len(filtered.get(field, []))
        for field in ['product_lines', 'target_industries', 'regions', 'hiring_focus', 'key_recent_events']
    )
    
    if removed_count > 0:
        logger.info(f"✅ HALLUCINATION FILTER: Removed {removed_count} hallucinated/placeholder values")
    else:
        logger.info("✅ HALLUCINATION FILTER: All extracted values verified")
    
    return filtered

def extract_business_overview(context: str) -> dict:
    """
    Extract business overview fields: business_summary, product_lines, 
    target_industries, regions.
    
    Args:
        context: Website and product content
        
    Returns:
        dict: Extracted overview fields
    """
    # Limit context
    max_length = 2000
    if len(context) > max_length:
        context = context[:max_length] + "\n...[truncated]"
    
    prompt = f"""Extract business information from the context below.

⚠️ RULES:
- Use ONLY the provided context
- Do NOT use prior knowledge
- If information is missing, return [] or ""

CONTEXT:
{context}

Extract:
- business_summary: Brief description (1-2 sentences from context)
- product_lines: Specific product/service names mentioned
- target_industries: Industries mentioned as targets/markets
- regions: Geographic regions/countries mentioned

Return ONLY this JSON:
{{
  "business_summary": "...",
  "product_lines": [...],
  "target_industries": [...],
  "regions": [...]
}}

JSON:"""
    
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2, "num_predict": 400}
        )
        
        response_text = response['message']['content']
        extracted = parse_llm_json_response(response_text)
        
        # Validate against context
        validated = {
            "business_summary": str(extracted.get("business_summary", "")).strip(),
            "product_lines": filter_against_context(extracted.get("product_lines", []), context),
            "target_industries": filter_against_context(extracted.get("target_industries", []), context),
            "regions": filter_against_context(extracted.get("regions", []), context)
        }
        
        return validated
        
    except Exception as e:
        logger.error(f"Business overview extraction failed: {e}")
        return {"business_summary": "", "product_lines": [], "target_industries": [], "regions": []}

def extract_hiring_focus(context: str) -> list:
    """
    Extract hiring_focus from job postings ONLY.
    
    Args:
        context: Job posting content
        
    Returns:
        list: Job roles/positions mentioned
    """
    if not context or len(context.strip()) < 20:
        return []
    
    # Limit context
    max_length = 1500
    if len(context) > max_length:
        context = context[:max_length] + "\n...[truncated]"
    
    prompt = f"""Extract job roles and positions from the job postings below.

⚠️ RULES:
- Use ONLY the job posting text provided
- Extract specific role names (e.g., "Software Engineer", "Data Scientist")
- Do NOT infer or guess roles
- If no roles are mentioned, return []

JOB POSTINGS:
{context}

Return ONLY a JSON array of role names:
{{"hiring_focus": ["role1", "role2"]}}

JSON:"""
    
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 200}
        )
        
        response_text = response['message']['content']
        logger.info(f"Hiring extraction raw: {response_text[:200]}")
        
        extracted = parse_llm_json_response(response_text)
        
        # Handle both dict and list responses
        if isinstance(extracted, dict):
            roles = extracted.get("hiring_focus", [])
        elif isinstance(extracted, list):
            roles = extracted
        else:
            roles = []
        
        # Validate against context
        validated_roles = filter_against_context(roles, context)
        logger.info(f"✅ Extracted {len(validated_roles)} hiring roles")
        
        return validated_roles
        
    except Exception as e:
        logger.error(f"Hiring focus extraction failed: {e}")
        return []

def extract_recent_events(context: str) -> list:
    """
    Extract recent_events from news snippets ONLY.
    
    Args:
        context: News content
        
    Returns:
        list: Recent events/announcements
    """
    if not context or len(context.strip()) < 20:
        return []
    
    # Limit context
    max_length = 1500
    if len(context) > max_length:
        context = context[:max_length] + "\n...[truncated]"
    
    prompt = f"""Extract recent events and announcements from the news snippets below.

⚠️ RULES:
- Use ONLY the news text provided
- Extract specific events (e.g., "Launched new AI platform", "Acquired Company X")
- Do NOT infer or make up events
- If no events are mentioned, return []

NEWS SNIPPETS:
{context}

Return ONLY a JSON array of events:
{{"recent_events": ["event1", "event2"]}}

JSON:"""
    
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 200}
        )
        
        response_text = response['message']['content']
        logger.info(f"Events extraction raw: {response_text[:200]}")
        
        extracted = parse_llm_json_response(response_text)
        
        # Handle both dict and list responses
        if isinstance(extracted, dict):
            events = extracted.get("recent_events", [])
        elif isinstance(extracted, list):
            events = extracted
        else:
            events = []
        
        # Validate against context
        validated_events = filter_against_context(events, context)
        logger.info(f"✅ Extracted {len(validated_events)} recent events")
        
        return validated_events
        
    except Exception as e:
        logger.error(f"Recent events extraction failed: {e}")
        return []

def filter_against_context(items: list, context: str) -> list:
    """
    Remove items that don't appear in the context (hallucination filter).
    
    Args:
        items: List of extracted values
        context: Original context text
        
    Returns:
        list: Filtered items that exist in context
    """
    if not items or not context:
        return []
    
    context_lower = context.lower()
    validated = []
    
    for item in items:
        item_str = str(item).strip()
        if not item_str or len(item_str) < 2:
            continue
        
        # Check if item appears in context (case-insensitive)
        words = item_str.lower().split()
        if len(words) == 1:
            # Single word: must appear in context
            if words[0] in context_lower:
                validated.append(item_str)
        else:
            # Multi-word: at least 50% of words must appear
            matching = sum(1 for word in words if word in context_lower)
            if matching >= len(words) * 0.5:
                validated.append(item_str)
    
    return validated

def get_fallback_structure() -> dict:
    """
    Return a safe fallback structure when LLM extraction fails.
    Returns EMPTY fields, not placeholder text.
    
    Returns:
        dict: Default structure with empty values
    """
    return {
        "business_summary": "",
        "product_lines": [],
        "target_industries": [],
        "regions": [],
        "hiring_focus": [],
        "key_recent_events": []
    }
