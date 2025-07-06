.PHONY: install run smoke e2e format lint

install:
	pip install -r requirements.txt

run:
	python scraper.py $(ARGS)

format:
	black scraper.py

lint:
	flake8 scraper.py

smoke:
	python scraper.py --keywords "test" --pages 1 --mode batch || true

e2e:
	python scraper.py --keywords "test" --pages 3 --mode batch --output results.json || true
