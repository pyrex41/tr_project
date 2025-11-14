"""
Basic Metadata Extraction Service

Extracts case metadata from parsed OrderAST without using AI/LLM.
Extracts: case name, dates, docket numbers, expert counts, etc.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.services.parser import OrderAST


class MetadataExtractor:
    """Extracts basic metadata from legal order documents."""

    # Date patterns
    DATE_PATTERNS = [
        re.compile(r'\b([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})\b'),  # August 17, 2001
        re.compile(r'\b(\d{1,2}/\d{1,2}/\d{4})\b'),  # 8/17/2001
        re.compile(r'\b(\d{4}-\d{2}-\d{2})\b'),  # 2001-08-17
    ]

    # Docket number pattern
    DOCKET_PATTERN = re.compile(
        r'No\.\s+([\d–-]+[A-Z]+-?[A-Z]*[\d–-]+)',
        re.IGNORECASE
    )

    # Case name pattern (from title)
    CASE_NAME_PATTERN = re.compile(
        r'^(?:\d+\s*-\s*)?(.+?)\s*(?:\.md)?$'
    )

    # Judge name pattern
    JUDGE_PATTERN = re.compile(
        r'([A-Z]+\s+[A-Z]+\.\s+[A-Z]+),\s*(?:District|Circuit|Magistrate)\s+Judge',
        re.IGNORECASE
    )

    def extract_basic_metadata(self, ast: OrderAST) -> Dict[str, Any]:
        """
        Extract basic metadata from an OrderAST.

        Args:
            ast: Parsed OrderAST

        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            'filename': ast.filename,
            'case_name': self._extract_case_name(ast),
            'docket_number': self._extract_docket_number(ast),
            'date': self._extract_date(ast),
            'judge_name': self._extract_judge_name(ast),
            'expert_count': len(ast.all_expert_names),
            'expert_names': ast.all_expert_names,
            'citation_count': len(ast.all_citations),
            'citations': ast.all_citations,
            'daubert_mentions': ast.daubert_mentions,
            'has_daubert': ast.daubert_mentions > 0,
            'section_count': len(ast.sections),
            'word_count': len(ast.raw_text.split()),
            'char_count': len(ast.raw_text),
        }

        return metadata

    def _extract_case_name(self, ast: OrderAST) -> Optional[str]:
        """Extract case name from filename or first section header."""
        # Try from filename first
        match = self.CASE_NAME_PATTERN.match(ast.filename)
        if match:
            case_name = match.group(1)
            # Remove file extension if present
            case_name = case_name.replace('.md', '').strip()
            return case_name

        # Try from first section header
        if ast.sections and ast.sections[0].header != "[Document Start]":
            header = ast.sections[0].header
            match = self.CASE_NAME_PATTERN.match(header)
            if match:
                return match.group(1).strip()

        return None

    def _extract_docket_number(self, ast: OrderAST) -> Optional[str]:
        """Extract docket number from document text."""
        match = self.DOCKET_PATTERN.search(ast.raw_text)
        if match:
            return match.group(1)
        return None

    def _extract_date(self, ast: OrderAST) -> Optional[str]:
        """Extract date from document text."""
        for pattern in self.DATE_PATTERNS:
            match = pattern.search(ast.raw_text)
            if match:
                date_str = match.group(1)
                # Try to parse and normalize
                try:
                    # Try different formats
                    for fmt in ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(date_str.replace('.', ''), fmt)
                            return dt.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                    # If parsing failed, return as-is
                    return date_str
                except Exception:
                    return date_str

        return None

    def _extract_judge_name(self, ast: OrderAST) -> Optional[str]:
        """Extract judge name from document text."""
        match = self.JUDGE_PATTERN.search(ast.raw_text)
        if match:
            return match.group(1)
        return None


# Convenience function
def extract_metadata(ast: OrderAST) -> Dict[str, Any]:
    """
    Convenience function to extract metadata from an OrderAST.

    Args:
        ast: Parsed OrderAST

    Returns:
        Dictionary of extracted metadata
    """
    extractor = MetadataExtractor()
    return extractor.extract_basic_metadata(ast)
