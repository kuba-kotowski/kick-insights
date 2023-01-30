from typing import List, Dict
from pprint import pprint

from base_models.base_model import GameBaseModel
from base_models.past_games import PastGamesModel

from utility_functions.mongodb_functions import get_team_latest_n_games, get_single_doc, connect_to_collection
from utility_functions.mongodb_functions import URI, DB_NAME


class BttsModel(GameBaseModel):
    def __init__(self, base_doc, past_games_home: List[Dict], past_games_away: List[Dict]) -> None:
        super().__init__(base_doc)
        self.btts_attrs() # get info only for btts
        self.past_games_home = PastGamesModel(past_games_home, team=self.home_team, team_side="home").process()
        self.past_games_away = PastGamesModel(past_games_away, team=self.away_team, team_side="away").process()   

    def process(self):
        self.home_team_btts_last_n_games = self.past_games_home.goals_total_btts
        self.away_team_btts_last_n_games = self.past_games_away.goals_total_btts
        self.home_team_scored_last_n_games = self.past_games_home.goals_team_scored
        self.away_team_scored_last_n_games = self.past_games_away.goals_team_scored
        self.home_team_cleansheet_last_n_games = self.past_games_home.goals_team_cleansheet
        self.away_team_cleansheet_last_n_games = self.past_games_away.goals_team_cleansheet
        self.home_team_avg_goals_last_n_games = self.past_games_home.goals_team_avg
        self.away_team_avg_goals_last_n_games = self.past_games_away.goals_team_avg
        self.home_team_goals_total_over15_last_n_games = self.past_games_home.goals_total_over15
        self.away_team_goals_total_over15_last_n_games = self.past_games_away.goals_total_over15
        self.home_team_goals_total_over25_last_n_games = self.past_games_home.goals_total_over25
        self.away_team_goals_total_over25_last_n_games = self.past_games_away.goals_total_over25

        del self.past_games_home
        del self.past_games_away
        return self


if __name__ == "__main__":
    future_games = connect_to_collection(URI, DB_NAME, "temp_future_details")
    past_games = connect_to_collection(URI, DB_NAME, "football_main_v2")

    base_doc = get_single_doc(future_games, "63d6cc01e5df73b5003b1042") # Udinese vs Verona
    past_games_home = get_team_latest_n_games(past_games, "Udinese", 20, "home")
    past_games_away = get_team_latest_n_games(past_games, "Verona", 20, "away")

    model = BttsModel(base_doc, past_games_home, past_games_away)
    pprint(vars(model.process()))