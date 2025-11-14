"""
Script to populate database from processing_results.json

Reads the processed analysis results and loads them into SQLite.
"""

import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_markdown_file(filename: str, md_data_dir: Path) -> str:
    """Load raw markdown content from file."""
    file_path = md_data_dir / filename
    if not file_path.exists():
        logger.warning(f"Markdown file not found: {file_path}")
        return ""

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def populate_database():
    """Populate database from processing results."""

    # Initialize paths
    project_root = Path(__file__).parent.parent.parent
    results_path = project_root / "data" / "processing_results.json"
    md_data_dir = project_root / "md_data"

    logger.info(f"Loading processing results from: {results_path}")

    # Load processing results
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)

    logger.info(f"Found {results['total_files']} files to process")
    logger.info(f"Successful: {results['successful']}, Failed: {results['failed']}")

    # Initialize database
    db = DatabaseService(str(project_root / "data" / "orders.db"))

    # Check if database already has data
    stats = db.get_stats()
    if stats['total_orders'] > 0:
        logger.warning(f"Database already contains {stats['total_orders']} orders")
        response = input("Do you want to continue and add more? (y/n): ")
        if response.lower() != 'y':
            logger.info("Aborting")
            return

    # Process each result
    inserted_count = 0
    error_count = 0

    for result in results['results']:
        filename = result['filename']

        try:
            if not result['success']:
                logger.warning(f"Skipping failed result: {filename}")
                continue

            # Load raw markdown
            raw_text = load_markdown_file(filename, md_data_dir)
            if not raw_text:
                logger.error(f"Could not load markdown for: {filename}")
                error_count += 1
                continue

            # Extract data
            metadata = result['metadata']
            analysis = result.get('deep_analysis', {})

            # Insert into database
            order_id = db.insert_order(
                filename=filename,
                raw_text=raw_text,
                metadata=metadata,
                analysis=analysis
            )

            logger.info(f"✅ Inserted order {order_id}: {filename}")
            inserted_count += 1

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}", exc_info=True)
            error_count += 1

    # Print summary
    logger.info("=" * 80)
    logger.info("DATABASE POPULATION COMPLETE")
    logger.info(f"Successfully inserted: {inserted_count} orders")
    logger.info(f"Errors: {error_count}")

    # Print final stats
    final_stats = db.get_stats()
    logger.info("=" * 80)
    logger.info("DATABASE STATISTICS:")
    logger.info(f"  Total orders: {final_stats['total_orders']}")
    logger.info(f"  Orders with analysis: {final_stats['orders_with_analysis']}")
    logger.info(f"  Order embeddings: {final_stats['order_embeddings']}")
    logger.info(f"  Analysis chunks: {final_stats['analysis_chunks']}")
    logger.info(f"  Chunk embeddings: {final_stats['chunk_embeddings']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    populate_database()
