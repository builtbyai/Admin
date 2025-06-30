import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse, unquote
import time
from pathlib import Path
from datetime import datetime
import json

class VideoScraper:
    def __init__(self, max_depth=2):
        self.max_depth = max_depth
        self.visited_urls = set()
        self.found_videos = []
        
        # Create unique output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"video_links_{timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Video extensions to search for
        self.video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.m3u8', '.webm', '.mpg', '.mpeg'}
        
        # Common video URL patterns - expanded for better detection
        self.video_patterns = [
            # Direct video file URLs
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm|mpg|mpeg|3gp|ogv)',
            # Video URLs with query parameters
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)\?[^\s<>"{}|\\^`\[\]]*',
            # Common video paths
            r'https?://[^\s<>"{}|\\^`\[\]]+/video/[^\s<>"{}|\\^`\[\]]+',
            r'https?://[^\s<>"{}|\\^`\[\]]+/stream/[^\s<>"{}|\\^`\[\]]+',
            r'https?://[^\s<>"{}|\\^`\[\]]+/media/[^\s<>"{}|\\^`\[\]]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)',
            r'https?://[^\s<>"{}|\\^`\[\]]+/content/[^\s<>"{}|\\^`\[\]]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)',
            # M3U8 streaming
            r'https?://[^\s<>"{}|\\^`\[\]]+\.m3u8[^\s<>"{}|\\^`\[\]]*',
            # Blob URLs
            r'blob:https?://[^\s<>"{}|\\^`\[\]]+',
            # CDN patterns
            r'https?://[^\s<>"{}|\\^`\[\]]+\.cloudfront\.net/[^\s<>"{}|\\^`\[\]]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)',
            r'https?://[^\s<>"{}|\\^`\[\]]+\.amazonaws\.com/[^\s<>"{}|\\^`\[\]]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)',
        ]
    
    def get_user_urls(self):
        """Get URLs from user input"""
        urls = []
        print("=" * 60)
        print("Video Link Scraper")
        print("=" * 60)
        print("\nThis tool will search for video files and streaming links:")
        print("Supported formats: .MP4, .MOV, .AVI, .MKV, .WMV, .FLV, .M3U8, etc.")
        print("\nEnter URLs to scan (one per line).")
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
                            url = markdown_match.group(1)
                            urls.append(url)
                        elif line.startswith(('http://', 'https://')):
                            urls.append(line)
                        elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line):
                            urls.append('https://' + line)
        except FileNotFoundError:
            print(f"Sources file not found: {sources_file}")
        
        return urls
    
    def extract_video_urls_from_html(self, html_content, base_url):
        """Extract video URLs from HTML content"""
        video_urls = set()
        
        # Search in HTML attributes
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for video tags
        for video in soup.find_all(['video', 'source']):
            # Check multiple attributes
            for attr in ['src', 'data-src', 'data-source', 'data-video-src']:
                src = video.get(attr)
                if src:
                    video_urls.add(urljoin(base_url, src))
        
        # Look for links to video files
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(ext in href.lower() for ext in self.video_extensions):
                video_urls.add(urljoin(base_url, href))
        
        # Look for iframes (might contain video players)
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and any(provider in src.lower() for provider in ['youtube', 'vimeo', 'dailymotion', 'video', 'player', 'embed']):
                video_urls.add(urljoin(base_url, src))
        
        # Search in JavaScript content
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for video URLs in JavaScript
                for pattern in self.video_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        video_urls.add(match)
                
                # Look for JSON objects containing video URLs
                json_pattern = r'\{[^{}]*"(?:url|src|source|video|file|stream)"[^{}]*:[^{}]*"([^"]+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)[^"]*)"[^{}]*\}'
                json_matches = re.findall(json_pattern, script.string, re.IGNORECASE)
                for match in json_matches:
                    video_urls.add(urljoin(base_url, match))
        
        # Search in all data attributes
        for element in soup.find_all(True):  # All elements
            for attr, value in element.attrs.items():
                if isinstance(value, str):
                    # Check if attribute name suggests video
                    if any(keyword in attr.lower() for keyword in ['video', 'media', 'src', 'source', 'file', 'url']):
                        if any(ext in value.lower() for ext in self.video_extensions):
                            video_urls.add(urljoin(base_url, value))
                    
                    # Also check attribute values for video URLs
                    for pattern in self.video_patterns:
                        matches = re.findall(pattern, value, re.IGNORECASE)
                        for match in matches:
                            video_urls.add(match)
        
        # Look for meta tags with video content
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if any(ext in content.lower() for ext in self.video_extensions):
                video_urls.add(urljoin(base_url, content))
        
        # Search in style attributes for background videos
        for element in soup.find_all(style=True):
            style = element['style']
            for pattern in self.video_patterns:
                matches = re.findall(pattern, style, re.IGNORECASE)
                for match in matches:
                    video_urls.add(match)
        
        return video_urls
    
    def extract_video_urls_from_text(self, text):
        """Extract video URLs from plain text using regex"""
        video_urls = set()
        
        # Apply each video pattern
        for pattern in self.video_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            video_urls.update(matches)
        
        # Look for URLs in quotes (single or double)
        quoted_url_pattern = r'["\']([^"\']+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)[^"\']*)["\']'
        quoted_matches = re.findall(quoted_url_pattern, text, re.IGNORECASE)
        video_urls.update(quoted_matches)
        
        # Look for URLs in JSON-style strings
        json_url_pattern = r'["\']\s*:\s*["\']([^"\']+\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)[^"\']*)["\']'
        json_matches = re.findall(json_url_pattern, text, re.IGNORECASE)
        video_urls.update(json_matches)
        
        # Look for base64 encoded URLs (sometimes used for video sources)
        base64_pattern = r'data:video/[^;]+;base64,[A-Za-z0-9+/=]+'
        base64_matches = re.findall(base64_pattern, text)
        video_urls.update(base64_matches)
        
        # Also look for any URL ending with video extensions
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        all_urls = re.findall(url_pattern, text)
        for url in all_urls:
            if any(ext in url.lower() for ext in self.video_extensions):
                video_urls.add(url)
        
        # Look for relative paths to video files
        relative_pattern = r'["\']([^"\']*\.(?:mp4|mov|avi|mkv|wmv|flv|m3u8|webm)[^"\']*)["\']'
        relative_matches = re.findall(relative_pattern, text, re.IGNORECASE)
        for match in relative_matches:
            if not match.startswith(('http://', 'https://', 'data:')):
                video_urls.add(match)  # Will be converted to absolute URL later
        
        return video_urls
    
    def scrape_url(self, url, depth=0):
        """Scrape a single URL for video links"""
        try:
            # Skip if already visited
            if url in self.visited_urls:
                return None
            
            print(f"{'  ' * depth}Scanning: {url}")
            self.visited_urls.add(url)
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Get the content
            content = response.text
            
            # Extract video URLs from HTML
            video_urls = self.extract_video_urls_from_html(content, url)
            
            # Also extract from raw text (catches things BeautifulSoup might miss)
            text_videos = self.extract_video_urls_from_text(content)
            video_urls.update(text_videos)
            
            # Clean and validate URLs
            cleaned_urls = set()
            for video_url in video_urls:
                # Skip data URLs and blob URLs for now
                if video_url.startswith(('data:', 'blob:')):
                    cleaned_urls.add(video_url)
                    continue
                
                # Convert relative URLs to absolute
                if not video_url.startswith(('http://', 'https://')):
                    video_url = urljoin(url, video_url)
                
                # Validate URL
                try:
                    parsed = urlparse(video_url)
                    if parsed.scheme in ['http', 'https']:
                        cleaned_urls.add(video_url)
                except:
                    pass
            
            video_urls = cleaned_urls
            
            # Parse page for more links to follow
            soup = BeautifulSoup(content, 'html.parser')
            page_links = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                parsed = urlparse(absolute_url)
                if parsed.scheme in ['http', 'https'] and parsed.netloc:
                    page_links.add(absolute_url)
            
            # Store found videos
            for video_url in video_urls:
                # Check if we've already found this video
                if not any(v['url'] == video_url for v in self.found_videos):
                    # Determine video type
                    video_type = 'unknown'
                    if video_url.startswith('data:'):
                        video_type = 'base64'
                    elif video_url.startswith('blob:'):
                        video_type = 'blob'
                    elif '.m3u8' in video_url.lower():
                        video_type = 'streaming'
                    else:
                        for ext in self.video_extensions:
                            if ext in video_url.lower():
                                video_type = ext[1:]  # Remove the dot
                                break
                    
                    video_info = {
                        'url': video_url,
                        'found_on': url,
                        'depth': depth,
                        'type': video_type,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.found_videos.append(video_info)
                    print(f"{'  ' * (depth + 1)}Found {video_type} video: {video_url[:100]}...")
            
            return {
                'url': url,
                'video_count': len(video_urls),
                'links': list(page_links),
                'success': True
            }
            
        except Exception as e:
            print(f"{'  ' * depth}Error scanning {url}: {str(e)}")
            return {
                'url': url,
                'video_count': 0,
                'links': [],
                'success': False
            }
    
    def scrape_recursive(self, url, depth=0):
        """Recursively scrape URL and its links"""
        if depth > self.max_depth:
            return
        
        # Scrape the current URL
        result = self.scrape_url(url, depth)
        if not result:
            return
        
        # Be respectful - add delay
        time.sleep(1)
        
        # Recursively scrape links if we haven't reached max depth
        if depth < self.max_depth and result.get('success') and result.get('links'):
            # Limit number of links to follow
            links_to_follow = result['links'][:20]
            
            for link in links_to_follow:
                # Only follow links from the same domain
                if urlparse(link).netloc == urlparse(url).netloc:
                    self.scrape_recursive(link, depth + 1)
    
    def save_results(self):
        """Save found video URLs to files"""
        # Save as JSON
        json_file = self.output_dir / 'video_links.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.found_videos, f, indent=2)
        
        # Save as text file
        txt_file = self.output_dir / 'video_links.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Video Links Found - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Group by source page
            by_source = {}
            for video in self.found_videos:
                source = video['found_on']
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(video['url'])
            
            for source, videos in by_source.items():
                f.write(f"\nSource: {source}\n")
                f.write("-" * 40 + "\n")
                for video_url in videos:
                    f.write(f"{video_url}\n")
        
        # Save as CSV
        csv_file = self.output_dir / 'video_links.csv'
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("Video URL,Found On,Type,Depth,Timestamp\n")
            for video in self.found_videos:
                f.write(f'"{video["url"]}","{video["found_on"]}",{video.get("type", "unknown")},{video["depth"]},{video["timestamp"]}\n')
        
        # Save summary
        summary_file = self.output_dir / 'summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Video Scraping Summary - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total videos found: {len(self.found_videos)}\n")
            f.write(f"URLs scanned: {len(self.visited_urls)}\n\n")
            
            # Count by type
            type_counts = {}
            for video in self.found_videos:
                vtype = video.get('type', 'unknown')
                type_counts[vtype] = type_counts.get(vtype, 0) + 1
            
            f.write("Videos by type:\n")
            for vtype, count in sorted(type_counts.items()):
                f.write(f"  {vtype}: {count}\n")
        
        print(f"\nResults saved to: {self.output_dir.absolute()}")
    
    def run(self):
        """Main scraping process"""
        urls = self.get_user_urls()
        
        if not urls:
            print("No URLs provided.")
            return
        
        print(f"\nStarting video scan of {len(urls)} URLs")
        print(f"Max depth: {self.max_depth}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print("-" * 60)
        
        for url in urls:
            self.scrape_recursive(url, depth=0)
        
        print("-" * 60)
        print(f"\nScan complete!")
        print(f"Total video links found: {len(self.found_videos)}")
        print(f"URLs scanned: {len(self.visited_urls)}")
        
        if self.found_videos:
            self.save_results()
        else:
            print("No video links were found.")

if __name__ == "__main__":
    try:
        scraper = VideoScraper(max_depth=1)
        scraper.run()
    except KeyboardInterrupt:
        print("\n\nScanning interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
