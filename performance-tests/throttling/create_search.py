#!/usr/bin/env python3

"""
Verify throttling policy against create search API.
This is an unauthenticated API that is quiet expensive since it launches a crawler.
"""

import requests
import concurrent.futures
import threading

from typing import List

NUM_REQUESTS = 100


def create_search(result_list: List[int], result_list_lock: threading.Lock) -> None:
    payload = {
        "property_type": ["apartment"],
        "transaction_type": ["rent"],
        "city": ["blumenau"],
        "neighborhood": ["fortaleza"],
        "bedroom_quantity": [1],
        "suite_quantity": [0],
        "bathroom_quantity": [1],
        "garage_slots_quantity": [0],
        "min_price": 500,
        "max_price": 3000,
        "min_area": 30,
        "max_area": 100,
    }

    url = "http://127.0.0.1:8000/api/search/v1/search"
    resp = requests.post(url=url, json=payload)

    with result_list_lock:
        result_list.append(resp.status_code)


if __name__ == "__main__":

    result_list = []
    result_list_lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor() as executor:

        for i in range(NUM_REQUESTS):
            create_search(result_list, result_list_lock)

    count_status_201 = result_list.count(201)
    count_status_429 = result_list.count(429)
    count_status_other = len(result_list) - count_status_201 - count_status_429

    print("Count status 201: ", count_status_201)
    print("Count status 429: ", count_status_429)
    print("Count status others: ", count_status_other)
