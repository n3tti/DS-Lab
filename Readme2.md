# HTML to Markdown Converter Project Documentation

## Overview
This project is a web crawler and HTML to Markdown converter that processes web pages from Swiss government websites. It consists of multiple components that handle crawling, data storage, and content conversion.

## Key Components

### 1. Web Crawler
The project includes a Scrapy-based crawler that can be run with restart options:

```bash
# Run crawler with restart
scrapy crawl my2crawler -a restart=True

# Run crawler without restart (default)
scrapy crawl my2crawler
```

To cleanly stop the crawling process for later resumption, use CTRL+C once.

### 2. HTML to Markdown Converter
The core conversion functionality is implemented in the HTMLToMarkdownConverter class:

```python:app/html2md/converter.py
startLine: 8
endLine: 32
```

Key features:
- Converts HTML content to Markdown format
- Stores converted content in database
- Handles UTF-8 encoding
- Includes error handling for conversion process

### 3. Database Integration
The project uses SQLAlchemy for database operations with the following models:
- ScrapedPage: Stores raw HTML content
- MarkdownPage: Stores converted markdown content
- PageStatusEnum: Tracks conversion status

### 4. Directory Structure
```
project/
├── app/
│   ├── html2md/
│   │   ├── converter.py
│   │   ├── html_files/
│   │   └── markdown/
│   ├── repository/
│   │   ├── db.py
│   │   └── models.py
│   └── config.py
└── Crawler/
    └── adminch_crawler/
```

## Usage

### Running the Crawler
```bash
# Clean restart
make start RESTART=true
rm -r ./adminch_crawler/persistance/jobdir/*

# Resume previous crawl
make start RESTART=false
```

### Converting HTML to Markdown
```bash
make html2md
```

### Running Tests
```bash
make test
```

## Sample Output
The converter processes HTML content like navigation menus, content sections, and links. Example of converted content:

```markdown:app/html2md/markdown/00a5c640-17c3-4889-88b1-e39fae635f3b.md
startLine: 456
endLine: 467
```

## Error Handling
The converter includes error handling for:
- UTF-8 decoding issues
- Database connection errors
- Malformed HTML content

## Dependencies
- markdownify
- SQLAlchemy
- Scrapy
- Python 3.x

## Notes
- The crawler can be safely paused and resumed
- Markdown conversion preserves link structures and hierarchies
- Database transactions use session management for consistency
```