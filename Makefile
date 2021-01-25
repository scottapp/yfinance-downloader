.PHONY: build run

build:
	docker build -t yfinance_downloader .

run:
	docker run -d -e GOOGLE_APPLICATION_CREDENTIALS='/tmp/keys/credential.json' \
	-e PROJECT_ID='$(PROJECT_ID)' \
	-v $(GOOGLE_APPLICATION_CREDENTIALS):/tmp/keys/credential.json:ro yfinance_downloader

test:
	docker run --rm --entrypoint pytest -e GOOGLE_APPLICATION_CREDENTIALS='/tmp/keys/credential.json' \
	-e PROJECT_ID='$(PROJECT_ID)' \
	-v $(GOOGLE_APPLICATION_CREDENTIALS):/tmp/keys/credential.json:ro yfinance_downloader
