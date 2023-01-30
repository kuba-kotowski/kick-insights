from typing import Union, List, Dict
from .past_single_game import PastSingleGameModel


class PastGamesModel:
    # List of past games for given team (team is provided in SingleGameDetails TODO: maybe providing here) 
    def __init__(self, past_games: List[Dict], team: str = None, team_side: str = None) -> None:
        """
        past_games - list of dictionaries containing game details
        team_side - if needed to calculate trends based on the team's side (if Team A plays next game away, then there will be trends calculated for Team A only playing away)
        """
        self.team = team
        if self.team:
            self.team_side = self.check_team_side(team_side)
        else:
            self.team_side = None

        self.past_games = [PastSingleGameModel(base_doc=game, team=team).process() for game in past_games]
        self.past_games_number = len(self.past_games)
        self.past_games_team_side = [game for game in self.past_games if game.team_side == team_side] # if team is playing home then we analyze past games home
        self.past_games_number_team_side = len(self.past_games_team_side)

    def process(self):
        self.get_all_info()
        del self.past_games
        del self.past_games_team_side
        
        if not self.team_side:
            del self.team_side
            del self.past_games_number_team_side
        if not self.team:
            del self.team
        
        return self

    # def get_h2h_ratio(self, home_team=None, away_team=None):
    #     # Calculating h2h ratio - it aims to represent the different between quality of two teams
    #     teams = []
    #     [teams.extend([game.home_team, game.away_team]) for game in self.past_games]
    #     teams = list(set(teams))
    #     if len(teams) != 2 or None in teams:
    #         raise Exception("Only H2H games are accepted - found different teams among games' home/away teams")
    #     elif home_team and away_team and (home_team not in teams or away_team not in teams):
    #         raise Exception("If providing team sides then they need to match with h2h past games")

    #     if home_team and away_team:
    #         winners = [vars(game)[f"{game.winner}_team"].replace(home_team, "-1").replace(away_team, "1") if game.winner != "draw" else 0 for game in self.past_games]
    #         winners = [int(winner) for winner in winners]
    #         return self.calculate_average(winners)
    #     else:
    #         winners = [vars(game)[f"{game.winner}_team"].replace(teams[0], "-1").replace(teams[1], "1") if game.winner != "draw" else 0 for game in self.past_games]
    #         winners = [int(winner) for winner in winners]
    #         return abs(self.calculate_average(winners))

    @staticmethod
    def check_team_side(team_side):
        if team_side not in ["home", "away", None]:
            raise Exception("Team side must be either home/away or None")
        else:
            return team_side

    def get_all_info(self):
        self.get_btts()
        self.get_goals()
        self.get_yellow_cards()
        self.get_corners()
        self.get_offsides()
        if self.team:
            self.get_team_results()

    def round_digits(self, number: Union[int, float]):
        return "{:.2f}".format(number)

    def calculate_percentage(self, number: Union[int, float], divisor: str):
        if number == 0:
            return 0
        divisors = {
            "total": self.past_games_number,
            "team_side": self.past_games_number_team_side
        }
        return float(self.round_digits(number/divisors[divisor]))

    def calculate_average(self, numbers: List[Union[int, float]]):
        if numbers:
            return float(self.round_digits(sum(numbers)/len(numbers)))
        else:
            return 0

    # def calculate_games_timedelta(self, next_game: datetime):
    #     last_game = self.docs[0].game_time
    #     return (next_game-last_game).days

    def get_btts(self):
        btts_games = len([game for game in self.past_games if game.btts])
        btts_games_team_side = len([game for game in self.past_games_team_side if game.btts])

        self.goals_total_btts = self.calculate_percentage(btts_games, "total")

        if self.team:
            self.goals_team_scored = self.calculate_percentage(len([game for game in self.past_games if game.team_scored]), "total")
            self.goals_team_cleansheet = self.calculate_percentage(len([game for game in self.past_games if game.team_cleansheet]), "total")
        
        if self.team_side:
            self.goals_total_btts_team_side = self.calculate_percentage(btts_games_team_side, "team_side")
            self.goals_team_scored_team_side = self.calculate_percentage(len([game for game in self.past_games_team_side if game.team_scored]), "team_side")
            self.goals_team_cleansheet_team_side = self.calculate_percentage(len([game for game in self.past_games_team_side if game.team_cleansheet]), "team_side")


    def get_goals(self):
        self.goals_total_avg = self.calculate_average([game.goals_total for game in self.past_games])
        if self.team:
            self.goals_team_avg = self.calculate_average([game.goals_team for game in self.past_games])
            # self.goals_avg_team_lost = self.calculate_average([game.goals_opponent for game in self.past_games])
        if self.team_side:
            self.goals_total_avg_team_side = self.calculate_average([game.goals_total for game in self.past_games_team_side])
            self.goals_team_avg_team_side = self.calculate_average([game.goals_team for game in self.past_games_team_side])
            # self.goals_avg_team_lost_team_side = self.calculate_average([game.goals_opponent for game in self.past_games_team_side])

        over15 = len([game for game in self.past_games if game.goals_total > 1.5])
        over25 = len([game for game in self.past_games if game.goals_total > 2.5])
        over15_team_side = len([game for game in self.past_games_team_side if game.goals_total > 1.5])
        over25_team_side = len([game for game in self.past_games_team_side if game.goals_total > 2.5])

        self.goals_total_over15 = self.calculate_percentage(over15,"total")
        self.goals_total_over25 = self.calculate_percentage(over25, "total")
        if self.team_side:
            self.goals_total_over15_team_side = self.calculate_percentage(over15_team_side,"team_side")
            self.goals_total_over25_team_side = self.calculate_percentage(over25_team_side, "team_side")

    def get_yellow_cards(self):
        self.yc_total_avg = self.calculate_average([game.yc_total for game in self.past_games])
        if self.team:
            self.yc_team_avg = self.calculate_average([game.yc_team for game in self.past_games])
        if self.team_side:
            self.yc_total_avg_team_side = self.calculate_average([game.yc_total for game in self.past_games_team_side])
            self.yc_team_avg_team_side = self.calculate_average([game.yc_team for game in self.past_games_team_side])

        self.yc_total_over25 = self.calculate_percentage(len([game for game in self.past_games if game.yc_total > 2.5]), "total")
        self.yc_total_over35 = self.calculate_percentage(len([game for game in self.past_games if game.yc_total > 3.5]), "total")
        self.yc_total_over45 = self.calculate_percentage(len([game for game in self.past_games if game.yc_total > 4.5]), "total")

        if self.team:
            self.yc_team_over15 = self.calculate_percentage(len([game for game in self.past_games if game.yc_team > 1.5]), "total")
            self.yc_team_over25 = self.calculate_percentage(len([game for game in self.past_games if game.yc_team > 2.5]), "total")
            self.yc_team_over35 = self.calculate_percentage(len([game for game in self.past_games if game.yc_team > 3.5]), "total")

            self.yc_opponent_over15 = self.calculate_percentage(len([game for game in self.past_games if game.yc_opponent > 1.5]), "total")
            self.yc_opponent_over25 = self.calculate_percentage(len([game for game in self.past_games if game.yc_opponent > 2.5]), "total")
            self.yc_opponent_over35 = self.calculate_percentage(len([game for game in self.past_games if game.yc_opponent > 3.5]), "total")

    def get_corners(self):
        self.corners_total_avg = self.calculate_average([game.corners_total for game in self.past_games])
        if self.team:
            self.corners_team_avg = self.calculate_average([game.corners_team for game in self.past_games])
        if self.team_side:
            self.corners_total_avg_team_side = self.calculate_average([game.corners_total for game in self.past_games_team_side])
            self.corners_team_avg_team_side = self.calculate_average([game.corners_team for game in self.past_games_team_side])

        self.corners_total_over55 = self.calculate_percentage(len([game for game in self.past_games if game.corners_total > 5.5]), "total")
        self.corners_total_over65 = self.calculate_percentage(len([game for game in self.past_games if game.corners_total > 6.5]), "total")
        self.corners_total_over75 = self.calculate_percentage(len([game for game in self.past_games if game.corners_total > 7.5]), "total")
        self.corners_total_over85 = self.calculate_percentage(len([game for game in self.past_games if game.corners_total > 8.5]), "total")
        self.corners_total_over95 = self.calculate_percentage(len([game for game in self.past_games if game.corners_total > 9.5]), "total")
        self.corners_total_over105 = self.calculate_percentage(len([game for game in self.past_games if game.corners_total > 10.5]), "total")

        if self.team:
            self.corners_team_over25 = self.calculate_percentage(len([game for game in self.past_games if game.corners_team > 2.5]), "total")
            self.corners_team_over35 = self.calculate_percentage(len([game for game in self.past_games if game.corners_team > 3.5]), "total")
            self.corners_team_over45 = self.calculate_percentage(len([game for game in self.past_games if game.corners_team > 4.5]), "total")
            self.corners_team_over55 = self.calculate_percentage(len([game for game in self.past_games if game.corners_team > 5.5]), "total")
            self.corners_team_over65 = self.calculate_percentage(len([game for game in self.past_games if game.corners_team > 6.5]), "total")

            self.corners_opponent_over15 = self.calculate_percentage(len([game for game in self.past_games if game.corners_opponent > 1.5]), "total")
            self.corners_opponent_over25 = self.calculate_percentage(len([game for game in self.past_games if game.corners_opponent > 2.5]), "total")
            self.corners_opponent_over35 = self.calculate_percentage(len([game for game in self.past_games if game.corners_opponent > 3.5]), "total")

    def get_offsides(self):
        self.offsides_total_avg = self.calculate_average([game.offsides_total for game in self.past_games])
        if self.team:
            self.offsides_team_avg = self.calculate_average([game.offsides_team for game in self.past_games])
        if self.team_side:
            self.offsides_total_avg_team_side = self.calculate_average([game.offsides_total for game in self.past_games_team_side])
            self.offsides_team_avg_team_side = self.calculate_average([game.offsides_team for game in self.past_games_team_side])

        self.offsides_total_over25 = self.calculate_percentage(len([game for game in self.past_games if game.offsides_total > 2.5]), "total")
        self.offsides_total_over35 = self.calculate_percentage(len([game for game in self.past_games if game.offsides_total > 3.5]), "total")
        self.offsides_total_over45 = self.calculate_percentage(len([game for game in self.past_games if game.offsides_total > 4.5]), "total")

        if self.team:
            self.offsides_team_over15 = self.calculate_percentage(len([game for game in self.past_games if game.offsides_team > 1.5]), "total")
            self.offsides_team_over25 = self.calculate_percentage(len([game for game in self.past_games if game.offsides_team > 2.5]), "total")
            self.offsides_team_over35 = self.calculate_percentage(len([game for game in self.past_games if game.offsides_team > 3.5]), "total")

            self.offsides_opponent_over15 = self.calculate_percentage(len([game.offsides_opponent for game in self.past_games if game.offsides_opponent > 1.5]), "total")
            self.offsides_opponent_over25 = self.calculate_percentage(len([game.offsides_opponent for game in self.past_games if game.offsides_opponent > 2.5]), "total")
            self.offsides_opponent_over35 = self.calculate_percentage(len([game.offsides_opponent for game in self.past_games if game.offsides_opponent > 3.5]), "total")

    def get_fouls(self):
        self.fouls_total_avg = self.calculate_average([game.fouls_total for game in self.past_games])
        if self.team:
            self.fouls_team_avg = self.calculate_average([game.fouls_team for game in self.past_games])
        if self.team_side:
            self.fouls_total_avg_team_side = self.calculate_average([game.fouls_total for game in self.past_games_team_side])
            self.fouls_team_avg_team_side = self.calculate_average([game.fouls_team for game in self.past_games_team_side])

        self.fouls_total_over25 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_total > 2.5]), "total")
        self.fouls_total_over35 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_total > 3.5]), "total")
        self.fouls_total_over45 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_total > 4.5]), "total")

        if self.team:
            self.fouls_team_over15 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_team > 1.5]), "total")
            self.fouls_team_over25 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_team > 2.5]), "total")
            self.fouls_team_over35 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_team > 3.5]), "total")

            self.fouls_opponent_over15 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_opponent > 1.5]), "total")
            self.fouls_opponent_over25 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_opponent > 2.5]), "total")
            self.fouls_opponent_over35 = self.calculate_percentage(len([game for game in self.past_games if game.fouls_opponent > 3.5]), "total")

    def get_team_results(self):
        team_form = [game.team_result for game in self.past_games]
        team_form_team_side = [game.team_result for game in self.past_games_team_side]

        self.result_team_won_total = self.calculate_percentage(len([result for result in team_form if result == "win"]), "total")
        self.result_team_not_lost_total = self.calculate_percentage(len([result for result in team_form if result != "lose"]), "total")
        self.result_team_lost_total = self.calculate_percentage(len([result for result in team_form if result == "lose"]), "total")
        if self.team_side:
            self.result_team_won_team_side = self.calculate_percentage(len([result for result in team_form_team_side if result == "win"]), "team_side")
            self.result_team_not_lost_team_side = self.calculate_percentage(len([result for result in team_form_team_side if result != "lose"]), "team_side")
            self.result_team_lost_total_team_side = self.calculate_percentage(len([result for result in team_form_team_side if result == "lose"]), "team_side")

        if "lose" in team_form:
            self.result_team_not_lost_consecutive_games = team_form.index("lose")
        else:
            self.result_team_not_lost_consecutive_games = len(team_form)

        if self.team_side and "lose" in team_form_team_side:
            self.result_team_not_lost_consecutive_games_team_side = team_form_team_side.index("lose")
        else:
            self.result_team_not_lost_consecutive_games_team_side = len(team_form_team_side)
