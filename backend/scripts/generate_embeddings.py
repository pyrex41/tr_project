"""
Generate Embeddings for All Orders

Creates embeddings for:
1. Full order text (order_embeddings)
2. Individual analysis sections (chunk_embeddings)
"""

import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import DatabaseService
from services.embeddings import EmbeddingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_all_embeddings():
    """Generate embeddings for all orders and analysis chunks."""

    # Initialize services
    project_root = Path(__file__).parent.parent.parent
    db = DatabaseService(str(project_root / "data" / "orders.db"))
    embedding_service = EmbeddingService()

    logger.info("Starting embedding generation...")

    # Get all orders
    all_orders = db.get_all_orders(limit=1000)
    logger.info(f"Found {len(all_orders)} orders to process")

    order_embeddings_count = 0
    chunk_embeddings_count = 0

    for order_summary in all_orders:
        order_id = order_summary['id']
        filename = order_summary['filename']

        try:
            # Get full order details
            order = db.get_order_by_id(order_id)
            if not order:
                logger.warning(f"Order {order_id} not found")
                continue

            logger.info(f"Processing order {order_id}: {filename}")

            # Generate embedding for full order text
            full_text = order['raw_text']
            if full_text:
                logger.info(f"  Generating order embedding...")
                order_embedding = embedding_service.generate_embedding(full_text)
                db.insert_order_embedding(order_id, order_embedding)
                order_embeddings_count += 1
                logger.info(f"  ✅ Order embedding generated")

            # Generate embeddings for analysis chunks
            analysis = order.get('analysis')
            if analysis and 'analysis' in analysis:
                analysis_sections = analysis['analysis']

                # Define the 10 sections to embed
                section_names = [
                    'case_context',
                    'expert_profile',
                    'challenged_methodology',
                    'daubert_standards',
                    'court_reasoning',
                    'exclusion_admission',
                    'precedent_analysis',
                    'implications',
                    'judicial_patterns',
                    'key_takeaways'
                ]

                for section_name in section_names:
                    if section_name in analysis_sections:
                        content = analysis_sections[section_name]

                        if content and len(content.strip()) > 0:
                            logger.info(f"    Generating chunk embedding for: {section_name}")
                            chunk_embedding = embedding_service.generate_embedding(content)

                            chunk_id = db.insert_analysis_chunk(
                                order_id=order_id,
                                section_name=section_name,
                                content=content,
                                embedding=chunk_embedding
                            )

                            chunk_embeddings_count += 1
                            logger.info(f"    ✅ Chunk {chunk_id} embedded")

        except Exception as e:
            logger.error(f"Error processing order {order_id}: {e}", exc_info=True)

    # Print summary
    logger.info("=" * 80)
    logger.info("EMBEDDING GENERATION COMPLETE")
    logger.info(f"Order embeddings generated: {order_embeddings_count}")
    logger.info(f"Chunk embeddings generated: {chunk_embeddings_count}")

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
    generate_all_embeddings()
