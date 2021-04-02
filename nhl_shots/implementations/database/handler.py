import json

class database:
    def __init__(self, api, games_file, old_bets_file, team_ids_file, player_ids_file):
        self.games = self.load(games_file)
        self.old_bets = self.load(old_bets_file)
        self.team_ids = self.load(team_ids_file)
        self.player_ids = self.load(player_ids_file)
        self.games_file_path = games_file
        self.old_bets_file_path = old_bets_file
        self.team_ids_file_path = team_ids_file
        self.player_ids_file_path = player_ids_file

    def save(self):
        try:
            with open(self.games_file_path, "w") as f:
                f.write(json.dumps(self.games))
        except Exception as e:
            print("Something went wrong when saving database...")

        try:
            with open(self.old_bets_file_path, "w") as f:
                f.write(json.dumps(self.old_bets))
        except Exception as e:
            print("Something went wrong when saving database...")

        try:
            with open(self.team_ids_file_path, "w") as f:
                f.write(json.dumps(self.team_ids))
        except Exception as e:
            print("Something went wrong when saving database...")

        try:
            with open(self.player_ids_file_path, "w") as f:
                f.write(json.dumps(self.player_ids))
        except Exception as e:
            print("Something went wrong when saving database...")


    def load(self, path):
        try:
            with open(path) as json_file:
                return json.load(json_file)
        except Exception as e:
            print("Could not find file {}, starting over with an empty one.".format(path))
            return {}