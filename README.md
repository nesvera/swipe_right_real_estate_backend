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

## Tests

Use the following command to run tests.
```
make test
```

You can run specific tests from an app
```
make test path=real_estate_review
```

You can run even more specific test by choosing the file, test suite or test case
```
make test path=real_estate_review.tests.test_model
make test path=real_estate_review.tests.test_model.TestRealEstateReviewModels
make test path=real_estate_review.tests.test_model.TestRealEstateReviewModels.test_radar_real_estate_review_creation_success_min_info
```



Tests via API call requires patch of throttling mechanism from Django, if not tets may fail since server may return status code 429.

You can patch the TestCase class as showing below.
```
@patch("rest_framework.throttling.AnonRateThrottle.get_rate", lambda x: "1000/minute")
@patch("rest_framework.throttling.UserRateThrottle.get_rate", lambda x: "1000/minute")
class PublicApiTests(TestCase):
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