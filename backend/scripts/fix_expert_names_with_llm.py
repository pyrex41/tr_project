#!/usr/bin/env python3
"""
Fix Expert Names Using LLM

Uses GPT to extract expert witness names from the existing analysis.
"""

import json
import sqlite3
import logging
import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "orders.db"
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def extract_expert_names_with_llm(expert_profile: str, case_context: str) -> list[str]:
    """
    Use GPT to extract expert witness names from analysis text.

    Args:
        expert_profile: Expert profile section from analysis
        case_context: Case context for additional context

    Returns:
        List of expert witness names
    """
    prompt = f"""Extract ONLY the expert witness names from this legal analysis. Return a JSON array of names.

Rules:
- Only include actual expert witnesses (people testifying as experts)
- Do NOT include party names, company names, or attorneys
- Do NOT include fragments or partial phrases
- Use full names when available (e.g., "Dr. John Smith" not just "John")
- Return empty array [] if no experts found

Case Context:
{case_context[:500]}

Expert Profile:
{expert_profile}

Return format: {{"expert_names": ["Name 1", "Name 2"]}}
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap for extraction
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured data from legal documents."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("expert_names", [])

    except Exception as e:
        logger.error(f"Error extracting names: {e}")
        return []


async def process_order(order_id, filename, metadata, analysis_data):
    """Process a single order."""
    if 'analysis' not in analysis_data:
        return None

    analysis = analysis_data['analysis']
    expert_profile = analysis.get('expert_profile', '')
    case_context = analysis.get('case_context', '')

    if not expert_profile:
        return None

    # Extract names with LLM
    expert_names = await extract_expert_names_with_llm(expert_profile, case_context)

    old_names = metadata.get('expert_names', [])
    metadata['expert_names'] = expert_names
    metadata['expert_count'] = len(expert_names)

    logger.info(f"Order {order_id} ({filename}):")
    logger.info(f"  Old ({len(old_names)}): {old_names}")
    logger.info(f"  New ({len(expert_names)}): {expert_names}")

    return (order_id, json.dumps(metadata))


async def main():
    """Update expert names using LLM extraction."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, metadata_json, analysis_json FROM orders")
    rows = cursor.fetchall()

    # Process all orders concurrently (with rate limiting)
    tasks = []
    for row in rows:
        order_id = row['id']
        filename = row['filename']
        metadata = json.loads(row['metadata_json'])
        analysis_data = json.loads(row['analysis_json'])

        tasks.append(process_order(order_id, filename, metadata, analysis_data))

    # Run with concurrency limit (5 at a time to avoid rate limits)
    results = []
    for i in range(0, len(tasks), 5):
        batch = tasks[i:i+5]
        batch_results = await asyncio.gather(*batch)
        results.extend(batch_results)
        await asyncio.sleep(1)  # Rate limiting

    # Update database
    updated_count = 0
    for result in results:
        if result:
            order_id, metadata_json = result
            cursor.execute(
                "UPDATE orders SET metadata_json = ? WHERE id = ?",
                (metadata_json, order_id)
            )
            updated_count += 1

    conn.commit()
    conn.close()

    logger.info(f"\nUpdated {updated_count}/{len(rows)} orders with LLM-extracted expert names")


if __name__ == "__main__":
    asyncio.run(main())
