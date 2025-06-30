import os
import re
import json
import zipfile
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class HTMLToWebstack:
    def __init__(self, html_file_path):
        self.html_file_path = Path(html_file_path)
        self.output_dir = Path("webstack_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        self.assets_dir = self.output_dir / "assets"
        self.css_dir = self.assets_dir / "css"
        self.js_dir = self.assets_dir / "js"
        self.images_dir = self.assets_dir / "images"
        
        # Create all directories
        for dir_path in [self.css_dir, self.js_dir, self.images_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # URL mappings for images
        self.image_urls = {
            "hero_bg": "https://builtbyward.store//uploads/OVERVIEW%20HOUSE/Gen4%20Create%20a%20breathtaking%20aerial%20photograph%20captured%20during%20golden%20hour,%20showcasing%20t%20a-2,%2016451831.png",
            "about_image": "https://builtbyward.store//uploads/OVERVIEW%20HOUSE/Gen4%20Elegant%20luxury%20home%20in%20Highland%20Park%20Texas%20with%20brand%20new%20roof,%20gold%20s-terracotta,%20a-2,%204589674.png",
            "mission_crew": "https://builtbyward.store//uploads/CREW%20AND%20LABOR/jalen1wa_Hispanic_Roofing_crew_of_8_or_more_smiling_in_front_of_aa32b90c-833b-461f-a8da-b2cf4abcacc9.png",
            "review_sarah": "https://builtbyward.store//uploads/CUSTOMERS/jalen1wa_White_Homeowners_smiling_in_front_of_roof_ed5a306a-08bd-4ccd-9eb9-3260769cd43f.png",
            "review_michael": "https://builtbyward.store//uploads/CUSTOMERS/jalen1wa_Black_Homeowners_smiling_in_front_of_roof_8faae7b6-02f4-4c62-b707-d78f0e5c132c.png",
            "review_jennifer": "https://builtbyward.store//uploads/CUSTOMERS/jalen1wa_Hispanic_Family_smiling_in_front_of_roof_standing_on_l_a0ea4aab-1078-479b-a87d-82b9a0ed7c6c.png"
        }
        
        # Additional pages content
        self.additional_pages = {
            "shingles.html": self.get_shingles_page(),
            "gallery.html": self.get_gallery_page(),
            "team.html": self.get_team_page()
        }
    
    def process_html(self):
        """Main processing function"""
        print("Reading HTML file...")
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract CSS and JS
        print("Extracting CSS and JavaScript...")
        css_content = self.extract_css(soup)
        js_content = self.extract_js(soup)
        
        # Update HTML with external references
        print("Updating HTML with external references...")
        updated_html = self.update_html_references(soup)
        
        # Update navigation links
        print("Fixing navigation links...")
        updated_html = self.fix_navigation_links(updated_html)
        
        # Add image URLs
        print("Adding image URLs...")
        updated_html = self.add_image_urls(updated_html)
        
        # Save files
        print("Saving files...")
        self.save_files(updated_html, css_content, js_content)
        
        # Create additional pages
        print("Creating additional pages...")
        self.create_additional_pages()
        
        # Create supporting files
        print("Creating supporting files...")
        self.create_supporting_files()
        
        # Create zip file
        print("Creating zip file...")
        self.create_zip()
        
        print(f"\nWebstack created successfully in: {self.output_dir}")
        print(f"Zip file created: webstack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
    
    def extract_css(self, soup):
        """Extract all CSS from style tags"""
        css_content = []
        style_tags = soup.find_all('style')
        
        for style in style_tags:
            css_content.append(style.string or '')
            style.decompose()
        
        return '\n\n'.join(css_content)
    
    def extract_js(self, soup):
        """Extract all JavaScript from script tags"""
        js_content = []
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.get('src'):  # Only inline scripts
                js_content.append(script.string or '')
                script.decompose()
        
        return '\n\n'.join(js_content)
    
    def update_html_references(self, soup):
        """Add external CSS and JS references to HTML"""
        # Add CSS link
        css_link = soup.new_tag('link', rel='stylesheet', href='assets/css/main.css')
        soup.head.append(css_link)
        
        # Add JS script
        js_script = soup.new_tag('script', src='assets/js/main.js')
        soup.body.append(js_script)
        
        return str(soup.prettify())
    
    def fix_navigation_links(self, html_content):
        """Fix navigation links to point to actual files"""
        replacements = [
            ('href="#gallery"', 'href="gallery.html"'),
            ('href="#team"', 'href="team.html"'),
            ('href="shingles.html"', 'href="shingles.html"'),
            ('href="team.html"', 'href="team.html"'),
            ('href="index.html"', 'href="index.html"'),
        ]
        
        for old, new in replacements:
            html_content = html_content.replace(old, new)
        
        return html_content
    
    def add_image_urls(self, html_content):
        """Add actual image URLs to replace placeholders"""
        # Update hero background
        html_content = html_content.replace(
            "url('data:image/svg+xml;utf8,<svg",
            f"url('{self.image_urls['hero_bg']}'), url('data:image/svg+xml;utf8,<svg"
        )
        
        # Update about section image
        html_content = html_content.replace(
            'background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.2) 100%),',
            f'background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.2) 100%), url("{self.image_urls["about_image"]}") center/cover,'
        )
        
        # Add review avatars
        review_updates = [
            ("Sarah Johnson", self.image_urls["review_sarah"]),
            ("Michael Davis", self.image_urls["review_michael"]),
            ("Jennifer Martinez", self.image_urls["review_jennifer"])
        ]
        
        for name, url in review_updates:
            pattern = f'<strong>{name}</strong>'
            replacement = f'<img src="{url}" alt="{name}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; margin-right: 15px; vertical-align: middle;"><strong>{name}</strong>'
            html_content = html_content.replace(pattern, replacement)
        
        return html_content
    
    def save_files(self, html_content, css_content, js_content):
        """Save all files to output directory"""
        # Save index.html
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save CSS with image URL updates
        css_with_images = self.update_css_with_images(css_content)
        with open(self.css_dir / "main.css", 'w', encoding='utf-8') as f:
            f.write(css_with_images)
        
        # Save JS
        with open(self.js_dir / "main.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def update_css_with_images(self, css_content):
        """Update CSS with actual image URLs"""
        # Update hero background in CSS
        css_content = re.sub(
            r'\.hero\s*{[^}]*background:[^;]*;',
            lambda m: m.group(0).replace(
                "background:",
                f"background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.3)), url('{self.image_urls['hero_bg']}') center/cover,"
            ),
            css_content,
            flags=re.DOTALL
        )
        
        return css_content
    
    def create_additional_pages(self):
        """Create shingles.html, gallery.html, and team.html"""
        for filename, content in self.additional_pages.items():
            # Extract CSS and JS from each page
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove style and script tags (already in main.css/js)
            for tag in soup.find_all(['style', 'script']):
                if not tag.get('src'):
                    tag.decompose()
            
            # Add external references
            css_link = soup.new_tag('link', rel='stylesheet', href='assets/css/main.css')
            soup.head.append(css_link)
            
            js_script = soup.new_tag('script', src='assets/js/main.js')
            soup.body.append(js_script)
            
            # Fix navigation links
            updated_content = self.fix_navigation_links(str(soup.prettify()))
            
            # Save file
            with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
                f.write(updated_content)
    
    def create_supporting_files(self):
        """Create robots.txt, sitemap.xml, .htaccess, and 404.html"""
        # robots.txt
        robots_content = """User-agent: *
Allow: /
Disallow: /assets/
Sitemap: https://goldennailroofing.com/sitemap.xml"""
        
        with open(self.output_dir / "robots.txt", 'w') as f:
            f.write(robots_content)
        
        # sitemap.xml
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://goldennailroofing.com/</loc>
    <lastmod>2024-01-01</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://goldennailroofing.com/shingles.html</loc>
    <lastmod>2024-01-01</lastmod>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://goldennailroofing.com/gallery.html</loc>
    <lastmod>2024-01-01</lastmod>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://goldennailroofing.com/team.html</loc>
    <lastmod>2024-01-01</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>"""
        
        with open(self.output_dir / "sitemap.xml", 'w') as f:
            f.write(sitemap_content)
        
        # .htaccess
        htaccess_content = """# Enable compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/javascript application/javascript
</IfModule>

# Browser caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>

# Custom 404 page
ErrorDocument 404 /404.html

# Remove .html extension
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^([^\\.]+)$ $1.html [NC,L]"""
        
        with open(self.output_dir / ".htaccess", 'w') as f:
            f.write(htaccess_content)
        
        # 404.html
        error_404_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | Golden Nail Roofing</title>
    <link rel="stylesheet" href="/assets/css/main.css">
</head>
<body>
    <div style="text-align: center; padding: 100px 20px;">
        <h1 style="color: #d4af37; font-size: 72px; margin-bottom: 20px;">404</h1>
        <h2>Page Not Found</h2>
        <p style="margin: 20px 0;">The page you're looking for doesn't exist.</p>
        <a href="/" style="color: #d4af37; text-decoration: none; font-weight: bold;">Return to Homepage</a>
    </div>
</body>
</html>"""
        
        with open(self.output_dir / "404.html", 'w') as f:
            f.write(error_404_content)
    
    def create_zip(self):
        """Create a zip file of the entire webstack"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"webstack_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.output_dir.parent)
                    zipf.write(file_path, arcname)
    
    def get_shingles_page(self):
        """Return the shingles.html content with proper image URLs"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Shingle Collection - Golden Nail Roofing</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        /* Shingle-specific styles */
        .shingle-hero {
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.3)),
                        url('https://builtbyward.store//uploads/SHINGLES/Photoshay_Brown_Shingle_Backdrop.jpg') center/cover;
        }
        .heritage { 
            background: url('https://builtbyward.store//uploads/SHINGLES/TAMKO_Brown_Grey_Layered_Shingles.jpg') center/cover;
        }
        .prestige { 
            background: url('https://builtbyward.store//uploads/SHINGLES/Charcoal_Grey_Shingles.jpg') center/cover;
        }
        .artisan { 
            background: url('https://builtbyward.store//uploads/SHINGLES/TAMKO_Brown_Red_Rustic_Shingles.jpg') center/cover;
        }
        .storm { 
            background: url('https://builtbyward.store//uploads/SHINGLES/Dark-Grey_Black_Shingles.jpg') center/cover;
        }
        .eco { 
            background: url('https://builtbyward.store//uploads/SHINGLES/TAMKO_Brown_with_Blue_Grey_Accents_Shingles.jpg') center/cover;
        }
        .royal { 
            background: url('https://builtbyward.store//uploads/SHINGLES/Deep_Black_Shingles.jpg') center/cover;
        }
    </style>
</head>
<body>
    <!-- Shingles page content here -->
</body>
</html>"""
    
    def get_gallery_page(self):
        """Return the gallery.html content with proper image URLs"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Gallery - Golden Nail Roofing</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        /* Gallery-specific styles */
        .hero-banner {
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)),
                        url('https://builtbyward.store//uploads/OVERVIEW%20HOUSE/jalen1wa_IMAGINE_a_slow_pan_shot_focusing_on_a_grand_historic_7c408e9a-b796-4455-bf28-843679811784_2.png') center/cover;
        }
        .thumbnail-1 { 
            background: url('https://builtbyward.store//uploads/OVERVIEW%20HOUSE/Gen4%20Elegant%20luxury%20home%20in%20Highland%20Park%20Texas%20with%20brand%20new%20roof,%20gold%20s-terracotta,%20a-2,%204589674.png') center/cover;
        }
        .thumbnail-2 { 
            background: url('https://builtbyward.store//uploads/OVERVIEW%20HOUSE/0022_www_tamko_com_81547798.jpg') center/cover;
        }
        .thumbnail-3 { 
            background: url('https://builtbyward.store//uploads/OVERVIEW%20HOUSE/jalen1wa_Historical_Asphalt_shingle_roof_Brand_New_2ca024b7-a63c-4d55-8ac4-f7e49ae6be12.png') center/cover;
        }
        .thumbnail-4 { 
            background: url('https://builtbyward.store//uploads/OVERVIEW%20HOUSE/0054_www_tamko_com_70969628.jpg') center/cover;
        }
        .thumbnail-5 { 
            background: url('https://builtbyward.store//uploads/OVERVIEW%20HOUSE/jalen1wa_IMAGINE_a_wide-angle_shot_of_a_historic_neighborhood_577d7b24-1cfc-4ae3-9b9d-11cefd3bbd9a_1.png') center/cover;
        }
        .thumbnail-6 { 
            background: url('https://builtbyward.store//uploads/CUSTOMERS/Gen4%20Happy%20homeowner%20shaking%20hands%20with%20roofing%20foreman%20in%20front%20of%20completed%20s-terracotta,%2020510950.png') center/cover;
        }
    </style>
</head>
<body>
    <!-- Gallery page content here -->
</body>
</html>"""
    
    def get_team_page(self):
        """Return the team.html content with proper image URLs"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meet the Team - Golden Nail Roofing</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        /* Team-specific styles */
        .team-hero {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%),
                        url('https://builtbyward.store//uploads/CREW%20AND%20LABOR/jalen1wa_Hispanic_Roofing_crew_of_8_or_more_smiling_in_front_of_30dacb03-c917-47ba-89f8-6b3e995dc53c.png') center/cover;
            background-blend-mode: overlay;
        }
    </style>
</head>
<body>
    <!-- Team page content here -->
</body>
</html>"""


def main():
    """Main function to run the HTML to webstack converter"""
    html_file = r"E:\Users\Admin\OneDrive\Desktop\GOLDEN NAILNEW.html"
    
    if not Path(html_file).exists():
        print(f"Error: HTML file not found at {html_file}")
        return
    
    converter = HTMLToWebstack(html_file)
    converter.process_html()


if __name__ == "__main__":
    main()
