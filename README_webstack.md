# HTML to Webstack Converter

This tool converts the Golden Nail Roofing HTML file into a complete, production-ready webstack with proper file structure, external CSS/JS, and all image URLs properly integrated.

## Features

- Extracts inline CSS and JavaScript to external files
- Creates proper file hierarchy with assets directory
- Fixes navigation links to work across multiple pages
- Integrates all provided image URLs from builtbyward.store
- Creates additional pages (shingles.html, gallery.html, team.html)
- Generates supporting files (robots.txt, sitemap.xml, .htaccess, 404.html)
- Packages everything into a zip file

## Requirements

- Python 3.6 or higher
- BeautifulSoup4
- lxml

## Installation

1. Install Python from https://www.python.org/
2. Install required packages:
   ```
   pip install -r requirements_webstack.txt
   ```

## Usage

1. Make sure the HTML file is at: `E:\Users\Admin\OneDrive\Desktop\GOLDEN NAILNEW.html`
2. Run the batch file:
   ```
   run_html_to_webstack.bat
   ```
   Or run the Python script directly:
   ```
   python html_to_webstack.py
   ```

## Output

The script creates:
- `webstack_output/` directory with the complete website structure
- `webstack_[timestamp].zip` file containing the entire webstack

## File Structure

```
webstack_output/
├── index.html
├── shingles.html
├── gallery.html
├── team.html
├── assets/
│   ├── css/
│   │   └── main.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── robots.txt
├── sitemap.xml
├── .htaccess
└── 404.html
```

## Image URLs Used

All images are hosted externally on builtbyward.store and are integrated directly into the HTML/CSS. No images are downloaded locally.

### Homepage Images
- Hero background: Golden hour aerial photograph
- About section: Luxury home in Highland Park
- Mission section: Roofing crew photo
- Customer reviews: Individual customer photos

### Shingles Page Images
- Hero: Brown shingle backdrop
- Product cards: Various shingle textures and colors

### Gallery Page Images
- Hero: Historic neighborhood shot
- Project thumbnails: Various completed projects

### Team Page Images
- Hero: Full crew photo
- Team member photos: Individual professional shots

## Customization

To change image URLs or add new ones, edit the `image_urls` dictionary in `html_to_webstack.py`.

## Deployment

1. Upload the contents of `webstack_output/` to your web server
2. Ensure your server supports .htaccess files (Apache)
3. Update the domain in sitemap.xml to match your actual domain
4. Test all pages and navigation links

## SEO Considerations

The generated site includes:
- Proper meta tags structure
- Sitemap for search engines
- Clean URL structure (removes .html extensions)
- Optimized image loading

## Performance Tips

1. Consider using a CDN for the external images
2. Enable gzip compression on your server
3. Implement lazy loading for images
4. Minify CSS and JS files for production

## Support

For issues or questions, please check:
1. That the HTML file path is correct
2. Python and required packages are installed
3. You have write permissions in the current directory
