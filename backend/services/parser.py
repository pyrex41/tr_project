"""
Markdown AST Parser for Legal Documents

Parses markdown files containing Judge Boyle's expert witness rulings
into a structured Abstract Syntax Tree (AST) for further analysis.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class OrderSection:
    """Represents a section within a legal order document."""

    header: str
    content: str
    level: int  # Header level (1-6)
    citations: List[str] = field(default_factory=list)
    expert_names: List[str] = field(default_factory=list)
    legal_entities: List[str] = field(default_factory=list)
    has_daubert_mention: bool = False


@dataclass
class OrderAST:
    """Abstract Syntax Tree representation of a complete legal order."""

    filename: str
    raw_text: str
    sections: List[OrderSection] = field(default_factory=list)
    all_citations: List[str] = field(default_factory=list)
    all_expert_names: List[str] = field(default_factory=list)
    all_legal_entities: List[str] = field(default_factory=list)
    daubert_mentions: int = 0


class MarkdownParser:
    """Parser for converting legal order markdown into structured AST."""

    # Regex patterns for extraction
    # Match full case citations like "Daubert v. Merrell-Dow Pharmaceuticals, Inc., 509 U.S. 579"
    CITATION_PATTERN = re.compile(
        r'([A-Z][\w\s&\.-]+\s+v\.\s+[\w\s&\.-]+,\s*\d+\s+[UF]\.\s*(?:S\.|Supp\.|3d|2d|App\.)\s*\d+)'
    )

    # Short citation format like "509 U.S. 579"
    CITATION_PATTERN_SHORT = re.compile(
        r'(\d+\s+[UF]\.\s*(?:S\.|Supp\.|3d|2d|App\.)\s*\d+)'
    )

    # Named Expert pattern - catches explicit expert declarations
    NAMED_EXPERT_PATTERN = re.compile(
        r'Named Expert[s]?:\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)*)',
        re.IGNORECASE
    )

    # Expert name patterns (titles and credentials) - more restrictive
    EXPERT_TITLE_PATTERN = re.compile(
        r'\b(Dr\.|Ph\.D\.|M\.D\.|Professor|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s+)?[A-Z][a-z]+)'
    )

    # Witness/Expert in context - must have capital letter names on both sides
    EXPERT_CONTEXT_PATTERN = re.compile(
        r'(?:Strike|testimony of|deposition of)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s+)?[A-Z][a-z]+)',
        re.IGNORECASE
    )

    # Legal entities
    ENTITY_PATTERN = re.compile(
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Corp|Ltd|Co))\.?)'
    )

    # Daubert mentions
    DAUBERT_PATTERN = re.compile(
        r'\b(Daubert|daubert|FRE\s*702|Fed\.\s*R\.\s*Evid\.\s*702)\b'
    )

    # Header pattern (markdown headers)
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse_file(self, file_path: Path) -> OrderAST:
        """
        Parse a markdown file into an OrderAST.

        Args:
            file_path: Path to the markdown file

        Returns:
            OrderAST representation of the document
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        return self.parse_md_to_ast(file_path.name, raw_text)

    def parse_md_to_ast(self, filename: str, raw_text: str) -> OrderAST:
        """
        Parse markdown text into structured AST using a state machine.

        Args:
            filename: Name of the source file
            raw_text: Raw markdown content

        Returns:
            OrderAST with extracted sections and metadata
        """
        ast = OrderAST(filename=filename, raw_text=raw_text)

        lines = raw_text.split('\n')

        # State machine variables
        current_section: Optional[OrderSection] = None
        current_content: List[str] = []

        for line in lines:
            # Check for header
            header_match = self.HEADER_PATTERN.match(line)

            if header_match:
                # Save previous section if exists
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    self._extract_section_metadata(current_section)
                    ast.sections.append(current_section)

                # Start new section
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()

                current_section = OrderSection(
                    header=header_text,
                    content="",
                    level=header_level
                )
                current_content = []
            else:
                # Accumulate content for current section
                if current_section:
                    current_content.append(line)
                else:
                    # Content before first header - create implicit section
                    if not current_section:
                        current_section = OrderSection(
                            header="[Document Start]",
                            content="",
                            level=0
                        )
                    current_content.append(line)

        # Don't forget the last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            self._extract_section_metadata(current_section)
            ast.sections.append(current_section)

        # Aggregate metadata across all sections
        self._aggregate_ast_metadata(ast)

        return ast

    def _extract_section_metadata(self, section: OrderSection) -> None:
        """
        Extract citations, expert names, entities, and Daubert mentions from section content.

        Args:
            section: OrderSection to extract metadata from
        """
        text = section.content

        # Extract citations
        citations = self.CITATION_PATTERN.findall(text)
        citations_short = self.CITATION_PATTERN_SHORT.findall(text)
        section.citations = list(set(citations + citations_short))

        # Extract expert names - multiple strategies
        expert_names = []

        # 1. Named Expert declarations (highest priority)
        named_expert_match = self.NAMED_EXPERT_PATTERN.search(text)
        if named_expert_match:
            expert_list = named_expert_match.group(1)
            # Split on commas and clean up
            experts = [name.strip() for name in expert_list.split(',')]
            expert_names.extend(experts)

        # 2. Experts with titles (Dr., Prof., etc.)
        expert_matches = self.EXPERT_TITLE_PATTERN.findall(text)
        expert_names.extend([f"{title} {name}" for title, name in expert_matches])

        # 3. Experts in context (expert witness X, testimony of Y)
        context_matches = self.EXPERT_CONTEXT_PATTERN.findall(text)
        expert_names.extend(context_matches)

        # Deduplicate and filter out common false positives
        expert_names = list(set(expert_names))
        expert_names = [
            name for name in expert_names
            if not any(fp in name for fp in [
                'District', 'United States', 'Court', 'Government',
                'Thomson Reuters', 'Law Firms', 'Citations', 'All',
                'Pages', 'Total', 'Division', 'Strike', 'Not Reported'
            ])
        ]

        section.expert_names = expert_names

        # Extract legal entities
        entities = self.ENTITY_PATTERN.findall(text)
        section.legal_entities = list(set(entities))

        # Check for Daubert mentions
        daubert_matches = self.DAUBERT_PATTERN.findall(text)
        section.has_daubert_mention = len(daubert_matches) > 0

    def _aggregate_ast_metadata(self, ast: OrderAST) -> None:
        """
        Aggregate metadata from all sections into the AST root.

        Args:
            ast: OrderAST to populate with aggregated metadata
        """
        all_citations = []
        all_experts = []
        all_entities = []
        daubert_count = 0

        for section in ast.sections:
            all_citations.extend(section.citations)
            all_experts.extend(section.expert_names)
            all_entities.extend(section.legal_entities)
            if section.has_daubert_mention:
                daubert_count += 1

        # Deduplicate and store
        ast.all_citations = list(set(all_citations))
        ast.all_expert_names = list(set(all_experts))
        ast.all_legal_entities = list(set(all_entities))
        ast.daubert_mentions = daubert_count

    def extract_plain_text(self, ast: OrderAST) -> str:
        """
        Extract plain text from AST, removing markdown formatting.

        Args:
            ast: OrderAST to extract text from

        Returns:
            Plain text representation
        """
        parts = []
        for section in ast.sections:
            if section.header != "[Document Start]":
                parts.append(f"\n{section.header}\n")
            parts.append(section.content)

        return '\n'.join(parts).strip()


# Convenience function
def parse_markdown_file(file_path: Path) -> OrderAST:
    """
    Convenience function to parse a markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        OrderAST representation
    """
    parser = MarkdownParser()
    return parser.parse_file(file_path)
