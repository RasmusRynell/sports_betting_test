import json
import msgpack

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
            with open(self.games_file_path, "wb") as f:
                f.write(msgpack.packb(self.games))
        except Exception as e:
            print("Something went wrong when saving games database...")

        try:
            with open(self.old_bets_file_path, "wb") as f:
                f.write(msgpack.packb(self.old_bets))
        except Exception as e:
            print("Something went wrong when saving the old bets database...")

        try:
            with open(self.team_ids_file_path, "wb") as f:
                f.write(msgpack.packb(self.team_ids))
        except Exception as e:
            print("Something went wrong when saving the team ids database...")

        try:
            with open(self.player_ids_file_path, "wb") as f:
                f.write(msgpack.packb(self.player_ids))
        except Exception as e:
            print("Something went wrong when saving the player ids database...")


    def load(self, path):
        try:
            with open(path, "rb") as f:
                return msgpack.unpackb(f.read())
        except Exception as e:
            print("Could not find file {}, starting over with an empty one.".format(path))
            return {}
