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

## Short introduction to the Folder structure
- The code for the **Scrapy crawler** is contained within the `app/` directory
- The code for the **deployments (with Docker or Apptainer)** is contained within the `deployments/` directory
- The code for the **migrations (with Alembic)** is contained within the `migrations/` directory
- The code for **post-processing of PDFs** is contained within the `postProcessing/` directory
- The **queries examples** are contained within the `queries/` directory
- *_The `scripts/` directory is work-in-progress, and is not important at the current state of the project_

## Installation: the easy way

### Launch Docker

```docker
make docker-up
```

## Installation: the harder way:

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

Create a copy of the file called `.env.example` and name it `.env`<br>
*If needed: set a preferred `LOG_LEVEL` there, as well as other parameters (for example if intended **not for developing**: set the `DEBUG=false`).

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
Create a database if it doesn't exist; and update it to the highest migration.
```
alembic upgrade head
```

*Example on how to create a migration having a model defined up in the `app/repository/models.py`
```
alembic revision --autogenerate -m "Create scraped_page table"
```

There is a command that deletes the database in the `data/` folder and creates a new one. Convenient for debugging:
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

