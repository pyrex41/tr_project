#!/usr/bin/env python3
"""
Add Exclusion Flag to Metadata

Extracts whether experts were excluded from the GPT analysis.
"""

import json
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "orders.db"


def has_exclusion(exclusion_text: str) -> bool:
    """
    Determine if the order contains expert exclusions.

    Args:
        exclusion_text: Text from analysis['exclusion_admission']

    Returns:
        True if experts were excluded
    """
    if not exclusion_text:
        return False

    exclusion_text_lower = exclusion_text.lower()

    # Strong indicators of exclusion
    exclusion_indicators = [
        'explicitly excludes',
        'testimony is excluded',
        'motion to strike is granted',
        'testimony excluded',
        'excluded from testifying',
        'exclude the testimony',
        'excludes the expert',
        'granted the motion to strike',
        'struck from',
        'testimony stricken'
    ]

    # Strong indicators of admission (no exclusion)
    admission_indicators = [
        'motion to strike is denied',
        'denies the motion',
        'explicitly denies',
        'motion denied',
        'may proceed',
        'permitted to present',
        'may testify',
        'admitted to testify'
    ]

    # Check for exclusion indicators
    has_exclusion_indicator = any(ind in exclusion_text_lower for ind in exclusion_indicators)

    # Check for admission indicators (overrides exclusion if both present)
    has_admission_indicator = any(ind in exclusion_text_lower for ind in admission_indicators)

    # If we have exclusion indicators and NO admission indicators, it's an exclusion
    if has_exclusion_indicator and not has_admission_indicator:
        return True

    return False


def main():
    """Add has_exclusion flag to metadata."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, metadata_json, analysis_json FROM orders")
    rows = cursor.fetchall()

    updated_count = 0
    excluded_orders = []

    for row in rows:
        order_id = row['id']
        filename = row['filename']
        metadata = json.loads(row['metadata_json'])
        analysis_data = json.loads(row['analysis_json'])

        # Check exclusion status
        if 'analysis' in analysis_data and 'exclusion_admission' in analysis_data['analysis']:
            exclusion_text = analysis_data['analysis']['exclusion_admission']
            has_exclusion_flag = has_exclusion(exclusion_text)

            # Update metadata
            metadata['has_exclusion'] = has_exclusion_flag

            # Save back to database
            cursor.execute(
                "UPDATE orders SET metadata_json = ? WHERE id = ?",
                (json.dumps(metadata), order_id)
            )

            if has_exclusion_flag:
                excluded_orders.append(f"  {order_id}: {filename}")

            logger.info(f"Order {order_id}: has_exclusion={has_exclusion_flag}")
            updated_count += 1

    conn.commit()
    conn.close()

    logger.info(f"\nUpdated {updated_count} orders with exclusion flags")
    logger.info(f"\nOrders with exclusions ({len(excluded_orders)}):")
    for order in excluded_orders:
        logger.info(order)


if __name__ == "__main__":
    main()
