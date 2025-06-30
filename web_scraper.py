import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
from datetime import datetime
import mimetypes

class WebScraper:
    def __init__(self, max_depth=2):
        self.max_depth = max_depth
        self.visited_urls = set()
        self.file_counter = 0
        self.media_counter = 0
        
        # Create unique output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_output_dir = Path(f"scraped_content_{timestamp}")
        self.output_dir = self.base_output_dir / "content"
        self.media_dir = self.base_output_dir / "media"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.html_dir = self.base_output_dir / "html_source"
        self.html_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Media extensions to download
        self.media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico',
                                '.mp4', '.webm', '.mp3', '.wav', '.pdf', '.doc', '.docx'}
    
    def get_user_urls(self):
        """Get URLs from user input"""
        urls = []
        print("=" * 60)
        print("Web Scraper with Media Collection")
        print("=" * 60)
        print("\nEnter URLs to scrape (one per line).")
        print("Press Enter twice when done, or type 'file' to load from Sources.txt\n")
        
        while True:
            url = input("URL: ").strip()
            
            if url.lower() == 'file':
                # Load from file
                return self.read_sources_file()
            
            if not url:
                if urls:
                    break
                else:
                    print("Please enter at least one URL.")
                    continue
            
            # Clean and validate URL
            if not url.startswith(('http://', 'https://')):
                if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', url):
                    url = 'https://' + url
                else:
                    print(f"Invalid URL format: {url}")
                    continue
            
            urls.append(url)
            print(f"Added: {url}")
        
        return urls
    
    def read_sources_file(self):
        """Read URLs from the sources file"""
        sources_file = "E:\\Users\\Admin\\OneDrive\\Desktop\\Sources.txt"
        urls = []
        try:
            with open(sources_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract URL from markdown-style links [text](url)
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
            print(f"Sources file not found: {sources_file}")
            return []
        
        return urls
    
    def clean_filename(self, text):
        """Clean text to be used as filename"""
        # Remove or replace invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        text = re.sub(r'\s+', '_', text)
        text = text[:100]  # Limit length
        return text
    
    def save_html_source(self, url, html_content, depth):
        """Save the raw HTML source to a text file"""
        try:
            # Generate filename based on URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('.', '_')
            path_part = self.clean_filename(parsed_url.path.replace('/', '_'))
            
            self.file_counter += 1
            filename = f"{self.file_counter:04d}_D{depth}_{domain}_{path_part}.html"
            filepath = self.html_dir / filename
            
            # Save HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Source URL: {url} -->\n")
                f.write(f"<!-- Scraped on: {time.strftime('%Y-%m-%d %H:%M:%S')} -->\n")
                f.write(f"<!-- Depth: {depth} -->\n\n")
                f.write(html_content)
            
            print(f"{'  ' * depth}Saved HTML source: {filename}")
        except Exception as e:
            print(f"{'  ' * depth}Error saving HTML source: {str(e)}")
    
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
    
    def extract_media_urls(self, soup, base_url):
        """Extract all media URLs from the page"""
        media_urls = set()
        
        # Find images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                media_urls.add(urljoin(base_url, src))
        
        # Find videos
        for video in soup.find_all(['video', 'source']):
            src = video.get('src')
            if src:
                media_urls.add(urljoin(base_url, src))
        
        # Find links to media files
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(href.lower().endswith(ext) for ext in self.media_extensions):
                media_urls.add(urljoin(base_url, href))
        
        # Find background images in style attributes
        for element in soup.find_all(style=True):
            style = element['style']
            urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
            for url in urls:
                media_urls.add(urljoin(base_url, url))
        
        return media_urls
    
    def download_media(self, url, page_url):
        """Download a media file"""
        try:
            # Skip if already downloaded
            url_hash = str(abs(hash(url)))[:8]
            
            # Get file extension
            parsed_url = urlparse(url)
            path = parsed_url.path
            ext = os.path.splitext(path)[1].lower()
            
            # If no extension, try to get from content-type
            if not ext:
                try:
                    response = requests.head(url, headers=self.headers, timeout=10)
                    content_type = response.headers.get('content-type', '')
                    ext = mimetypes.guess_extension(content_type.split(';')[0]) or ''
                except:
                    ext = ''
            
            # Generate filename
            self.media_counter += 1
            domain = urlparse(page_url).netloc.replace('.', '_')
            filename = f"{self.media_counter:04d}_{domain}_{url_hash}{ext}"
            filepath = self.media_dir / filename
            
            # Download the file
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Save the file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"{'  ' * 2}Downloaded media: {filename}")
            return str(filepath.relative_to(self.base_output_dir))
            
        except Exception as e:
            print(f"{'  ' * 2}Error downloading media {url}: {str(e)}")
            return None
    
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
            
            # Save HTML source
            self.save_html_source(url, response.text, depth)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).netloc
            
            # Extract all links from the page
            links = self.extract_links(soup, url)
            
            # Extract media URLs
            media_urls = self.extract_media_urls(soup, url)
            
            # Download media files
            downloaded_media = []
            print(f"{'  ' * depth}Found {len(media_urls)} media files")
            for media_url in list(media_urls)[:20]:  # Limit to 20 media files per page
                media_path = self.download_media(media_url, url)
                if media_path:
                    downloaded_media.append({
                        'url': media_url,
                        'local_path': media_path
                    })
            
            # Extract main content
            content = self.extract_content(soup)
            
            # Convert to markdown
            markdown_content = self.html_to_markdown(content)
            
            return {
                'title': title_text,
                'url': url,
                'content': markdown_content,
                'links': list(links),
                'media': downloaded_media,
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
                'media': [],
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
        
        # Format media section
        media_section = ""
        if data.get('media'):
            media_section = f"\n## Media Files ({len(data['media'])} downloaded)\n\n"
            for media in data['media']:
                media_section += f"- [{media['local_path']}]({media['url']})\n"
        
        markdown_content = f"""# {data['title']}

**Source URL:** {data['url']}
**Scraped on:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {'Success' if data['success'] else 'Error'}
**Depth:** {data.get('depth', 0)}

---

{data['content']}

---
{links_section}
{media_section}
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
        urls = self.get_user_urls()
        
        if not urls:
            print("No URLs provided.")
            return
        
        print(f"\nStarting scrape of {len(urls)} URLs")
        print(f"Max depth: {self.max_depth}")
        print(f"Output directory: {self.base_output_dir.absolute()}")
        print(f"  Content: {self.output_dir.name}/")
        print(f"  Media: {self.media_dir.name}/")
        print(f"  HTML Source: {self.html_dir.name}/")
        print("-" * 60)
        
        self.successful = 0
        self.failed = 0
        
        for url in urls:
            self.scrape_recursive(url, depth=0)
        
        print("-" * 60)
        print(f"\nScraping complete!")
        print(f"Successful: {self.successful}")
        print(f"Failed: {self.failed}")
        print(f"Total content files: {self.file_counter}")
        print(f"Total media files: {self.media_counter}")
        print(f"URLs visited: {len(self.visited_urls)}")
        print(f"\nOutput saved to: {self.base_output_dir.absolute()}")

if __name__ == "__main__":
    # You can adjust max_depth here (0 = only source URLs, 1 = source + their links, etc.)
    try:
        scraper = WebScraper(max_depth=1)
        scraper.run()
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
