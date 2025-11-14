#!/usr/bin/env python3
"""
Fix Expert Names from GPT Analysis

Extracts expert names from existing GPT-5.1 analysis (expert_profile field)
and updates the metadata in the database.
"""

import re
import json
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "orders.db"


def extract_expert_names_from_analysis(expert_profile: str) -> list[str]:
    """
    Extract expert names from GPT analysis expert_profile text.

    Args:
        expert_profile: Text from analysis['expert_profile']

    Returns:
        List of expert names
    """
    names = []

    # Pattern 1: "names X and Y as" or "identifies X and Y"
    pattern1 = re.compile(r'names?\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)', re.IGNORECASE)
    matches = pattern1.findall(expert_profile)
    for match in matches:
        names.extend(match)

    # Pattern 2: "Dr./Prof. Name"
    pattern2 = re.compile(r'\b(Dr\.|Prof\.|Professor)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)')
    matches = pattern2.findall(expert_profile)
    for title, name in matches:
        names.append(f"{title} {name}")

    # Pattern 3: Names in quotes
    pattern3 = re.compile(r'"([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)"')
    names.extend(pattern3.findall(expert_profile))

    # Pattern 4: "testimony of X" or "expert X"
    pattern4 = re.compile(r'(?:testimony of|expert witness|expert)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)', re.IGNORECASE)
    names.extend(pattern4.findall(expert_profile))

    # Pattern 5: Standalone proper names (2-3 words, capitalized)
    pattern5 = re.compile(r'\b([A-Z][a-z]{2,}\s+(?:[A-Z]\.?\s*)?[A-Z][a-z]{2,})\b')
    potential_names = pattern5.findall(expert_profile)

    # Filter out common false positives
    false_positives = {
        'United States', 'District Court', 'Northern District', 'Federal Rules',
        'Daubert Standards', 'Expert Testimony', 'Motion Strike', 'Court Rules',
        'Summary Judgment', 'Civil Procedure', 'Expert Witness', 'Court Finds',
        'Plaintiff argues', 'Defendant contends', 'Court concludes', 'Court holds',
        'Federal Court', 'Trial Court', 'Appellate Court', 'Expert Profile',
        'Case Context', 'Key Takeaways', 'Judicial Patterns'
    }

    for name in potential_names:
        if name not in false_positives and not any(fp.lower() in name.lower() for fp in ['court', 'federal', 'district', 'motion', 'rules', 'standards']):
            names.append(name)

    # Deduplicate and return
    return sorted(list(set(names)))


def main():
    """Update expert names from GPT analysis."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, metadata_json, analysis_json FROM orders")
    rows = cursor.fetchall()

    updated_count = 0

    for row in rows:
        order_id = row['id']
        filename = row['filename']

        # Parse existing data
        metadata = json.loads(row['metadata_json'])
        analysis_data = json.loads(row['analysis_json'])

        # Extract expert names from GPT analysis
        if 'analysis' in analysis_data and 'expert_profile' in analysis_data['analysis']:
            expert_profile = analysis_data['analysis']['expert_profile']
            expert_names = extract_expert_names_from_analysis(expert_profile)

            # Update metadata
            old_names = metadata.get('expert_names', [])
            metadata['expert_names'] = expert_names
            metadata['expert_count'] = len(expert_names)

            # Save back to database
            cursor.execute(
                "UPDATE orders SET metadata_json = ? WHERE id = ?",
                (json.dumps(metadata), order_id)
            )

            logger.info(f"Order {order_id} ({filename}): {len(old_names)} -> {len(expert_names)} experts")
            logger.info(f"  Old: {old_names}")
            logger.info(f"  New: {expert_names}")

            updated_count += 1

    conn.commit()
    conn.close()

    logger.info(f"\nUpdated {updated_count} orders with expert names from GPT analysis")


if __name__ == "__main__":
    main()
