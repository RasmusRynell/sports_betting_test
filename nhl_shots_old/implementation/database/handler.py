import json

class database:
    def __init__(self, api, games_file, old_bets_file):
        self.games = self.load_database(games_file)
        self.old_bets = self.load_database(old_bets_file)
        self.games_file_path = games_file
        self.old_bets_file = old_bets_file

    def save_database(self, path):
        try:
            with open(path, "w") as f:
                f.write(json.dumps(self.games_file))
        except:
            print("Something went wrong when saving database...")

        try:
            with open(path, "w") as f:
                f.write(json.dumps(old_bets_file))
        except:
            print("Something went wrong when saving database...")


    def load_database(self, path):
        try:
            with open(path) as json_file:
                return json.load(self.json_file)
        except:
            print("Could not find file {}, starting over with an empty one.".format(path))
            return {}