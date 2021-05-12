# yfinance-downloader


## Stacks

- google cloud run
- google cloud storage
- google pub/sub
- python
- docker
- make tool

You need to setup a Google Cloud Run project and export the environment variables in order to run the code

```
export PROJECT_ID=YOUR_PROJECT_ID
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credential
make build
make run 
```

