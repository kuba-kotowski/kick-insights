import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, List, Union
import os

load_dotenv()

URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

def connect_to_collection(uri, db_name, collection_name):
    if uri and db_name:
        try:
            mongo_db = MongoClient(uri)[db_name]
        except: 
            raise Exception("Cannot connect to provided mongodb")
        if collection_name in mongo_db.list_collection_names():
            return mongo_db[collection_name]
        else:
            raise Exception("Invalid collection name")
    else:
        raise Exception("Please provide connection string and db name")


def get_single_doc(collection, doc_id) -> Dict:
    doc = list(collection.find({"_id": ObjectId(doc_id)}))
    if doc:
        return doc[0]
    else:
        raise Exception("Document not found in collection")


def get_past_n_games(collection, doc: Dict, n_games, type):
    # doc: base game (dict) - then returning past games from home/away teams from this game
    home_team = doc.get("home")
    away_team = doc.get("away")
    datetime = doc.get("datetime")

    if type=="home":
        return list(collection.find({
            "datetime": {"$lt": datetime}, 
            "events": {"$ne": []},
            "stats": {"$ne": []},
            "odds.odds_btts_yes": {"$exists": True},
            "$or": [{"home": home_team}, {"away": home_team}], 
            "league": {"$nin": ["Club Friendly"]}
        }).sort("datetime", -1).limit(n_games))
    elif type=="away":
        return list(collection.find({
            "datetime": {"$lt": datetime}, 
            "events": {"$ne": []},
            "stats": {"$ne": []},
            "odds.odds_btts_yes": {"$exists": True},
            "$or": [{"home": away_team}, {"away": away_team}], 
            "league": {"$nin": ["Club Friendly"]}
        }).sort("datetime", -1).limit(n_games))
    elif type=="h2h":
        return list(collection.find({
            "datetime": {"$lt": datetime}, 
            "events": {"$ne": []},
            "stats": {"$ne": []},
            "$or": [
                {"home": home_team, "away": away_team},
                {"home": away_team, "away": home_team}
                ]
            }).sort("datetime", -1).limit(n_games))


def get_team_latest_n_games(collection, team: str, n_games: float, team_side: str = "all"):
    if team_side not in ["home", "away", "all"]:
        raise Exception("Team side needs to be home/away/all")
    filters = {
        "home": {
            "home": team, 
            "events": {"$ne": []},
            "stats": {"$ne": []},
            "league": {"$ne": "Club Friendly"}
        },
        "away": {
            "away": team, 
            "events": {"$ne": []},
            "stats": {"$ne": []},
            "league": {"$ne": "Club Friendly"}
        },
        "all": {
            "$or": [
                {"home": team}, 
                {"away": team}
                ], 
            "events": {"$ne": []},
            "stats": {"$ne": []},
            "league": {"$ne": "Club Friendly"}
        }
    }
    return list(collection.find(filters[team_side]).sort("datetime", -1).limit(n_games))
