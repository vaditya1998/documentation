import os
import markdown
import re
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

# Define the custom order you want in the sidebar.
# Titles here must match exactly the 'page_title' from your Markdown files.
CUSTOM_ORDER = [
    "Home",
    "Quick-start-‐-Demo-install",
    "Production-Install",
    "i2b2-Upgrade",
    "i2b2-Admin-Module"
]

def fix_link(match):
    """
    Fixes relative links in the final HTML by appending .html if needed.
    """
    url = match.group(1)
    if url.startswith(("http://", "https://", "mailto:")):
        return match.group(0)
    if url in ['./', '.']:
        return 'href="./index.html"'
    if url.endswith('.html'):
        return match.group(0)
    if url.endswith('.md'):
        url = url[:-3]
    return f'href="{url}.html"'

def parse_headings(html_content):
    """
    Parse the HTML and return a list of (heading_level, heading_text, heading_id).
    Only for H1 and H2 in this example.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = []
    for tag in soup.find_all(['h1','h2']):
        level = int(tag.name[1])  # 1 or 2
        # Generate or extract ID
        if not tag.has_attr('id'):
            heading_id = re.sub(r'\s+', '-', tag.get_text().strip().lower())
            tag['id'] = heading_id
        else:
            heading_id = tag['id']
        headings.append((level, tag.get_text().strip(), heading_id))
    return str(soup), headings

def wrap_h2_collapsible(html_content):
    """
    Post-process the HTML so that each H2 heading becomes an "expand/collapse" section.
    - Insert a toggle button into each H2.
    - Wrap the content following that H2 (until the next H2) in a <div class="collapsible-section">.
    - By default, the collapsible sections are hidden (display:none).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    container = soup.new_tag('div')
    current_section = None

    for element in soup.contents:
        # If we hit an H2
        if element.name == 'h2':
            # Close out the previous section if it exists
            if current_section is not None:
                container.append(current_section)
                current_section = None
            
            # Insert a toggle button at the start of the H2
            toggle_btn = soup.new_tag('button', **{'class': 'h2-toggle'})
            toggle_btn.string = '+'
            element.insert(0, toggle_btn)
            
            # Add the H2 to the container
            container.append(element)
            
            # Start a new collapsible section for subsequent content
            current_section = soup.new_tag('div', **{
                'class': 'collapsible-section',
                'style': 'display:none;'
            })
        else:
            # If we're currently in a section, put this element inside it
            if current_section is not None:
                current_section.append(element)
            else:
                container.append(element)

    # If there's a trailing section at the end, close it
    if current_section is not None:
        container.append(current_section)

    return str(container)

def build_site_map(readme_dir):
    """
    Reads each file in readme_dir, converts to HTML, extracts H1/H2 headings,
    and builds a data structure with:
        site_map = [
          {
            "filename": "page1.md",
            "page_title": "Page1", 
            "html_name": "page1.html",
            "headings": [
              { "level": 1, "text": "...", "id": "..."},
              { "level": 2, "text": "...", "id": "..."}
            ],
            "html_content": "<p>...</p>"
          },
          ...
        ]
    """
    site_map = []
    for filename in os.listdir(readme_dir):
        if filename.lower().endswith((".md", ".readme")):
            filepath = os.path.join(readme_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 1) Convert to HTML
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite', 'tables'])
            
            # 2) Parse headings (H1/H2) and ensure they have IDs
            html_content, headings = parse_headings(html_content)
            
            # 3) Fix relative links
            html_content = re.sub(r'href="([^"]+)"', fix_link, html_content)
            
            # 4) Wrap H2 sections in collapsible containers
            html_content = wrap_h2_collapsible(html_content)
            
            # Derive a "page title" from the filename
            page_title = os.path.splitext(filename)[0]

            site_map.append({
                "filename": filename,
                "page_title": page_title,
                "html_name": page_title + ".html",
                "headings": [
                    {"level": lvl, "text": txt, "id": hid}
                    for (lvl, txt, hid) in headings
                ],
                "html_content": html_content
            })
    return site_map

