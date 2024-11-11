from urllib.parse import parse_qs, urlparse, urlunparse


def normalize_url(url):
    url_parts = urlparse(url)
    query = url_parts.query
    sorted_query = sorted(parse_qs(query).items())
    # Reconstruct query string with sorted parameters
    normalized_query = "&".join(f"{key}={'&'.join(sorted(values))}" for key, values in sorted_query)
    # Reassemble the full URL with sorted query parameters
    normalized_url = urlunparse((url_parts.scheme, url_parts.netloc, url_parts.path, url_parts.params, normalized_query, url_parts.fragment))
    return normalized_url
