lint:
	black . && isort . && flake8 .

start:
	cd crawler && scrapy crawl mycrawler

test:
	pytest