def build_sidebar(site_map):
    """
    Builds an expandable/collapsible sidebar for the entire site:
      - Each page is a top-level item
      - Expanding a page shows its H1 headings
      - Expanding an H1 shows its H2 headings
    Returns HTML for the sidebar.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup("", 'html.parser')
    root_ul = soup.new_tag('ul', **{'class': 'sidebar-root'})

    for page in site_map:
        li_page = soup.new_tag('li', **{'class': 'sidebar-page'})
        if page["headings"]:
            toggle_page = soup.new_tag('span', **{'class': 'sidebar-toggle'})
            toggle_page.string = '+ '
            li_page.append(toggle_page)
        # Link to page root
        a_page = soup.new_tag('a', href=page["html_name"])
        a_page.string = page["page_title"]
        li_page.append(a_page)

        # Create UL for page's H1 headings
        ul_h1 = soup.new_tag('ul', **{'class': 'h1-list', 'style': 'display:none;'})
        h1_list = [h for h in page["headings"] if h["level"] == 1]
        for h1_item in h1_list:
            li_h1 = soup.new_tag('li', **{'class': 'sidebar-h1'})
            # If there are H2 under this H1, create a toggle
            h2_list = [h for h in page["headings"] if h["level"] == 2]

            if h2_list:
                toggle_h1 = soup.new_tag('span', **{'class': 'sidebar-toggle'})
                toggle_h1.string = '+ '
                li_h1.append(toggle_h1)
            # Link for H1
            a_h1 = soup.new_tag('a', href=f"{page['html_name']}#{h1_item['id']}")
            a_h1.string = h1_item["text"]
            li_h1.append(a_h1)

            # Create UL for H2
            ul_h2 = soup.new_tag('ul', **{'class': 'h2-list', 'style': 'display:none;'})
            for h2_item in h2_list:
                li_h2 = soup.new_tag('li', **{'class': 'sidebar-h2'})
                a_h2 = soup.new_tag('a', href=f"{page['html_name']}#{h2_item['id']}")
                a_h2.string = h2_item["text"]
                li_h2.append(a_h2)
                ul_h2.append(li_h2)

            if h2_list:
                li_h1.append(ul_h2)
            ul_h1.append(li_h1)

        if h1_list:
            li_page.append(ul_h1)

        root_ul.append(li_page)

    return str(root_ul)

def create_webpages_with_sidebar(readme_dir, output_dir, template_file="template.html"):
    """
    1. Build a site map of all pages (and their headings).
    2. Sort them according to CUSTOM_ORDER so certain pages appear first.
    3. Build a universal sidebar that lists all pages as roots.
    4. Render each page with the same sidebar and collapsible H2 sections.
    """
    os.makedirs(output_dir, exist_ok=True)
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template(template_file)

    # 1. Build the site map
    site_map = build_site_map(readme_dir)

    # 2. Sort site_map by custom order
    def sort_key(page):
        # If the page title is in CUSTOM_ORDER, return its index
        # otherwise return len(CUSTOM_ORDER) to put it at the end
        title = page["page_title"]
        if title in CUSTOM_ORDER:
            return CUSTOM_ORDER.index(title)
        else:
            return len(CUSTOM_ORDER)

    site_map.sort(key=sort_key)

    # 3. Build the sidebar HTML
    sidebar_html = build_sidebar(site_map)

    # 4. Render each page
    for page in site_map:
        output_path = os.path.join(output_dir, page["html_name"])
        rendered_html = template.render(
            title=page["page_title"],
            sidebar=sidebar_html,
            content=page["html_content"]
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print("Created:", page["html_name"])

if __name__ == "__main__":
    readme_directory = "/home/aditya/webpage/readme/"
    output_directory = "/home/aditya/webpage/webpages/"
    create_webpages_with_sidebar(readme_directory, output_directory)
