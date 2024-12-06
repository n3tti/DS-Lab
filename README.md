My questions to all: 

- links to files with whole path?
- no enumeration is ok right?
- For developers chapter is with chat generated… XD please review and adjust
- somewhere the postprocessing part needs to be mentioned
    - before crawling is technically seen not in postprocessing

# Overview

This project is a web crawler that processes web pages from Swiss government websites. It consists of multiple components that handle crawling, data storage, and content conversion.

- [Overview](#overview)
- [Installation & Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
    - [Local Setup](#local-setup)
    - [Docker Setup](#docker-setup)
- [Usage Guide](#usage-guide)
  - [Initialize Database](#initialize-database)
  - [Crawler Usage](#crawler-usage)
    - [Setup](#setup)
    - [Crawling](#crawling)
  - [Postprocessing](#postprocessing)
    - [Convert HTML to Markdown](#convert-html-to-markdown)
    - [Save Markdown to JSONL](#save-markdown-to-jsonl)
- [Features](#features)
  - [Existing](#existing)
  - [Missing, Nice to Have](#missing-nice-to-have)

# Installation & Setup

## Prerequisites

- Python 3.x

## Environment Setup

For setting up the environment [locally](#local-setup)

or using a [docker container](#docker-setup) @Petr right?

**TODO: setup for make file**

### Local setup

1. Clone the repository

```jsx
git clone git@github.com:n3tti/DS-Lab.git
```

1. Install dependencies

```jsx
pip install -r requirements.txt
```

1. For using playwright

```makefile
playwright install
```

### Docker setup

```docker
docker-compose up
```

# Usage Guide

## Initialize database

Per default, a sqlite database is stored as [/data/example.db](./data/)

 If there is an existing database or the path resp. name should be different, create a `.env`  file and add this line:

```makefile
DATABASE_URL=sqlite://PATH_TO_DB/DB_NAME
```

For initializing a new database, you can use the following command:

```makefile
make alembic-from-scratch
```

## Crawler usage

### Setup

In [app/adminch_crawler/spiders/crawling_spider.py](./app/adminch_crawler/spiders/crawling_spider.py), you can define the allowed domains to be crawled and the url that the crawler should start with.

**Important**: The start_urls need to consist of either “http” or “https” 

```python
class CrawlingSpider(CrawlSpider):

    name = "my2crawler"
    allowed_domains = ["admin.ch"]
    start_urls = ["https://www.admin.ch/"]
```

### Crawling

To start the crawler:

```makefile
make start
```

The crawler can be stopped and continued any time later by recalling the make command.

Note that if the crawler should be completely restarted anew, the [.persistence](./.persistence/) directory needs to be removed.

## Postprocessing

### Convert html to markdown

#### Before crawling

If a specific markdown format is required before starting the crawler, change the function
`format_content_with_markdown` which can be found in [app/adminch_crawler/spiders/crawling_spider.py](./app/adminch_crawler/spiders/crawling_spider.py).

#### After crawling

If all markdown entries of the database need complete change and the change should be written into the database, adjust the function `convert_to_md` in [app/html2md/converter.py](./app/html2md/converter.py) and run the following make command:

```makefile
make html2md
```

The mentioned function in this script can also be individually called. It expects an html as string as input.

### Save markdown to jsonl

There is a script that saves the markdown content into a jsonl file. Currently, only the id and the markdown are saved. (see [postProcessing/jsonl/md2jsonl.py](./postProcessing/jsonl/md2jsonl.py))

This can be run:

```makefile
make extract-md
```

# Features

## existing

- crawler can start from whatever url is given. (see [setup](#setup))
- specific domains can be allowed (resp. excluded)
- crawler can

## missing, nice to have
