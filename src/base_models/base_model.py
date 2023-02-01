from typing import Dict

class GameBaseModel:
    def __init__(self, base_doc: Dict) -> None:
        self.game = base_doc
        self.game_url = self.game["game_url"]
        self.datetime = self.game["datetime"]
        self.legaue = self.game["league"]
        self.home_team = self.game["home"]
        self.away_team = self.game["away"]

    def btts_attrs(self):
        self.odds_btts = self.game["odds"]["odds_btts_yes"]
        del self.game
        return self
