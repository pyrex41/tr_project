#!/usr/bin/env python3
"""
Parallel Processing Pipeline for Legal Orders

Processes all 19 markdown files in parallel:
1. Parse markdown into AST
2. Extract basic metadata
3. (Future) Generate deep analysis with GPT-5.1
4. (Future) Generate embeddings
5. (Future) Store in database

Usage:
    python backend/scripts/process_all_orders.py [--max-concurrent N]
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.parser import parse_markdown_file, OrderAST, MarkdownParser
from backend.services.metadata_extractor import extract_metadata
from backend.services.deep_analysis import DeepAnalysisService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/processing.log')
    ]
)
logger = logging.getLogger(__name__)


class OrderProcessor:
    """Handles parallel processing of legal orders."""

    def __init__(self, max_concurrent: int = 3, enable_deep_analysis: bool = True):
        """
        Initialize processor.

        Args:
            max_concurrent: Maximum number of concurrent operations
            enable_deep_analysis: Whether to run GPT analysis (default: True)
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.enable_deep_analysis = enable_deep_analysis
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, str]] = []

        # Initialize deep analysis service if enabled
        if self.enable_deep_analysis:
            self.analysis_service = DeepAnalysisService()
            logger.info("Deep analysis enabled - will use GPT-5 nano (fastest)")
        else:
            self.analysis_service = None
            logger.info("Deep analysis disabled - parsing only")

    async def process_single_order(self, md_file: Path) -> Dict[str, Any]:
        """
        Process a single order file.

        Args:
            md_file: Path to markdown file

        Returns:
            Dictionary containing processing results
        """
        async with self.semaphore:
            try:
                logger.info(f"Processing: {md_file.name}")
                start_time = time.time()

                # Step 1: Parse markdown
                ast = await asyncio.to_thread(parse_markdown_file, md_file)
                logger.debug(f"  ✓ Parsed {len(ast.sections)} sections")

                # Step 2: Extract basic metadata
                metadata = await asyncio.to_thread(extract_metadata, ast)
                logger.debug(f"  ✓ Extracted metadata: {metadata['case_name']}")

                # Step 3: Deep analysis with GPT-4o
                deep_analysis = None
                if self.enable_deep_analysis and self.analysis_service:
                    parser = MarkdownParser()
                    plain_text = parser.extract_plain_text(ast)
                    analysis_result = await self.analysis_service.generate_analysis(
                        plain_text, metadata
                    )
                    deep_analysis = analysis_result
                    logger.debug(
                        f"  ✓ Generated analysis: {analysis_result['token_usage']['total_tokens']} tokens, "
                        f"${analysis_result['token_usage']['cost_usd']:.4f}"
                    )

                # Step 4: TODO - Generate embeddings
                # This will be added after deep analysis
                embeddings = None  # Placeholder

                processing_time = time.time() - start_time

                result = {
                    'filename': md_file.name,
                    'success': True,
                    'metadata': metadata,
                    'ast_summary': {
                        'sections': len(ast.sections),
                        'citations': len(ast.all_citations),
                        'experts': len(ast.all_expert_names),
                        'daubert_mentions': ast.daubert_mentions,
                    },
                    'deep_analysis': deep_analysis,
                    'embeddings': embeddings,
                    'processing_time_seconds': round(processing_time, 2),
                }

                logger.info(
                    f"✓ Completed: {md_file.name} "
                    f"({processing_time:.2f}s, "
                    f"{len(ast.all_expert_names)} experts, "
                    f"{ast.daubert_mentions} Daubert mentions)"
                )

                return result

            except Exception as e:
                logger.error(f"✗ Error processing {md_file.name}: {str(e)}", exc_info=True)
                return {
                    'filename': md_file.name,
                    'success': False,
                    'error': str(e),
                }

    async def process_all_orders(self, md_dir: Path) -> Dict[str, Any]:
        """
        Process all markdown files in parallel.

        Args:
            md_dir: Directory containing markdown files

        Returns:
            Summary of processing results
        """
        start_time = time.time()

        # Find all markdown files
        md_files = sorted(md_dir.glob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files to process")
        logger.info(f"Max concurrent operations: {self.max_concurrent}")

        if not md_files:
            logger.error(f"No markdown files found in {md_dir}")
            return {'error': 'No files found'}

        # Create data directory if needed
        Path('data').mkdir(exist_ok=True)

        # Process all files in parallel
        tasks = [self.process_single_order(md_file) for md_file in md_files]
        results = await asyncio.gather(*tasks)

        # Separate successes and failures
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]

        total_time = time.time() - start_time

        summary = {
            'total_files': len(md_files),
            'successful': len(successful),
            'failed': len(failed),
            'total_time_seconds': round(total_time, 2),
            'average_time_per_file': round(total_time / len(md_files), 2) if md_files else 0,
            'results': results,
        }

        # Calculate total costs if deep analysis was enabled
        if self.enable_deep_analysis and self.analysis_service:
            cost_stats = self.analysis_service.get_total_cost()
            summary['cost_statistics'] = cost_stats

        # Save results to JSON
        output_file = Path('data/processing_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total files: {summary['total_files']}")
        logger.info(f"Successful: {summary['successful']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Total time: {summary['total_time_seconds']:.2f}s")
        logger.info(f"Average per file: {summary['average_time_per_file']:.2f}s")

        if self.enable_deep_analysis and 'cost_statistics' in summary:
            stats = summary['cost_statistics']
            logger.info(f"\nAI COST STATISTICS:")
            logger.info(f"  Total tokens: {stats['total_tokens']:,}")
            logger.info(f"  Input tokens: {stats['total_input_tokens']:,}")
            logger.info(f"  Output tokens: {stats['total_output_tokens']:,}")
            logger.info(f"  Total cost: ${stats['total_cost_usd']:.2f}")
            logger.info(f"  Cost per file: ${stats['total_cost_usd']/summary['successful']:.4f}")

        logger.info(f"\nResults saved to: {output_file}")
        logger.info(f"{'='*60}\n")

        return summary


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Process legal orders in parallel')
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=3,
        help='Maximum number of concurrent GPT API operations (default: 3)'
    )
    parser.add_argument(
        '--md-dir',
        type=Path,
        default=Path('md_data'),
        help='Directory containing markdown files (default: md_data)'
    )
    parser.add_argument(
        '--no-analysis',
        action='store_true',
        help='Disable deep analysis (parsing only, faster)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: process only the first file'
    )

    args = parser.parse_args()

    processor = OrderProcessor(
        max_concurrent=args.max_concurrent,
        enable_deep_analysis=not args.no_analysis
    )

    # Test mode: process only first file
    if args.test:
        md_files = sorted(args.md_dir.glob("*.md"))
        if md_files:
            logger.info("TEST MODE: Processing only first file")
            result = await processor.process_single_order(md_files[0])
            print(json.dumps(result, indent=2))
            return

    summary = await processor.process_all_orders(args.md_dir)

    # Exit with error code if any failed
    if summary.get('failed', 0) > 0:
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
