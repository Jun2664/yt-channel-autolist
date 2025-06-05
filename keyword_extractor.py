import re
from typing import List, Dict, Set
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import requests

class KeywordExtractor:
    """Extract and expand keywords from video titles"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self._setup_nltk()
        self.stop_words = self._get_stop_words()
        
    def _setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    
    def _get_stop_words(self) -> Set[str]:
        """Get stop words for the specified language"""
        language_map = {
            'en': 'english',
            'es': 'spanish',
            'pt': 'portuguese',
            'ja': None  # Japanese requires special handling
        }
        
        if self.language in language_map and language_map[self.language]:
            return set(stopwords.words(language_map[self.language]))
        return set()
    
    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract n-grams from text"""
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Tokenize
        if self.language == 'ja':
            # Simple space-based tokenization for Japanese
            # In production, would use mecab or similar
            tokens = text.split()
        else:
            tokens = word_tokenize(text)
        
        # Remove stop words
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]
        
        # Generate n-grams
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.append(ngram)
        
        return ngrams
    
    def extract_keywords_from_titles(self, titles: List[str], max_keywords: int = 20) -> List[str]:
        """Extract top keywords from a list of video titles"""
        all_ngrams = []
        
        # Extract 2-grams and 3-grams
        for title in titles:
            all_ngrams.extend(self.extract_ngrams(title, 2))
            all_ngrams.extend(self.extract_ngrams(title, 3))
        
        # Count frequencies
        ngram_counts = Counter(all_ngrams)
        
        # Get top keywords
        top_keywords = [ngram for ngram, _ in ngram_counts.most_common(max_keywords)]
        
        return top_keywords
    
    def expand_with_autosuggest(self, keyword: str, region: str = 'US', lang: str = 'en') -> List[str]:
        """Expand keywords using YouTube autosuggest"""
        suggestions = []
        
        # YouTube autosuggest endpoint
        url = 'http://suggestqueries.google.com/complete/search'
        params = {
            'client': 'youtube',
            'q': keyword,
            'gl': region.lower(),  # Geographic location
            'hl': lang,  # Language
            'ds': 'yt'  # Data source (YouTube)
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and isinstance(data[1], list):
                    suggestions = data[1][:10]  # Top 10 suggestions
        except Exception as e:
            print(f"Error getting autosuggest for '{keyword}': {e}")
        
        return suggestions
    
    def calculate_keyword_score(self, keyword: str, search_volume: int, competition: float) -> float:
        """Calculate keyword score based on volume and competition"""
        # Simple scoring: volume / (competition or 1)
        # Competition is typically 0-1, where 1 is high competition
        if competition <= 0:
            competition = 0.1  # Avoid division by zero
        
        score = search_volume / competition
        return round(score, 2)