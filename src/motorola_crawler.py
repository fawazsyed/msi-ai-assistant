"""
Motorola Documentation Crawler.

This crawler is specifically designed for docs.motorolasolutions.com structure:
1. Takes a "table of contents" page (like bundle/89303/page/23111842.html)
2. Extracts all navigation links to sub-pages in the same bundle
3. Crawls each sub-page individually
4. Creates a JSON entry for each with: title, URL, content snippet, and LLM-generated description

Usage:
    python src/motorola_crawler.py
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent


async def extract_navigation_links(toc_url: str) -> List[Dict[str, str]]:
    """
    Extract navigation links from the "What's New" section of the page.
    
    Args:
        toc_url: URL of the TOC page (e.g., bundle/89303/page/23111842.html)
        
    Returns:
        List of dicts with 'url' and 'text' (link text from "What's New" section)
    """
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    print(f"\n[+] Extracting 'What's New' links from: {toc_url}")
    
    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(
        page_timeout=30000,
        delay_before_return_html=2.0
    )
    
    navigation_links = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(toc_url, config=crawler_config)
        
        if not result.success:
            print(f"    [X] Failed to fetch TOC page: {result.error_message}")
            return []
        
        # Extract bundle ID from URL
        bundle_match = re.search(r'/bundle/(\d+)/', toc_url)
        if not bundle_match:
            print("    [X] Could not extract bundle ID from URL")
            return []
        
        bundle_id = bundle_match.group(1)
        print(f"    [+] Bundle ID: {bundle_id}")
        
        # Parse HTML to find "What's New" section
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Look for "What's New" heading or section
        whats_new_section = None
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            if "what's new" in heading.get_text().lower() or "whats new" in heading.get_text().lower():
                whats_new_section = heading
                print(f"    [+] Found 'What's New' section: {heading.get_text().strip()}")
                break
        
        if whats_new_section:
            # Get all links after the "What's New" heading until the next major heading
            seen_urls = set()
            current = whats_new_section.find_next()
            
            while current:
                # Stop at next major heading (same level or higher)
                if current.name in ['h1', 'h2', 'h3'] and current != whats_new_section:
                    break
                
                # Find all links in this element
                links = current.find_all('a', href=True) if hasattr(current, 'find_all') else []
                
                for link in links:
                    url = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Only include bundle pages, skip auth/login
                    if f'/bundle/{bundle_id}/page/' in url and '/auth/login' not in url:
                        # Construct full URL if needed
                        if not url.startswith('http'):
                            url = f"https://docs.motorolasolutions.com{url}"
                        
                        if url not in seen_urls and text:
                            seen_urls.add(url)
                            navigation_links.append({
                                'url': url,
                                'nav_text': text
                            })
                
                current = current.find_next_sibling()
        
        if not navigation_links:
            print("    [!] No links found in 'What's New' section, falling back to list items...")
            # Fallback: look for list items with links
            for li in soup.find_all('li'):
                link = li.find('a', href=True)
                if link:
                    url = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if f'/bundle/{bundle_id}/page/' in url and '/auth/login' not in url:
                        if not url.startswith('http'):
                            url = f"https://docs.motorolasolutions.com{url}"
                        
                        if url not in seen_urls and text:
                            seen_urls.add(url)
                            navigation_links.append({
                                'url': url,
                                'nav_text': text
                            })
        
        print(f"    [+] Found {len(navigation_links)} links")
        
        # Show all found links
        for i, link in enumerate(navigation_links[:10], 1):
            print(f"        {i}. {link['nav_text']}")
        if len(navigation_links) > 10:
            print(f"        ... and {len(navigation_links) - 10} more")
    
    return navigation_links


async def crawl_single_page(url: str, nav_text: str = None, max_retries: int = 2) -> Dict:
    """
    Crawl a single documentation page.
    
    Args:
        url: Page URL (may include anchor like #section-id)
        nav_text: Text from navigation link (fallback for title)
        max_retries: Number of retry attempts for failed requests
        
    Returns:
        Document dict with title, url, content, etc.
    """
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(
        page_timeout=45000,  # Increased timeout
        delay_before_return_html=3.0,  # Longer delay to avoid rate limiting
        word_count_threshold=10
    )
    
    # Retry logic for failed requests
    last_error = None
    result = None
    
    for attempt in range(max_retries + 1):
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)
            
            if result.success:
                # Extract meaningful content
                content = result.markdown.raw_markdown
                html = result.html
                
                # Check for security blocks (Incapsula, Cloudflare, etc.)
                if "Request unsuccessful" in content or "Incapsula incident ID" in content:
                    last_error = "Security block (WAF/CDN)"
                    if attempt < max_retries:
                        await asyncio.sleep(3)  # Wait before retry
                        continue
                    else:
                        return {
                            "error": True,
                            "url": url,
                            "error_message": last_error
                        }
                # Success - break out of retry loop
                break
            else:
                last_error = result.error_message
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue
    
    # If all retries failed, return error
    if not result or not result.success:
        return {
            "error": True,
            "url": url,
            "error_message": last_error or "Unknown error"
        }
    
    # Clean content - remove cookie banners, navigation, etc.
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove common noise elements
    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    # Remove cookie banners and privacy notices
    for element in soup.find_all(text=lambda text: text and ('cookie' in text.lower() or 'privacy statement' in text.lower())):
        if element.parent and len(element) > 100:  # Only remove long cookie notices
            element.parent.decompose()
    
    # Get title - use nav_text as primary since it's from "What's New"
    if nav_text:
        title = nav_text
    else:
        title = result.metadata.get('title', 'Unknown')
        if ' — ' in title:
            title = title.split(' — ')[0]
    
    # If URL has anchor, try to extract that specific section
    section_content = None
    if '#' in url:
        anchor = url.split('#')[1]
        section = soup.find(id=anchor)
        
        if section:
            # Get content from this section
            content_parts = [section.get_text(strip=True)]
            for sibling in section.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                text = sibling.get_text(strip=True)
                if text:
                    content_parts.append(text)
            
            section_content = ' '.join(content_parts)
    
    # If no section found or no anchor, extract main content area
    if not section_content:
        # Try to find main content container
        main_content = soup.find(['main', 'article']) or soup.find(class_=lambda c: c and 'content' in c.lower())
        
        if main_content:
            section_content = main_content.get_text(separator=' ', strip=True)
        else:
            # Fallback to cleaned HTML text
            section_content = soup.get_text(separator=' ', strip=True)
    
    # Final cleanup - remove excessive whitespace
    section_content = ' '.join(section_content.split())
    
    return {
        "title": title,
        "url": url,
        "nav_text": nav_text,
        "content_snippet": section_content[:1500],
        "full_content": section_content,
        "content_length": len(section_content),
        "source_type": "motorola_docs",
        "crawled_at": datetime.now().isoformat()
    }


async def crawl_documentation_bundle(toc_url: str, max_pages: int = None) -> List[Dict]:
    """
    Crawl an entire documentation bundle.
    
    Args:
        toc_url: URL of the table of contents page
        max_pages: Optional limit on number of pages to crawl
        
    Returns:
        List of document dicts
    """
    print("\n" + "=" * 70)
    print("MOTOROLA DOCUMENTATION CRAWLER")
    print("=" * 70)
    print(f"Target: {toc_url}")
    if max_pages:
        print(f"Max pages: {max_pages}")
    
    # Step 1: Extract navigation links
    nav_links = await extract_navigation_links(toc_url)
    
    if not nav_links:
        print("\n[X] No navigation links found")
        return []
    
    # Limit if requested
    if max_pages:
        nav_links = nav_links[:max_pages]
        print(f"\n[!] Limited to {len(nav_links)} pages")
    
    # Step 2: Crawl each page
    print(f"\n[+] Crawling {len(nav_links)} pages...")
    documents = []
    
    for i, link in enumerate(nav_links, 1):
        print(f"\n[{i}/{len(nav_links)}] {link['nav_text']}")
        print(f"    URL: {link['url']}")
        
        doc = await crawl_single_page(link['url'], link['nav_text'])
        
        if doc.get('error'):
            print(f"    [X] Failed: {doc.get('error_message')}")
        else:
            print(f"    [+] Success: {doc['content_length']} chars")
            documents.append(doc)
        
        # Small delay to be respectful
        await asyncio.sleep(0.5)
    
    print(f"\n[+] Successfully crawled {len(documents)}/{len(nav_links)} pages")
    return documents


async def generate_descriptions(documents: List[Dict]) -> List[Dict]:
    """
    Generate searchable descriptions for each document using LLM.
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        Same list with 'description' field added
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    
    print(f"\n[+] Generating descriptions with GPT-4o-mini...")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_template(
        """You are analyzing Motorola technical documentation.
        Generate a concise 2-3 sentence description that:
        1. Explains what this page/section covers
        2. Lists key features, procedures, or functionality described
        3. Uses terminology that users would search for (e.g., "password reset", "firmware update", "device configuration")
        
        Page Title: {title}
        Navigation Context: {nav_text}
        Content Preview: {content}
        
        Description (2-3 sentences):"""
    )
    
    for i, doc in enumerate(documents, 1):
        try:
            response = await llm.ainvoke(
                prompt.format_messages(
                    title=doc["title"],
                    nav_text=doc.get("nav_text", ""),
                    content=doc["content_snippet"]
                )
            )
            doc["description"] = response.content.strip()
            print(f"    [{i}/{len(documents)}] {doc['title'][:50]}")
            
        except Exception as e:
            print(f"    [{i}/{len(documents)}] [X] Failed: {e}")
            doc["description"] = doc["content_snippet"][:200]  # Fallback
    
    print(f"[+] Generated {len(documents)} descriptions")
    return documents


def save_documents(documents: List[Dict], filename: str = "motorola_docs.json"):
    """Save crawled documents to JSON file."""
    output_path = PROJECT_ROOT / "data" / filename
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] Saved {len(documents)} documents to: {output_path}")
    return output_path


async def main():
    """Main entry point."""
    
    # Target URL - VideoManager Admin Guide TOC
    toc_url = "https://docs.motorolasolutions.com/bundle/89303/page/23111842.html"
    
    # Crawl all pages from "What's New" section
    documents = await crawl_documentation_bundle(toc_url, max_pages=10)
    
    if not documents:
        print("\n[X] No documents crawled")
        return
    
    # Generate descriptions
    documents = await generate_descriptions(documents)
    
    # Save to file
    save_documents(documents, "motorola_docs.json")
    
    # Display summary
    print("\n" + "=" * 70)
    print("CRAWL SUMMARY")
    print("=" * 70)
    print(f"Total pages: {len(documents)}")
    print(f"\nSample entries:")
    
    for i, doc in enumerate(documents[:3], 1):
        print(f"\n{i}. {doc['title']}")
        print(f"   URL: {doc['url']}")
        print(f"   Description: {doc['description']}")
    
    print(f"\n[+] Complete! Run prototype_indexer.py to build the search index.")


if __name__ == "__main__":
    asyncio.run(main())
