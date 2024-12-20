# Overview

This project is a web crawler that processes web pages from Swiss government websites. It consists of multiple components that handle crawling, data storage, and content conversion.

- [Overview](#overview)
- [Installation \& Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
    - [Local setup](#local-setup)
    - [Docker setup](#docker-setup)
- [Usage Guide](#usage-guide)
  - [First things first](#first-things-first)
    - [Newrelic for Observability](#newrelic-for-observability)
  - [Initialize database](#initialize-database)
  - [Crawler usage](#crawler-usage)
    - [Setup](#setup)
    - [Crawling](#crawling)
  - [Postprocessing](#postprocessing)
    - [Save markdown to jsonl](#save-markdown-to-jsonl)
    - [Convert pdf text and tables to markdown](#convert-pdf-text-and-tables-to-markdown)
    - [Get SimHash on md text](#get-simhash-on-md-text)
- [Features](#features)

# Installation & Setup

## The easy way:

### Launch Docker

```docker
make docker-up
```

## The harder way:

### Prerequisites

- Python 3.11.10

### Environment Setup

For setting up the environment [locally](#local-setup)

or using a [docker container](#docker-setup)


#### Local setup
<!--
Clone the repository
```jsx
git clone git@github.com:n3tti/DS-Lab.git
```
(Preferred but not required:) Create a python virtual environment and activate it
```
python -m venv VENV_NAME
source PATH_TO_VENV/bin/activate
```
-->
Install dependencies

```jsx
pip install -r requirements.txt
```
For using playwright

```bash
playwright install
```

<details>
	<summary>TL;DR: In case <code>playwright install</code> is not enough</summary>
	Playwright will produce errors and might require installation of the following libs (within the Apptainer it should be possible to run it without having system-wide sudo access):
	<pre><code class="language-bash">
sudo apt-get install libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libgbm1
	</code></pre>
</details>


# Usage Guide

## First things first

Create a copy of the file called `.env.example`. Set a preferred `LOG_LEVEL` there as well as other parameters (for example if intended for usage and not for developing: set the `DEBUG=false`).

### Newrelic for Observability
<details>
	<summary>TL;DR: Newrelic notes</summary>
	<p class="has-line-data" data-line-start="0" data-line-end="1">Potentially register a new <strong>newrelic</strong> account to have logs stored on <a href="http://newrelic.com">newrelic.com</a> for easier monitoring. Add a <code>NEW_RELIC_LICENSE_KEY</code> to the <code>.env</code> file. Pay attention that setting this <code>NEW_RELIC_LICENSE_KEY</code> ENV in the <code>.env</code> file works only coupled with containerized environment now, and it’s loaded before the python program is launched.</p>
<p class="has-line-data" data-line-start="2" data-line-end="3">It is not enough for it to work with a virtual environment of python (i.e. the one created with <code>python -m venv &lt;name-of-environment&gt;</code>) since the module <strong>dotenv</strong> loads the ENVs after the <strong>newrelic</strong> is initialized. For <strong>newrelic</strong> to work with the virtual environment of python put the <code>NEW_RELIC_LICENSE_KEY</code> into the <code>newrelic.ini</code> file (be careful not to push it to github or other platforms).</p>
</details>



## Initialize database

Per default, a sqlite database is stored as [data/example.db](./data/)

 If there is an existing database or the path resp. name should be different, create a `.env`  file and add this line:

```makefile
DATABASE_URL=sqlite:///PATH_TO_DB/DB_NAME
```

For initializing a new database, you can use the following command:

**EXAMPLE ON HOW TO USE ALEMBIC**
```
alembic:
	rm -rf data/*.db*; \
# 	rm -rf migrations/versions/*.py; \
# 	alembic revision --autogenerate -m "Create scraped_page table"; \
	alembic upgrade head

alembic-from-scratch:
	rm -rf data/*.db*; \
	rm -rf migrations/versions/*.py; \
	alembic revision --autogenerate -m "Create scraped_page table"; \
	alembic upgrade head
```

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

<!--
### Convert html to markdown

#### Before crawling

If a specific markdown format is required before starting the crawler, change the function
`format_content_with_markdown` which can be found in [app/adminch_crawler/spiders/crawling_spider.py](./app/adminch_crawler/spiders/crawling_spider.py).

#### After crawling

If all markdown entries of the database need complete change and the change should be written into the database, adjust the function `convert_to_md` in [app/html2md/converter.py](./app/html2md/converter.py) and run the following make command:

```makefile
make html2md
```

The mentioned function in this script can also be individually called. It expects an html as string as input and returns the markdown as a string.
-->
### Save markdown to jsonl

There is a script that saves the markdown content into a jsonl file. Currently, only the id and the markdown are saved. (see [postProcessing/jsonl/md2jsonl.py](./postProcessing/jsonl/md2jsonl.py))

This can be run:

```makefile
make extract-md
```

### Convert pdf text and tables to markdown

Run the python script parsePDFs.py (see[postProcessing/ExtractPDFs/parsePDFs.py](./postProcessing/ExtractPDFs/parsePDFs.py)) or multicore.py in the same folder.

### Get SimHash on md text
Run the python script compute_hash.py (see[postProcessing/simhash/compute_hash.py](./postProcessing/simhash/compute_hash.py)).

# Features

- crawler can start from whatever url is given. (see [setup](#setup))
- specific domains can be allowed (resp. excluded)
- see all additional crawler setting in [app/config.py](./app/config.py)

