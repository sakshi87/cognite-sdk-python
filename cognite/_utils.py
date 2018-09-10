# -*- coding: utf-8 -*-
"""Utilites for Cognite API SDK

This module provides helper methods and different utilities for the Cognite API Python SDK.

This module is protected and should not used by end-users.
"""
import gzip
import json
import logging
import re
import time
from datetime import datetime
from typing import Callable, List

import requests

import cognite.config as config

log = logging.getLogger("cognite-sdk")


def delete_request(url, params=None, headers=None, cookies=None):
    """Perform a DELETE request with a predetermined number of retries."""
    _log_request("DELETE", url, params=params, headers=headers, cookies=cookies)
    for number_of_tries in range(config.get_number_of_retries() + 1):
        try:
            res = requests.delete(url, params=params, headers=headers, cookies=cookies)
            if res.status_code == 200:
                return res
        except Exception:
            if number_of_tries == config.get_number_of_retries():
                raise
    x_request_id = res.headers.get("X-Request-Id")
    code = res.status_code
    try:
        error = res.json()["error"]
        if isinstance(error, str):
            msg = error
        else:
            msg = error.get("message") or res.json()
    except TypeError:
        msg = res.content
    except KeyError:
        msg = res.json()
    raise APIError(msg, code, x_request_id)


def get_request(url, params=None, headers=None, cookies=None):
    """Perform a GET request with a predetermined number of retries."""
    _log_request("GET", url, params=params, headers=headers, cookies=cookies)
    for number_of_tries in range(config.get_number_of_retries() + 1):
        try:
            res = requests.get(url, params=params, headers=headers, cookies=cookies)
            if res.status_code == 200:
                return res
        except Exception:
            if number_of_tries == config.get_number_of_retries():
                raise
    x_request_id = res.headers.get("X-Request-Id")
    code = res.status_code
    try:
        error = res.json()["error"]
        if isinstance(error, str):
            msg = error
        else:
            msg = error.get("message") or res.json()
    except TypeError:
        msg = res.content
    except KeyError:
        msg = res.json()
    raise APIError(msg, code, x_request_id)


def post_request(url, body, headers=None, params=None, cookies=None, use_gzip=False):
    """Perform a POST request with a predetermined number of retries."""
    _log_request("POST", url, body=body, params=params, headers=headers, cookies=cookies)

    for number_of_tries in range(config.get_number_of_retries() + 1):
        try:
            if use_gzip:
                if headers:
                    headers["Content-Encoding"] = "gzip"
                else:
                    headers = {"Content-Encoding": "gzip"}
                res = requests.post(
                    url,
                    data=gzip.compress(json.dumps(body).encode("utf-8")),
                    headers=headers,
                    params=params,
                    cookies=cookies,
                )
            else:
                res = requests.post(url, data=json.dumps(body), headers=headers, params=params, cookies=cookies)
            if res.status_code == 200:
                return res
        except Exception:
            if number_of_tries == config.get_number_of_retries():
                raise
    x_request_id = res.headers.get("X-Request-Id")
    code = res.status_code
    try:
        error = res.json()["error"]
        if isinstance(error, str):
            msg = error
        else:
            msg = error.get("message") or res.json()
    except TypeError:
        msg = res.content
    except KeyError:
        msg = res.json()
    raise APIError(msg, code, x_request_id)


def put_request(url, body=None, headers=None, cookies=None):
    """Perform a PUT request with a predetermined number of retries."""
    _log_request("PUT", url, body=body, headers=headers, cookies=cookies)
    for number_of_tries in range(config.get_number_of_retries() + 1):
        try:
            res = requests.put(url, data=json.dumps(body), headers=headers, cookies=cookies)
            if res.ok:
                return res
        except Exception:
            if number_of_tries == config.get_number_of_retries():
                raise
    x_request_id = res.headers.get("X-Request-Id")
    code = res.status_code
    try:
        error = res.json()["error"]
        if isinstance(error, str):
            msg = error
        else:
            msg = error.get("message") or res.json()
    except TypeError:
        msg = res.content
    except KeyError:
        msg = res.json()
    raise APIError(msg, code, x_request_id)


def _log_request(method, url, **kwargs):
    log.debug("HTTP/1.1 {} {}".format(method, url), extra=kwargs)


def datetime_to_ms(dt):
    return int(dt.timestamp() * 1000)


def round_to_nearest(x, base):
    return int(base * round(float(x) / base))


def granularity_to_ms(time_string):
    """Returns millisecond representation of granularity time string"""
    magnitude = int("".join([c for c in time_string if c.isdigit()]))
    unit = "".join([c for c in time_string if c.isalpha()])
    unit_in_ms = {
        "s": 1000,
        "second": 1000,
        "m": 60000,
        "minute": 60000,
        "h": 3600000,
        "hour": 3600000,
        "d": 86400000,
        "day": 86400000,
    }
    return magnitude * unit_in_ms[unit]


def _time_ago_to_ms(time_ago_string):
    """Returns millisecond representation of time-ago string"""
    if time_ago_string == 'now':
        return 0
    pattern = r"(\d+)([a-z])-ago"
    res = re.match(pattern, str(time_ago_string))
    if res:
        magnitude = int(res.group(1))
        unit = res.group(2)
        unit_in_ms = {"s": 1000, "m": 60000, "h": 3600000, "d": 86400000, "w": 604800000}
        return magnitude * unit_in_ms[unit]
    return None


def interval_to_ms(start, end):
    """Returns the ms representation of start-end-interval whether it is time-ago, datetime or None."""
    time_now = int(round(time.time() * 1000))
    if isinstance(start, datetime):
        start = datetime_to_ms(start)
    elif isinstance(start, str):
        start = time_now - _time_ago_to_ms(start)
    elif start is None:
        start = time_now - _time_ago_to_ms("2w-ago")

    if isinstance(end, datetime):
        end = datetime_to_ms(end)
    elif isinstance(end, str):
        end = time_now - _time_ago_to_ms(end)
    elif end is None:
        end = time_now

    return start, end


class APIError(Exception):
    def __init__(self, message, code=None, x_request_id=None):
        self.message = message
        self.code = code
        self.x_request_id = x_request_id

    def __str__(self):
        return "{} | code: {} | X-Request-ID: {}".format(self.message, self.code, self.x_request_id)


class InputError(Exception):
    pass


class Bin:
    """
    Attributes:
        entries (List): List of entries.
        get_count (Callable): Callable function to get count.
    """

    def __init__(self, get_count):
        """
        Args:
            get_count: A function that will take an element and get the count of something in it.
        """
        self.entries = []
        self.get_count = get_count

    def add_item(self, item):
        self.entries.append(item)

    def sum(self):
        total = 0
        for elem in self.entries:
            total += self.get_count(elem)
        return total

    def show(self):
        return self.entries


def first_fit(list_items: List, max_size, get_count: Callable) -> List[List]:
    """Returns list of bins with input items inside."""

    # Sort the input list in decreasing order
    list_items = sorted(list_items, key=get_count, reverse=True)

    list_bins = [Bin(get_count=get_count)]

    for item in list_items:
        # Go through bins and try to allocate
        alloc_flag = False

        for bin in list_bins:
            if bin.sum() + get_count(item) <= max_size:
                bin.add_item(item)
                alloc_flag = True
                break

        # If item not allocated in bins in list, create new bin
        # and allocate it to it.
        if not alloc_flag:
            new_bin = Bin(get_count=get_count)
            new_bin.add_item(item)
            list_bins.append(new_bin)

    # Turn bins into list of items and return
    list_items = []
    for bin in list_bins:
        list_items.append(bin.show())

    return list_items
