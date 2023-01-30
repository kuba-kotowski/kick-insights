from pprint import pprint

from base_models.past_single_game import PastSingleGameModel
from base_models.past_games import PastGamesModel

from utility_functions.mongodb_functions import connect_to_collection, get_single_doc, get_past_n_games, get_team_latest_n_games
from utility_functions.mongodb_functions import URI, DB_NAME

collection = connect_to_collection(URI, DB_NAME, "football_main_v2")

# 1) PASTSINGLEGAMEMODEL:
doc = get_single_doc(collection, "63c995fbbe87ac1137ada688")

# WITHOUT SPECYFING THE TEAM NAME:
game_uni = PastSingleGameModel(doc)
pprint(vars(game_uni.process()))    

# SPECYFING TEAM NAME - to get team-oriented details:
game = PastSingleGameModel(doc, "Juventus")
pprint(vars(game.process()))



# 2) PASTGAMESMODEL:
past_games = get_team_latest_n_games(collection, team="Juventus", n_games=20)

# WITHOUT SPECYFING TEAM:
model_uni = PastGamesModel(past_games=past_games)
pprint(vars(model_uni.process()))

# SPECYFING TEAM - getting team-oriented trends
model = PastGamesModel(past_games=past_games, team="Juventus")
pprint(vars(model.process()))

# SPECYFING TEAM & TEAM SIDE - getting team-oriented & side-oriented (playing home/away) trends
model = PastGamesModel(past_games=past_games, team="Juventus", team_side="home")
pprint(vars(model.process()))
