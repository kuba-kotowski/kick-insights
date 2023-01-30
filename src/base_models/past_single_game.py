from typing import Dict
from pprint import pprint


class PastSingleGameModel:
    def __init__(self, base_doc: Dict, team: str = None) -> None:
        self.doc = base_doc # nested dictionary format
        self.events = self.doc["events"]
        self.stats = self.doc["stats"]
        self.team = team

        # self.referee = self.doc["referee"]
        # self.attendance = self.doc["attendance"]

    def process(self):
        self.find_side()
        self.get_all_info()
        del self.doc
        if self.events:
            self.events = True
        else:
            self.events = False
        if self.stats:
            self.stats = True
        else:
            self.stats = False
        # return vars(self)
        d = vars(self)
        team_side_keys = [key for key in d.keys() if not key.endswith(("home_team", "away_team")) and key.endswith(("_team", "_opponent"))]
        if not self.team:
            del self.team
            for key in team_side_keys:
                del self.__dict__[key]
        return self

    def find_side(self):
        if self.team is None:
            self.team_side = None
        elif self.doc["home"].lower().find(self.team.lower()) != -1:
            self.team_side = "home"
        elif self.doc["away"].lower().find(self.team.lower()) != -1:
            self.team_side = "away"
        else:
            raise Exception("Wrong team name provided")

    def get_all_info(self):
        self.get_basic_info()
        self.get_odds()
        self.get_winner()
        self.get_goals()
        self.get_first_goal_info()
        self.get_possesion()
        self.get_offsides()
        self.get_corners()
        self.get_yellow_cards()
        self.get_fouls()

    def get_basic_info(self):
        self.game_url = self.doc["game_url"]
        self.home_team = self.doc["home"]
        self.away_team = self.doc["away"]
        self.league = self.doc["league"]
        self.round = self.doc["round"]
        if type(self.doc["datetime"]) == dict:
            self.datetime = datetime.fromtimestamp(int(self.doc["datetime"]["$date"]["$numberLong"]) / 1e3)
        else:
            self.datetime = self.doc["datetime"]
        self.time = self.datetime.time()

    def get_odds(self):
        self.odds_draw = self.doc["odds_draw"]
        self.odds_home_team = self.doc["odds_home"]
        self.odds_away_team = self.doc["odds_away"]
        if self.team_side and self.team_side == "home":
            self.odds_team = self.odds_home_team
            self.odds_opponent = self.odds_away_team
        elif self.team_side and self.team_side == "away":
            self.odds_team = self.odds_away_team
            self.odds_opponent = self.odds_home_team
        else:
            self.odds_team = None
            self.opponent_team = None
        
        if self.doc.get("odds"):
            self.odds_over15 = self.doc["odds"]["odds_over_15"]
            self.odds_under15 = self.doc["odds"]["odds_under_15"]
            self.odds_over25 = self.doc["odds"]["odds_over_25"]
            self.odds_under25 = self.doc["odds"]["odds_under_25"]
        else:
            self.odds_over15 = None
            self.odds_under15 = None
            self.odds_over25 = None
            self.odds_under25 = None

    def get_winner(self):
        if self.doc["goals_home"] == self.doc["goals_away"]:
            self.winner = "draw"
            self.odds_winner = self.doc["odds_draw"]
        elif self.doc["goals_home"] > self.doc["goals_away"]:
            self.winner = "home"
            self.odds_winner = self.odds_home_team
        else:
            self.winner = "away"
            self.odds_winner = self.odds_away_team
        
        if self.team_side and self.winner == "draw":
            self.team_result = "draw"
        elif self.team_side and self.winner == self.team_side:
            self.team_result = "win"
        elif self.team_side:
            self.team_result = "lose"
        else:
            self.team_result = None

    def get_goals(self):
        # fields required: goals_home, goals_away
        self.goals_home_team = self.doc["goals_home"]
        self.goals_away_team = self.doc["goals_away"]
        self.goals_total = self.goals_home_team + self.goals_away_team
        if self.goals_total < 2:
            self.over15 = False
            self.over25 = False
        elif self.goals_total < 3:
            self.over15 = True
            self.over25 = False
        else:
            self.over15 = True
            self.over25 = True
        if self.goals_home_team != 0 and self.goals_away_team != 0:
            self.btts = True
        else:
            self.btts = False
        
        if not self.team_side:
            self.goals_team = None
            self.goals_opponent = None
            self.goals_team = None
            self.team_cleansheet = None
            self.team_scored = None
            return 0 

        if self.team_side == "home":
            self.goals_team = self.goals_home_team
            self.goals_opponent = self.goals_away_team
        else:
            self.goals_team = self.goals_away_team
            self.goals_opponent = self.goals_home_team
        
        if self.goals_team == self.goals_total:
            self.team_cleansheet = True
        else:
            self.team_cleansheet = False
        
        if self.goals_team > 0:
            self.team_scored = True
        else:
            self.team_scored = False

    def get_first_goal_info(self):
        # fields required: events
        if not self.events:
            self.first_goal_time = None
            self.first_goal_team = None
            self.team_first_goal_time = None
            self.team_first_scored = None
            return 0

        goals = [event for event in self.events if event["event_name"] in ["goal", "own_goal"]]
        goals_home_team = [event for event in self.events if event["event_name"] in ["goal", "own_goal"] and event["team"]=="home"]
        goals_away_team = [event for event in self.events if event["event_name"] in ["goal", "own_goal"] and event["team"]=="away"]
        if goals:
            self.first_goal_time = goals[0]["time"]
            self.first_goal_team = goals[0]["team"]
        else:
            self.first_goal_time = -1
            self.first_goal_team = None
        
        if not self.team_side:
            self.team_first_goal_time = None
            self.team_first_scored = None
            return 0

        if self.team_side == "home" and goals_home_team:
            self.team_first_goal_time = goals_home_team[0]["time"]
        elif self.team_side == "away" and goals_away_team:
            self.team_first_goal_time = goals_away_team[0]["time"]
        else:
            self.team_first_goal_time = -1
        
        if self.team_first_goal_time != -1 and self.team_first_goal_time <= self.first_goal_time:
            self.team_first_scored = True
        elif self.team_first_goal_time != -1:
            self.team_first_scored = False
        else:
            self.team_first_scored = None

    def get_possesion(self):
        # fields required: stats
        if not self.stats or "ball_possession" not in [stat["stat_name"] for stat in self.stats]:
            self.possesion_home_team = None
            self.possesion_away_team = None
            self.possesion_team = None
            self.possesion_opponent = None
            return 0
        possesion = [stat for stat in self.stats if stat["stat_name"]=="ball_possession"][0]
        self.possesion_home_team = possesion["home"]
        self.possesion_away_team = possesion["away"]
        if self.team_side:
            self.possesion_team = possesion[self.team_side]
            self.possesion_opponent = round(1 - self.possesion_team, 2)
        else:
            self.possesion_team = None
            self.possesion_opponent = None 

    def get_offsides(self):
        # fields required: stats
        if not self.stats or "offsides" not in [stat["stat_name"] for stat in self.stats]:
            self.offsides_home_team = None
            self.offsides_away_team = None
            self.offsides_total = None
            self.offsides_team = None
            self.offsides_opponent = None
            return 0
        offsides = [stat for stat in self.stats if stat["stat_name"]=="offsides"][0]
        self.offsides_home_team = offsides["home"]
        self.offsides_away_team = offsides["away"]
        self.offsides_total = self.offsides_home_team + self.offsides_away_team
        if self.team_side:
            self.offsides_team = offsides[self.team_side]
            self.offsides_opponent = self.offsides_total - self.offsides_team
        else:
            self.offsides_team = None
            self.offsides_opponent = None

    def get_corners(self):
        # fields required: stats
        if not self.stats or "corner_kicks" not in [stat["stat_name"] for stat in self.stats]:
            self.corners_home_team = None
            self.corners_away_team = None
            self.corners_total = None
            self.corners_team = None
            self.corners_opponent = None
            return 0
        corners = [stat for stat in self.stats if stat["stat_name"]=="corner_kicks"][0]
        self.corners_home_team = corners["home"]
        self.corners_away_team = corners["away"]
        self.corners_total = self.corners_home_team + self.corners_away_team
        if self.team_side:
            self.corners_team = corners[self.team_side]
            self.corners_opponent = self.corners_total - self.corners_team
        else:
            self.corners_team = None
            self.corners_opponent = None

    def get_yellow_cards(self):
        # fields required: events
        if not self.events:
            self.yc_home_team = None
            self.yc_away_team = None
            self.yc_total = None
            self.yc_team = None
            self.yc_opponent = None
            return 0
        yc = [event for event in self.events if event["event_name"] in ["yellow_card", "yellow_red_card"]]
        self.yc_total = len(yc)
        self.yc_home_team = len([event for event in yc if event["team"] == "home"])
        self.yc_away_team = len([event for event in yc if event["team"] == "away"])
        if self.team_side:
            self.yc_team = len([event for event in yc if event["team"] == self.team_side])
            self.yc_opponent = self.yc_total - self.yc_team
        else:
            self.yc_team = None
            self.yc_opponent = None        

    def get_fouls(self):
        # fields required: stats
        if not self.stats or "fouls" not in [stat["stat_name"] for stat in self.stats]:
            self.fouls_home_team = None
            self.fouls_away_team = None
            self.fouls_total = None
            self.fouls_team = None
            self.fouls_opponent = None
            return 0
        fouls = [event for event in self.stats if event["stat_name"] == "fouls"][0]
        self.fouls_home_team = fouls["home"]
        self.fouls_away_team = fouls["away"]
        self.fouls_total = self.fouls_home_team + self.fouls_away_team
        if self.team_side:
            self.fouls_team = fouls[self.team_side]
            self.fouls_opponent = self.fouls_total - self.fouls_team
        else:
            self.fouls_team = None
            self.fouls_opponent = None         
