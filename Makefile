DOCKER_COMPOSE = docker compose -p dockercrawler -f deployments/docker-compose.yml
JSON_FILE ?= metadata.json
RESTART ?= True

lint:
	black . && isort . && flake8 .

start:
	rm -rf crawler/adminch_crawler/persistance/jobdir* && cd crawler && scrapy crawl my2crawler -a restart=$(RESTART)

resume:
	cd crawler && scrapy crawl my2crawler -a restart=True

reformat:
	cat "data/$(JSON_FILE)" | jq . > "data/n_$(JSON_FILE)"

up:
	$(DOCKER_COMPOSE) up -d --build

test:
	pytest


docker-up:
	docker compose -p dockercrawler -f deployments/docker-compose.yml up -d --build

apptainer-up: deployments/Singularity requirements.txt
	@if [ ! -f .apptainer_build_trigger ]; then \
		echo "Initial build required..."; \
		sha256sum deployments/Singularity requirements.txt > .apptainer_build_trigger; \
		touch .force_rebuild; \
	fi
	@sha256sum deployments/Singularity requirements.txt > .apptainer_build_trigger.new
	@if [ ! -f deployments/_temp.admincrawler.sif ] || ! cmp -s .apptainer_build_trigger .apptainer_build_trigger.new || [ -f .force_rebuild ]; then \
		echo "Changes detected or initial build, rebuilding..."; \
		apptainer build --fakeroot --force deployments/_temp.admincrawler.sif deployments/Singularity; \
		mv .apptainer_build_trigger.new .apptainer_build_trigger; \
		rm -f .force_rebuild; \
	else \
		echo "No changes detected or rebuild needed. Skipping rebuild."; \
		rm .apptainer_build_trigger.new; \
	fi
	apptainer run --bind ./:/app --pwd /app deployments/_temp.admincrawler.sif
