import numpy as np
import pandas as pd


def do_cleaning(df):
    # Combining columns/replacing null values
    df["duration"] = np.where(df["duration"] == 0, df["ext_duration"], df["duration"])

    df["views_YT"].fillna(0, inplace=True)
    df["views"] = df["views_TED"] + df["views_YT"]

    df["nb_comments_YT"].fillna(0, inplace=True)
    df["nb_comments_TED"] = np.where(df["nb_comments_TED"] == -1, 0, df["nb_comments_TED"])
    df["nb_comments"] = df["nb_comments_TED"] + df["nb_comments_YT"]

    df["description"] = df["description_TED"].fillna(df["description_YT"])
    df["tags"] = df["tags_TED"].fillna(df["tags_YT"])
    df["transcript"] = df["transcript_TED"].fillna(df["transcript_YT"])

    # Getting rid of unnecessary columns
    df.drop(["url", "description_TED", "tags_TED", "nb_languages",
             "views_TED", "nb_comments_TED", "nb_speakers", "speakers", "speakers_desc",
             "ext_src", "ext_id", "ext_duration", "transcript_TED",
             "channel", "title_YT", "description_YT", "tags_YT", "date_published_YT",
             "views_YT", "nb_comments_YT", "transcript_YT"
             ], axis=1, inplace=True)

    # Renaming some columns
    df.rename(columns={"id_TED": "id", "title_TED": "title",
                       "date_published_TED": "date_published",
                       "native_language": "language", "id_YT": "yt_id"
                       }, inplace=True)

    # Removing duplicates
    df = df.drop_duplicates(subset="id", keep="first")

    # Changing data types
    df["duration"] = pd.Series(df["duration"], dtype="Int64")
    df["likes"] = pd.Series(df["likes"], dtype="Int64")
    df["dislikes"] = pd.Series(df["dislikes"], dtype="Int64")
    df["views"] = pd.Series(df["views"], dtype="Int64")
    df["nb_comments"] = pd.Series(df["nb_comments"], dtype="Int64")
    df["date_recorded"] = pd.to_datetime(df["date_recorded"])
    df["date_published"] = pd.to_datetime(df["date_published"])

    # Splitting into two dataframes: with or without transcript
    criteria = df["transcript"].isna()
    df_notranscript = df[criteria]
    df = df[~criteria]

    # Removing records with transcript shorter than 100 characters
    df = df[(df["transcript"].str.len() >= 100)]

    return df
