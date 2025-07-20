# swipe_right_real_estate_backend
Backend for swipe right real estate application


# Developing
## Build project first time
```
make build
```

## Start server
```
make run
```

## Run unit tests
```
make test
```

## Run migration after changing Django models
```
make makemigrations
make migrate
```

## Test cloud functions locally

### Cloud function for craw ISC website based in a search ID
```
functions-framework --source cloud-functions/webcrawler_isc/crawler.py --target crawler
curl "http://localhost:8080?search_id=<search-id>"
```

### Cloud function to update real estates and generate notification
```
????
```