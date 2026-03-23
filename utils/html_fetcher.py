import urllib.request
import urllib.error

def fetch_html(url: str, timeout: int = 10) -> tuple[int, str, str]:
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'MiniCrawler/1.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset()
            
            raw_data = response.read()
            if charset:
                html_text = raw_data.decode(charset, errors="replace")
            else:
                html_text = raw_data.decode("utf-8", errors="replace")
                
            return status_code, content_type, html_text
    except Exception:
        return 0, "", ""
