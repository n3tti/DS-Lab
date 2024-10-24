JSON_FILE ?= metadata.json

lint:
	black . && isort . && flake8 .

start:
	cd crawler && scrapy crawl mycrawler

reformat:
	cat "data/$(JSON_FILE)" | jq . > "data/n_$(JSON_FILE)"

test:
	pytest