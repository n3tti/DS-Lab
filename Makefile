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
	@bash _apptainer_up.sh &

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

apptainer-kill:
	pgrep -aif '[aA][pP][pP][tT][aA][iI][nN][eE][rR]' | awk '{print $1}' | xargs -I {} sh -c 'kill -TERM -- -$(ps -o pgid= -p {} | tr -d " ")'


apptainer-force-kill:
	-kill -- -$$(ps -eo pid,pgid,cmd | grep Apptainer | grep -v grep | head -n 1 | awk '{print $$2}')
	# if nothing helps use this: pkill -f 'python -m app.main'