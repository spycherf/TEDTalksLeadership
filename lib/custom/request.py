import random
import sys
import time

from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import urlopen
from urllib.request import urlretrieve


def wait():
    sleep_duration = random.randint(1, 60)
    print("Too many requests. Sleeping for {0} seconds...".format(sleep_duration))
    time.sleep(sleep_duration)
    print("Trying again...")


def request_html(url):
    print("Requesting:", url)
    i = 0

    while i < 100:
        sys.stdout.flush()
        time.sleep(2)
        try:
            response = urlopen(url)
            break
        except HTTPError as e:
            # Handling "too many requests" & "unknown" errors
            if e.code == 429 or e.code == 599:
                i += 1
                wait()
                continue
            else:
                raise
        # Handling "WinError 10054" errors
        except URLError:
            i += 1
            wait()
            continue

    src = response.read().decode("utf8", "ignore").replace("\r", " ").replace("\n", " ").replace("&amp;", "&")
    html = BeautifulSoup(src, "lxml")

    if not html:
        raise IOError("HTTP failure")

    return html


def download_image(url, file):
    print("Downloading:", url)
    i = 0

    while i < 100:
        try:
            urlretrieve(url, file)
            break
        except HTTPError as e:
            # Handling "too many requests" & "unknown" errors
            if e.code == 429 or e.code == 599:
                i += 1
                wait()
                continue
            else:
                raise
        # Handling "WinError 10054" errors
        except URLError:
            i += 1
            wait()
            continue
