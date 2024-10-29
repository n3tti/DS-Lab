JSON_FILE ?= metadata.json
RESTART ?= True

lint:
	black . && isort . && flake8 .

start:
	rm -rf crawler/adminch_crawler/persistance/jobdir* && cd crawler && scrapy crawl my2crawler -a restart=$(RESTART)

reformat:
	cat "data/$(JSON_FILE)" | jq . > "data/n_$(JSON_FILE)"

test:
	pytest
