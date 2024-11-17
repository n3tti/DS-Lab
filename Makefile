DOCKER_COMPOSE = docker compose -p dockercrawler -f deployments/docker-compose.yml
JSON_FILE ?= metadata.json
RESTART ?= True

lint:
	black . && isort . && flake8 .

start:
# 	rm -rf .persistence
	python -m app.main

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
	@if [ ! deployments/_temp.built_image.sif ]; then  \
		# echo "Initial build"; \
		sha256sum deployments/Singularity > deployments/.apptainer_build_trigger; \
		touch deployments/.force_rebuild; \
	fi
	@sha256sum deployments/Singularity > deployments/.apptainer_build_trigger.new
	@if [ ! -f deployments/_temp.built_image.sif ] || ! cmp -s deployments/.apptainer_build_trigger deployments/.apptainer_build_trigger.new || [ -f deployments/.force_rebuild ]; then \
		# echo "Rebuilding..."; \
		apptainer build --fakeroot --force deployments/_temp.built_image.sif deployments/Singularity; \
		mv deployments/.apptainer_build_trigger.new deployments/.apptainer_build_trigger; \
		rm -f deployments/.force_rebuild; \
	else \
		# echo "No need to rebuild."; \
		rm deployments/.apptainer_build_trigger.new; \
	fi
	@TIMESTAMP=$$(date +%Y-%m-%dT%H.%M.%S.%6N); \
	LOGFILE=$$(mktemp -u .XXXXXXXX).log; \
	apptainer run --bind ./:/app --pwd /app deployments/_temp.built_image.sif > $$LOGFILE 2>&1 & \
	PID=$$!; \
	mv $$LOGFILE $$TIMESTAMP.log; \
	echo "Logging to $$TIMESTAMP.log"

apptainer-list:
	@PIDS=$$(pgrep -f 'make start' | sort -n); \
	PIDS_EXCEPT_LAST_TWO=$$(echo "$$PIDS" | head -n $$((PID_COUNT - 2))); \
	PID_COUNT=$$(echo "$$PIDS" | wc -l | tr -d ' '); \
	if [ "$$PID_COUNT" -lt 3 ]; then \
		echo "No 'make start' process found."; \
	else \
		FIRST_PID=$$(echo "$$PIDS" | head -n 1); \
		echo "$$PIDS_EXCEPT_LAST_TWO"; \
	fi

apptainer-kill-first:
	@PIDS=$$(pgrep -f 'make start' | sort -n); \
	PIDS_EXCEPT_LAST_TWO=$$(echo "$$PIDS" | head -n $$((PID_COUNT - 2))); \
	PID_COUNT=$$(echo "$$PIDS" | wc -l | tr -d ' '); \
	if [ "$$PID_COUNT" -lt 3 ]; then \
		echo "No 'make start' process found."; \
	else \
		FIRST_PID=$$(echo "$$PIDS" | head -n 1); \
		echo "$$PIDS_EXCEPT_LAST_TWO"; \
		echo "Killing 'make start' process with first PID $$FIRST_PID"; \
		kill $$FIRST_PID; \
	fi

apptainer-force-kill:
	-kill -- -$$(ps -eo pid,pgid,cmd | grep Apptainer | grep -v grep | head -n 1 | awk '{print $$2}')
	# if nothing helps use this: pkill -f 'python -m app.main'