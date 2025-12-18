"""
Company Description Generator
Generates short and long descriptions for companies using LLM.
"""

import ollama
from config import OLLAMA_MODEL
import logging

logger = logging.getLogger(__name__)

def generate_short_description(combined_context: str, company_name: str) -> str:
    """
    Generate a concise 1-2 sentence description of the company.
    
    Args:
        combined_context: Combined RAG context from all sources
        company_name: Name of the company
        
    Returns:
        str: Short description (1-2 sentences)
    """
    try:
        # Limit context for focused description
        max_length = 2500
        if len(combined_context) > max_length:
            combined_context = combined_context[:max_length]
        
        prompt = f"""Based ONLY on the following context, write a concise 1-2 sentence description of {company_name}.

RULES:
- Use ONLY information from the context below
- Maximum 2 sentences
- Focus on what the company does and their main offerings
- Be specific and factual
- No marketing jargon or superlatives

CONTEXT:
{combined_context}

Short Description (1-2 sentences):"""
        
        logger.info(f"Generating short description for {company_name}...")
        
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={
                'temperature': 0.3,
                'num_predict': 100
            }
        )
        
        description = response['response'].strip()
        logger.info(f"Generated short description: {description[:100]}...")
        
        return description
        
    except Exception as e:
        logger.error(f"Short description generation failed: {str(e)}")
        return f"{company_name} is a company in the technology sector."

def generate_long_description(combined_context: str, company_name: str, industry_info: dict = None) -> str:
    """
    Generate a comprehensive 2-3 paragraph description of the company.
    
    Args:
        combined_context: Combined RAG context from all sources
        company_name: Name of the company
        industry_info: Optional industry classification data
        
    Returns:
        str: Long description (2-3 paragraphs)
    """
    try:
        # Use more context for detailed description
        max_length = 4000
        if len(combined_context) > max_length:
            combined_context = combined_context[:max_length]
        
        industry_context = ""
        if industry_info:
            industry_context = f"\nIndustry Classification: {industry_info.get('sector', '')} - {industry_info.get('sub_industry', '')}"
        
        prompt = f"""Based ONLY on the following context, write a comprehensive 2-3 paragraph description of {company_name}.{industry_context}

RULES:
- Use ONLY information from the context below
- Write 2-3 detailed paragraphs
- Paragraph 1: Company overview and main business
- Paragraph 2: Products/services and target markets
- Paragraph 3: Recent developments, growth, or strategic focus
- Be specific and factual
- Use complete sentences and proper structure
- No marketing jargon or superlatives

CONTEXT:
{combined_context}

Long Description (2-3 paragraphs):"""
        
        logger.info(f"Generating long description for {company_name}...")
        
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={
                'temperature': 0.3,
                'num_predict': 400
            }
        )
        
        description = response['response'].strip()
        logger.info(f"Generated long description: {len(description)} characters")
        
        return description
        
    except Exception as e:
        logger.error(f"Long description generation failed: {str(e)}")
        sector = industry_info.get('sector', 'technology') if industry_info else 'technology'
        return f"{company_name} operates in the {sector} sector, providing solutions and services to its customers."
