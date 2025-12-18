"""
Industry Classification Matcher
Semantically matches companies to industry classifications using embeddings.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class IndustryMatcher:
    """
    Semantic industry classification matcher.
    Matches company descriptions to industry classifications using embeddings.
    """
    
    def __init__(self, csv_path: str, embedding_model: SentenceTransformer):
        """
        Initialize the industry matcher.
        
        Args:
            csv_path: Path to industry classification CSV
            embedding_model: Pre-loaded SentenceTransformer model
        """
        self.csv_path = csv_path
        self.model = embedding_model
        self.df = None
        self.embeddings = {}
        
        # Similarity thresholds for matching (optimized based on testing)
        self.THRESHOLDS = {
            'sector': 0.30,        # Catches Financial Services at 0.323
            'sub_industry': 0.38,  # Catches Payment Solution at 0.397
            'Industry': 0.30       # Catches Financial Services at 0.323
        }
        
        self._load_and_prepare_data()
    
    def _load_and_prepare_data(self):
        """Load CSV and generate embeddings for classification fields."""
        try:
            logger.info(f"Loading industry classification data from {self.csv_path}")
            self.df = pd.read_csv(self.csv_path)
            
            # Clean data: remove NaN values
            self.df = self.df.dropna(subset=['sector', 'Industry', 'sub_industry'])
            
            logger.info(f"Loaded {len(self.df)} industry classifications")
            
            # Generate embeddings for each classification level
            logger.info("Generating embeddings for classification fields...")
            
            # Get unique values for each level
            unique_sectors = self.df['sector'].unique().tolist()
            unique_industries = self.df['Industry'].unique().tolist()
            unique_sub_industries = self.df['sub_industry'].unique().tolist()
            
            # Generate embeddings
            logger.info(f"Encoding {len(unique_sectors)} sectors...")
            sector_embeddings = self.model.encode(unique_sectors, convert_to_numpy=True)
            
            logger.info(f"Encoding {len(unique_industries)} industries...")
            industry_embeddings = self.model.encode(unique_industries, convert_to_numpy=True)
            
            logger.info(f"Encoding {len(unique_sub_industries)} sub-industries...")
            sub_industry_embeddings = self.model.encode(unique_sub_industries, convert_to_numpy=True)
            
            # Store embeddings as dictionaries for fast lookup
            self.embeddings = {
                'sector': dict(zip(unique_sectors, sector_embeddings)),
                'Industry': dict(zip(unique_industries, industry_embeddings)),
                'sub_industry': dict(zip(unique_sub_industries, sub_industry_embeddings))
            }
            
            logger.info("✅ Industry matcher initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to load industry data: {str(e)}")
            raise
    
    def match_company(self, company_text: str, company_name: str = "") -> Optional[Dict]:
        """
        Semantically match a company to an industry classification.
        
        Args:
            company_text: Combined company description text
            company_name: Company name for context
            
        Returns:
            Dict with matched classification and metadata, or None if no match
        """
        try:
            # Generate embedding for company text
            logger.info(f"Matching company: {company_name}")
            company_embedding = self.model.encode([company_text], convert_to_numpy=True)[0]
            
            # Try matching in priority order: sector → sub_industry → Industry
            
            # 1. Try matching with SECTOR first (broad categories)
            sector_match = self._find_best_match(
                company_embedding,
                self.embeddings['sector'],
                'sector',
                self.THRESHOLDS['sector']
            )
            
            if sector_match:
                logger.info(f"✅ Matched at SECTOR level: {sector_match['value']} (confidence: {sector_match['confidence']:.3f})")
                
                # Try to find best sub_industry within this sector
                sector_df = self.df[self.df['sector'] == sector_match['value']]
                sector_sub_industries = {}
                for sub_ind in sector_df['sub_industry'].unique():
                    if sub_ind in self.embeddings['sub_industry']:
                        sector_sub_industries[sub_ind] = self.embeddings['sub_industry'][sub_ind]
                
                sub_industry_match = self._find_best_match(
                    company_embedding,
                    sector_sub_industries,
                    'sub_industry',
                    self.THRESHOLDS['sub_industry']
                )
                
                if sub_industry_match:
                    logger.info(f"✅ Also matched SUB_INDUSTRY: {sub_industry_match['value']} (confidence: {sub_industry_match['confidence']:.3f})")
                    # Return the specific sub_industry row
                    matched_row = sector_df[sector_df['sub_industry'] == sub_industry_match['value']].iloc[0]
                    return self._format_result(matched_row, 'sub_industry', sub_industry_match['confidence'])
                
                # No sub_industry match, return first sector row
                matched_row = sector_df.iloc[0]
                return self._format_result(matched_row, 'sector', sector_match['confidence'])
            
            # 2. Try matching with SUB_INDUSTRY (most specific)
            sub_industry_match = self._find_best_match(
                company_embedding,
                self.embeddings['sub_industry'],
                'sub_industry',
                self.THRESHOLDS['sub_industry']
            )
            
            if sub_industry_match:
                logger.info(f"✅ Matched at SUB_INDUSTRY level: {sub_industry_match['value']} (confidence: {sub_industry_match['confidence']:.3f})")
                matched_row = self.df[self.df['sub_industry'] == sub_industry_match['value']].iloc[0]
                return self._format_result(matched_row, 'sub_industry', sub_industry_match['confidence'])
            
            # 3. Fall back to INDUSTRY (general category)
            industry_match = self._find_best_match(
                company_embedding,
                self.embeddings['Industry'],
                'Industry',
                self.THRESHOLDS['Industry']
            )
            
            if industry_match:
                logger.info(f"✅ Matched at INDUSTRY level: {industry_match['value']} (confidence: {industry_match['confidence']:.3f})")
                matched_row = self.df[self.df['Industry'] == industry_match['value']].iloc[0]
                return self._format_result(matched_row, 'Industry', industry_match['confidence'])
            
            # No match found
            logger.warning(f"⚠️ No confident match found for: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error matching company: {str(e)}")
            return None
    
    def _find_best_match(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: Dict[str, np.ndarray],
        level_name: str,
        threshold: float
    ) -> Optional[Dict]:
        """
        Find the best matching candidate using cosine similarity.
        
        Args:
            query_embedding: Company text embedding
            candidate_embeddings: Dict of {value: embedding}
            level_name: Classification level name
            threshold: Minimum similarity threshold
            
        Returns:
            Dict with matched value and confidence, or None
        """
        if not candidate_embeddings:
            return None
        
        # Calculate similarities
        candidates = list(candidate_embeddings.keys())
        embeddings_matrix = np.array([candidate_embeddings[c] for c in candidates])
        
        # Compute cosine similarity
        similarities = cosine_similarity([query_embedding], embeddings_matrix)[0]
        
        # Debug: log top 5 matches
        top_indices = np.argsort(similarities)[-5:][::-1]
        logger.info(f"🔍 Top 5 {level_name} matches:")
        for idx in top_indices:
            logger.info(f"  - {candidates[idx]}: {similarities[idx]:.3f}")
        
        # Get best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        best_candidate = candidates[best_idx]
        
        logger.debug(f"{level_name} best match: {best_candidate} (similarity: {best_similarity:.3f})")
        
        # Check if above threshold
        if best_similarity >= threshold:
            return {
                'value': best_candidate,
                'confidence': float(best_similarity)
            }
        
        return None
    
    def _format_result(self, row: pd.Series, matched_level: str, confidence: float) -> Dict:
        """
        Format the matched row into a standardized result dictionary.
        
        Args:
            row: Matched DataFrame row
            matched_level: Which level was matched (sector/Industry/sub_industry)
            confidence: Similarity score
            
        Returns:
            Dict with all classification fields
        """
        return {
            'matched_level': matched_level,
            'sector': str(row['sector']),
            'industry': str(row['Industry']),
            'sub_industry': str(row['sub_industry']),
            'sic_code': str(row['sic_code']),
            'sic_description': str(row['sic_description']),
            'confidence': confidence
        }


# Global instance (will be initialized in main.py)
industry_matcher: Optional[IndustryMatcher] = None

def init_industry_matcher(csv_path: str, embedding_model: SentenceTransformer):
    """Initialize the global industry matcher instance."""
    global industry_matcher
    industry_matcher = IndustryMatcher(csv_path, embedding_model)
    logger.info("✅ Industry matcher initialized")

def get_industry_matcher() -> IndustryMatcher:
    """Get the global industry matcher instance."""
    if industry_matcher is None:
        raise RuntimeError("Industry matcher not initialized. Call init_industry_matcher() first.")
    return industry_matcher
