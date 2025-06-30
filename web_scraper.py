import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path

class WebScraper:
    def __init__(self, sources_file="E:\\Users\\Admin\\OneDrive\\Desktop\\Sources.txt", max_depth=2):
        self.sources_file = sources_file
        self.output_dir = Path("scraped_content")
        self.output_dir.mkdir(exist_ok=True)
        self.max_depth = max_depth
        self.visited_urls = set()
        self.file_counter = 0
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def read_sources(self):
        """Read URLs from the sources file"""
        urls = []
        try:
            with open(self.sources_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract URL from markdown-style links [text](url)
                        import re
                        markdown_link_pattern = r'\[.*?\]\((https?://[^\)]+)\)'
                        markdown_match = re.search(markdown_link_pattern, line)
                        
                        if markdown_match:
                            # Extract URL from markdown link
                            url = markdown_match.group(1)
                            urls.append(url)
                        elif line.startswith(('http://', 'https://')):
                            # Already a proper URL
                            urls.append(line)
                        elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line):
                            # Looks like a domain name without protocol
                            urls.append('https://' + line)
                        else:
                            # Skip lines that don't look like URLs
                            print(f"Skipping non-URL line: {line[:50]}...")
                            continue
        except FileNotFoundError:
            print(f"Sources file not found: {self.sources_file}")
            return []
        
        return urls
    
    def clean_filename(self, text):
        """Clean text to be used as filename"""
        # Remove or replace invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        text = re.sub(r'\s+', '_', text)
        text = text[:100]  # Limit length
        return text
    
    def extract_content(self, soup):
        """Extract main content from the webpage"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '.container'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        # If no specific content area found, use body
        if not content:
            content = soup.find('body')
        
        return content
    
    def html_to_markdown(self, content):
        """Convert HTML content to markdown"""
        if not content:
            return ""
        
        markdown = ""
        
        # Process different HTML elements
        for element in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(element.name[1])
            markdown += f"\n{'#' * level} {element.get_text().strip()}\n\n"
        
        for element in content.find_all('p'):
            text = element.get_text().strip()
            if text:
                markdown += f"{text}\n\n"
        
        for element in content.find_all(['ul', 'ol']):
            for li in element.find_all('li'):
                text = li.get_text().strip()
                if text:
                    markdown += f"- {text}\n"
            markdown += "\n"
        
        for element in content.find_all('a'):
            text = element.get_text().strip()
            href = element.get('href', '')
            if text and href:
                markdown += f"[{text}]({href})\n"
        
        for element in content.find_all(['strong', 'b']):
            text = element.get_text().strip()
            if text:
                markdown += f"**{text}**\n"
        
        for element in content.find_all(['em', 'i']):
            text = element.get_text().strip()
            if text:
                markdown += f"*{text}*\n"
        
        for element in content.find_all('code'):
            text = element.get_text().strip()
            if text:
                markdown += f"`{text}`\n"
        
        for element in content.find_all('pre'):
            text = element.get_text().strip()
            if text:
                markdown += f"```\n{text}\n```\n\n"
        
        # If no specific elements found, just get all text
        if not markdown.strip():
            markdown = content.get_text()
        
        return markdown
    
    def extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Parse the URL
            parsed = urlparse(absolute_url)
            
            # Filter out non-HTTP(S) links and anchors
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                # Remove fragment (anchor) from URL
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                links.add(clean_url)
        
        return links
    
    def scrape_url(self, url, depth=0):
        """Scrape a single URL and return content with links"""
        try:
            # Clean up the URL
            url = url.strip()
            
            # Skip if already visited
            if url in self.visited_urls:
                return None
            
            # Validate URL format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                print(f"Invalid URL format: {url}")
                return {
                    'title': 'Invalid URL',
                    'url': url,
                    'content': f"Invalid URL format: {url}",
                    'links': [],
                    'success': False
                }
            
            print(f"{'  ' * depth}Scraping: {url}")
            self.visited_urls.add(url)
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).netloc
            
            # Extract all links from the page
            links = self.extract_links(soup, url)
            
            # Extract main content
            content = self.extract_content(soup)
            
            # Convert to markdown
            markdown_content = self.html_to_markdown(content)
            
            return {
                'title': title_text,
                'url': url,
                'content': markdown_content,
                'links': list(links),
                'success': True,
                'depth': depth
            }
            
        except Exception as e:
            print(f"{'  ' * depth}Error scraping {url}: {str(e)}")
            try:
                title = urlparse(url).netloc
            except:
                title = 'Error'
            return {
                'title': title,
                'url': url,
                'content': f"Error scraping content: {str(e)}",
                'links': [],
                'success': False,
                'depth': depth
            }
    
    def save_markdown(self, data):
        """Save scraped data as markdown file"""
        self.file_counter += 1
        depth_prefix = f"D{data.get('depth', 0)}_"
        filename = f"{self.file_counter:04d}_{depth_prefix}{self.clean_filename(data['title'])}.md"
        filepath = self.output_dir / filename
        
        # Format links section
        links_section = ""
        if data.get('links'):
            links_section = f"\n## Links Found ({len(data['links'])} total)\n\n"
            for link in data['links'][:50]:  # Limit to first 50 links
                links_section += f"- {link}\n"
            if len(data['links']) > 50:
                links_section += f"\n... and {len(data['links']) - 50} more links\n"
        
        markdown_content = f"""# {data['title']}

**Source URL:** {data['url']}
**Scraped on:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {'Success' if data['success'] else 'Error'}
**Depth:** {data.get('depth', 0)}

---

{data['content']}

---
{links_section}
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Saved: {filepath}")
            return True
        except Exception as e:
            print(f"Error saving {filepath}: {str(e)}")
            return False
    
    def scrape_recursive(self, url, depth=0):
        """Recursively scrape URL and its links up to max_depth"""
        if depth > self.max_depth:
            return
        
        # Scrape the current URL
        data = self.scrape_url(url, depth)
        if not data:
            return
        
        # Save the scraped content
        if self.save_markdown(data):
            if data['success']:
                self.successful += 1
            else:
                self.failed += 1
        else:
            self.failed += 1
        
        # Be respectful - add delay between requests
        time.sleep(2)
        
        # Recursively scrape links if we haven't reached max depth
        if depth < self.max_depth and data.get('success') and data.get('links'):
            print(f"{'  ' * depth}Found {len(data['links'])} links at depth {depth}")
            
            # Limit number of links to follow per page
            links_to_follow = data['links'][:10]  # Follow max 10 links per page
            
            for link in links_to_follow:
                # Only follow links from the same domain or if depth is 0
                if depth == 0 or urlparse(link).netloc == urlparse(url).netloc:
                    self.scrape_recursive(link, depth + 1)
    
    def run(self):
        """Main scraping process"""
        urls = self.read_sources()
        
        if not urls:
            print("No URLs found in sources file.")
            return
        
        print(f"Found {len(urls)} URLs to scrape")
        print(f"Max depth: {self.max_depth}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print("-" * 50)
        
        self.successful = 0
        self.failed = 0
        
        for url in urls:
            self.scrape_recursive(url, depth=0)
        
        print("-" * 50)
        print(f"\nScraping complete!")
        print(f"Successful: {self.successful}")
        print(f"Failed: {self.failed}")
        print(f"Total files: {self.file_counter}")
        print(f"URLs visited: {len(self.visited_urls)}")

if __name__ == "__main__":
    # You can adjust max_depth here (0 = only source URLs, 1 = source + their links, etc.)
    scraper = WebScraper(max_depth=1)
    scraper.run()
