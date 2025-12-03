"""Quick test to analyze Motorola docs structure."""
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def test():
    browser_config = BrowserConfig(headless=True, verbose=True)
    crawler_config = CrawlerRunConfig(
        page_timeout=30000,
        delay_before_return_html=2.0
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            'https://docs.motorolasolutions.com/bundle/89303/page/23111842.html',
            config=crawler_config
        )
        
        print(f"\nSuccess: {result.success}")
        print(f"Title: {result.metadata.get('title', 'N/A')}")
        print(f"Total internal links: {len(result.links.get('internal', []))}")
        print(f"Total external links: {len(result.links.get('external', []))}")
        
        # Show ALL internal links to see what we got
        all_internal = result.links.get('internal', [])
        print(f"\nAll internal links:")
        for link in all_internal[:30]:
            print(f"  - {link}")
        
        # Filter for page links in the same bundle
        page_links = [
            link for link in all_internal
            if '/bundle/89303/page/' in link or '/page/' in link
        ]
        
        print(f"\n\nPage links with /page/: {len(page_links)}")
        for link in page_links[:10]:
            print(f"  - {link}")
        
        # Check the HTML for navigation structure
        print(f"\n\nHTML length: {len(result.html)}")
        print(f"\n\nSearching HTML for navigation patterns...")
        
        if 'bundle/89303/page/' in result.html:
            print("✓ Found bundle page references in HTML")
            # Extract some examples
            import re
            matches = re.findall(r'bundle/89303/page/[a-f0-9]+', result.html)
            unique_pages = list(set(matches))[:10]
            print(f"Found {len(set(matches))} unique page IDs in HTML:")
            for page_id in unique_pages:
                print(f"  - https://docs.motorolasolutions.com/{page_id}.html")
        
        print(f"\n\nFirst 1000 chars of markdown:\n{result.markdown.raw_markdown[:1000]}")

asyncio.run(test())
