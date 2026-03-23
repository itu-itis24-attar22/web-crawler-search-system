import urllib.parse

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    if not path:
        path = "/"
    elif path != "/" and path.endswith("/"):
        path = path[:-1]
    
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{scheme}://{netloc}{path}{query}"

def resolve_url(base_url: str, href: str) -> str | None:
    joined = urllib.parse.urljoin(base_url, href)
    return normalize_url(joined)

def is_http_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme.lower() in ("http", "https")

def should_skip_url(url: str) -> bool:
    url = url.strip().lower()
    if not url:
        return True
    if url.startswith(("mailto:", "javascript:", "tel:")):
        return True
    
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return True
    
    path = parsed.path
    ext = path.split('.')[-1] if '.' in path else ""
    skip_exts = {
        "jpg", "jpeg", "png", "gif", "svg", "pdf", "zip", 
        "mp4", "mp3", "doc", "docx", "xls", "xlsx", "ppt", "pptx"
    }
    if ext in skip_exts:
        return True
        
    return False

def same_domain(origin_url: str, candidate_url: str) -> bool:
    origin_parsed = urllib.parse.urlparse(origin_url)
    candidate_parsed = urllib.parse.urlparse(candidate_url)
    return origin_parsed.netloc.lower() == candidate_parsed.netloc.lower()
