"""Quick test of the markdown parser"""

from pathlib import Path
from backend.services.parser import parse_markdown_file

# Test with first markdown file
md_file = Path("md_data/01 - Ameristar Jet Charter Inc v Signal Composites Inc.md")

if md_file.exists():
    print(f"Parsing: {md_file.name}")
    ast = parse_markdown_file(md_file)

    print(f"\n{'='*60}")
    print(f"Filename: {ast.filename}")
    print(f"Sections: {len(ast.sections)}")
    print(f"Citations: {len(ast.all_citations)}")
    print(f"Expert Names: {len(ast.all_expert_names)}")
    print(f"Legal Entities: {len(ast.all_legal_entities)}")
    print(f"Daubert Mentions: {ast.daubert_mentions}")
    print(f"{'='*60}\n")

    # Show sections
    print("SECTIONS:")
    for i, section in enumerate(ast.sections, 1):
        print(f"\n{i}. {section.header} (Level {section.level})")
        print(f"   Content length: {len(section.content)} chars")
        if section.citations:
            print(f"   Citations: {section.citations[:2]}")  # First 2
        if section.expert_names:
            print(f"   Experts: {section.expert_names}")
        if section.has_daubert_mention:
            print(f"   ✓ Contains Daubert mention")

    # Show aggregated data
    print(f"\n{'='*60}")
    print("AGGREGATED METADATA:")
    print(f"\nAll Citations ({len(ast.all_citations)}):")
    for citation in ast.all_citations[:3]:  # First 3
        print(f"  - {citation}")

    print(f"\nAll Expert Names ({len(ast.all_expert_names)}):")
    for expert in ast.all_expert_names:
        print(f"  - {expert}")

    print(f"\nAll Legal Entities ({len(ast.all_legal_entities)}):")
    for entity in ast.all_legal_entities[:5]:  # First 5
        print(f"  - {entity}")

else:
    print(f"File not found: {md_file}")
