DOCKER_COMPOSE = docker compose -p dockercrawler -f deployments/docker-compose.yml
JSON_FILE ?= metadata.json
RESTART ?= True

lint:
	black . && isort . && flake8 .

start:
	rm -rf persistence/*; \
	python -m app.main

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
	@if [ ! deployments/_temp.admincrawler.sif ]; then  \
		# echo "Initial build"; \
		sha256sum deployments/Singularity requirements.txt > deployments/.apptainer_build_trigger; \
		touch deployments/.force_rebuild; \
	fi
	@sha256sum deployments/Singularity requirements.txt > deployments/.apptainer_build_trigger.new
	@if [ ! -f deployments/_temp.admincrawler.sif ] || ! cmp -s deployments/.apptainer_build_trigger deployments/.apptainer_build_trigger.new || [ -f deployments/.force_rebuild ]; then \
		# echo "Rebuilding..."; \
		apptainer build --fakeroot --force deployments/_temp.admincrawler.sif deployments/Singularity; \
		mv deployments/.apptainer_build_trigger.new deployments/.apptainer_build_trigger; \
		rm -f deployments/.force_rebuild; \
	else \
		# echo "No need to rebuild."; \
		rm deployments/.apptainer_build_trigger.new; \
	fi
	apptainer run --bind ./:/app --pwd /app deployments/_temp.admincrawler.sif
