.PHONY: install run smoke e2e format lint

install:
	 pip install -r requirements.txt

run:
	 python scraper.py $(ARGS)

format:
	 black scraper.py tests/run.py

lint:
	 flake8 scraper.py tests/run.py

smoke:
	 python tests/run.py --pages 1 --expect 20

e2e:
	 python tests/run.py --pages 3 --expect 60 --outfile results.json
