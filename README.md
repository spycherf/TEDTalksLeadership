# Exploring the Impact of Charismatic and Leader-Like Speakers on Their Audience

*DM & ML semester project led by Prof. Michalis Vlachos, HEC Lausanne*

**Author**: Frederic Spycher

## Files

`notebook.ipynb` is the project's main file. It contains background information about the project, data collection, the cleaning process, etc. Custom functions used in the notebook were put in the `notebook_functions.py` file so as not to clutter the notebook needlessly.

All the files pertaining to data collection are stored under `data/`. Each subdirectory corresponds to a particular type of data, namely:

* `metadata_transcripts`: the main data, which consist of TED(x) talks transcripts and metadata (such as name of the speaker, the hosting event, the number of views, and many more). This data comes from two sources: scraped from the TED website and queried through the YouTube API. The TED scraper was heavily inspired by [this project](https://github.com/ROC-HCI/TEDTalk_Analytics/), and provided the basic structure for other scripts.
    * **TED**: [Script](https://github.com/spycherf/TEDTalksLeadership/blob/master/data/metadata_transcripts/ted/ted_scraper.py) | [Data](https://raw.githubusercontent.com/spycherf/TEDTalksLeadership/master/data/metadata_transcripts/ted/output/ted_talks_TED_metadata_transcripts.csv)
    * **YouTube metadata**: [Script](https://github.com/spycherf/TEDTalksLeadership/blob/master/data/metadata_transcripts/youtube/youtube_api_query.py) | [Data](https://raw.githubusercontent.com/spycherf/TEDTalksLeadership/master/data/metadata_transcripts/youtube/output/ted_talks_YT_metadata.csv)
    * **YouTube transcripts**: [Script](https://github.com/spycherf/TEDTalksLeadership/blob/master/data/metadata_transcripts/youtube/youtube_transcripts.py) | Data (hosted on SWITCHdrive)
    
* `personality_profiles`: transcripts were fed to the IBM Watson Personality Insights API in order to get their respective personality profile, which contain among other things information about the Big Five personality traits.
    * [Script](https://github.com/spycherf/TEDTalksLeadership/blob/master/data/personality_profiles/ibm_api_query.py) | [Data](https://raw.githubusercontent.com/spycherf/TEDTalksLeadership/master/data/personality_profiles/output/personality_profiles_json.csv)
    
* `gender_age` = estimates of the gender and age of TED(x) speakers based on either their photo/video thumbnail, or, in the case of gender, the pitch of their voice.
    * **Azure**: [Script](https://github.com/spycherf/TEDTalksLeadership/blob/master/data/gender_age/azure/azure_api_query.py) | [Data](https://raw.githubusercontent.com/spycherf/TEDTalksLeadership/master/data/gender_age/azure/output/gender_age_estimates.csv)
    * **GMM audio analysis**: [Script](https://github.com/spycherf/TEDTalksLeadership/blob/master/data/gender_age/gmm/gender_prediction.py) | [Data](https://raw.githubusercontent.com/spycherf/TEDTalksLeadership/master/data/gender_age/gmm/output/gender_estimates.csv)

In each case, the `logs/` subdirectory contains the IDs of records that could be processed successfully, and of those that failed.
