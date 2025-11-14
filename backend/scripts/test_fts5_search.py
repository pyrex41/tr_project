"""
Test FTS5 full-text search functionality

Tests keyword search with various queries to ensure FTS5 is working properly.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import DatabaseService


def test_search_queries():
    """Test various search queries."""

    db = DatabaseService(str(Path(__file__).parent.parent.parent / "data" / "orders.db"))

    # Test queries
    test_queries = [
        "Daubert",
        "expert witness",
        "methodology",
        "excluded",
        "testimony",
        "FRE 702",
        "reliability",
        "scientific evidence",
    ]

    print("=" * 80)
    print("FTS5 FULL-TEXT SEARCH TESTS")
    print("=" * 80)

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 80)

        try:
            results = db.keyword_search(query, limit=5)

            if results:
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['filename']}")
                    print(f"     Relevance: {result['relevance_score']:.2f}")
                    print(f"     Case: {result['metadata'].get('case_name', 'N/A')}")
            else:
                print("  No results found")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("FTS5 SEARCH TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_search_queries()
