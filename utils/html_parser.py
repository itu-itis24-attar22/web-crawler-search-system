from html.parser import HTMLParser
from utils.url_utils import resolve_url, should_skip_url

class SimpleHTMLParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.text_chunks = []
        self.links = []
        self.ignore_tags = {"script", "style", "noscript"}
        self.in_ignore_stack = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.ignore_tags:
            self.in_ignore_stack += 1
        
        if tag == "a":
            for attr, value in attrs:
                if attr == "href" and value:
                    resolved = resolve_url(self.base_url, value)
                    if resolved and not should_skip_url(resolved):
                        self.links.append(resolved)

    def handle_endtag(self, tag):
        if tag in self.ignore_tags:
            self.in_ignore_stack = max(0, self.in_ignore_stack - 1)

    def handle_data(self, data):
        if self.in_ignore_stack == 0:
            chunk = data.strip()
            if chunk:
                self.text_chunks.append(chunk)

def extract_text_and_links(html: str, base_url: str) -> tuple[str, list[str]]:
    parser = SimpleHTMLParser(base_url)
    try:
        parser.feed(html)
    except Exception:
        pass  # ignore malformed HTML errors
    
    seen_links = set()
    deduped_links = []
    for link in parser.links:
        if link not in seen_links:
            seen_links.add(link)
            deduped_links.append(link)
            
    visible_text = " ".join(parser.text_chunks)
    return visible_text, deduped_links
