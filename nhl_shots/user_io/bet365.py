import clipboard
import json
import Settings


def get_from_clipboard():
    text = clipboard.paste()  # text will have the content of clipboard
    text = text.replace("\r", "")
    new_list = text.split("\n")
    everything = [x for x in new_list if x != ' ' and x != '']

    current_game = ""
    current_game_time = ""
    current_game_team_one = ""
    current_game_team_two = ""
    current_player = ""


    bet_index = 0

    is_under = False

    results = {}

    for sentence in everything:
        if '@' in sentence:
            results[sentence] = {}
            current_game = sentence
        elif ':' in sentence:
            results[current_game]["Date-time"] = sentence
        elif '.' in sentence and ('0' in sentence or '1' in sentence or '2' in sentence or '3' in sentence):
            if "1.5" == sentence or "2.5" == sentence or "3.5" == sentence:
                results[current_game]["bet365-stat"][list(results[current_game]["bet365-stat"].keys())[bet_index]]["over-under"] = sentence
            elif is_under:
                results[current_game]["bet365-stat"][list(results[current_game]["bet365-stat"].keys())[bet_index]]["under"] = sentence
                bet_index += 1
            else:
                results[current_game]["bet365-stat"][list(results[current_game]["bet365-stat"].keys())[bet_index]]["over"] = sentence
                bet_index += 1
        else:
            if "Över" in sentence:
                bet_index = 0
                is_under = False
            elif "Under" in sentence:
                bet_index = 0
                is_under = True
            elif sentence.lower() in Settings.teams_translate.keys():
                results[current_game]["bet365-stat"][current_player]["team"] = sentence
            else:
                if "bet365-stat" not in results[current_game]:
                    results[current_game]["bet365-stat"] = {}
                results[current_game]["bet365-stat"][sentence] = {}
                current_player = sentence

    for key, value in results.items():
        (value["team_one"], value["team_two"]) = key.split("@")
        value["team_one"] = value["team_one"][:-1]
        value["team_two"] = value["team_two"][1:]

    return results
