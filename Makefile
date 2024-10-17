lint:
	black . && isort . && flake8 .

test:
	pytest