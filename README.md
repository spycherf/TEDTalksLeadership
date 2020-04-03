# Exploring the Impact of Charismatic Leadership Tactics Used by TED Speakers

*DM & ML semester project led by Prof. Michalis Vlachos, HEC Lausanne*

## Files

`notebook.ipynb` is the project's main file. It contains background information about the project, data processing, models, etc.

All the files pertaining to data collection are stored under `/data`:

* `ted_scraper.py`: script used to scrape the TED website (heavily inspired by [this project](https://github.com/ROC-HCI/TEDTalk_Analytics/)
* `youtube_query.py`: script used to harvest the YouTube data using their API
* The data itself is saved in the `/ted` and `/youtube` subfolders. In each case, the `successful.txt` and `failed.txt` files contain the IDs of records that could/could not be retrieved, respectively.