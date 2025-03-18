import os
import markdown
import re
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

CUSTOM_ORDER = [
    "Home",
    "Quick-start-Demo-install",
    "Production-Install",
    "i2b2-Upgrade",
    "i2b2-Admin-Module"
]

def fix_link(match):
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
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = []
    for tag in soup.find_all(['h1','h2']):
        level = int(tag.name[1])
        if not tag.has_attr('id'):
            heading_id = re.sub(r'\s+', '-', tag.get_text().strip().lower())
            tag['id'] = heading_id
        else:
            heading_id = tag['id']
        headings.append((level, tag.get_text().strip(), heading_id))
    return str(soup), headings

def wrap_h2_collapsible(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.new_tag('div')
    current_section = None

    for element in soup.contents:
        if element.name == 'h2':
            if current_section is not None:
                container.append(current_section)
                current_section = None
            
            toggle_btn = soup.new_tag('button', **{'class': 'h2-toggle'})
            toggle_btn.string = '+'
            element.insert(0, toggle_btn)
            container.append(element)
            
            current_section = soup.new_tag('div', **{
                'class': 'collapsible-section',
                'style': 'display:none;'
            })
        else:
            if current_section is not None:
                current_section.append(element)
            else:
                container.append(element)

    if current_section is not None:
        container.append(current_section)

    return str(container)

def build_site_map(readme_dir):
    site_map = []
    for filename in os.listdir(readme_dir):
        if filename.lower().endswith((".md", ".readme")):
            filepath = os.path.join(readme_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()

            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite', 'tables'])
            html_content, headings = parse_headings(html_content)
            html_content = re.sub(r'href="([^"]+)"', fix_link, html_content)
            html_content = wrap_h2_collapsible(html_content)
            
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
    soup = BeautifulSoup("", 'html.parser')
    root_ul = soup.new_tag('ul', **{'class': 'sidebar-root'})

    for page in site_map:
        li_page = soup.new_tag('li', **{'class': 'sidebar-page'})
        if page["headings"]:
            toggle_page = soup.new_tag('span', **{'class': 'sidebar-toggle'})
            toggle_page.string = '+ '
            li_page.append(toggle_page)
        a_page = soup.new_tag('a', href=page["html_name"])
        a_page.string = page["page_title"]
        li_page.append(a_page)

        ul_h1 = soup.new_tag('ul', **{'class': 'h1-list', 'style': 'display:none;'})
        h1_list = [h for h in page["headings"] if h["level"] == 1]
        for h1_item in h1_list:
            li_h1 = soup.new_tag('li', **{'class': 'sidebar-h1'})
            h2_list = [h for h in page["headings"] if h["level"] == 2]

            if h2_list:
                toggle_h1 = soup.new_tag('span', **{'class': 'sidebar-toggle'})
                toggle_h1.string = '+ '
                li_h1.append(toggle_h1)
            a_h1 = soup.new_tag('a', href=f"{page['html_name']}#{h1_item['id']}")
            a_h1.string = h1_item["text"]
            li_h1.append(a_h1)

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
    os.makedirs(output_dir, exist_ok=True)
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template(template_file)

    site_map = build_site_map(readme_dir)

    def sort_key(page):
        title = page["page_title"]
        return CUSTOM_ORDER.index(title) if title in CUSTOM_ORDER else len(CUSTOM_ORDER)

    site_map.sort(key=sort_key)
    sidebar_html = build_sidebar(site_map)

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
    readme_directory = "/home/aditya/readmetohtml/readme/"
    output_directory = "/home/aditya/readmetohtml/webpages/"
    create_webpages_with_sidebar(readme_directory, output_directory)
