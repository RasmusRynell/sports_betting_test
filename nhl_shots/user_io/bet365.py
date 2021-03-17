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



'''
BOS Bruins @ PIT Penguins
Ons 17 mar 00: 08

Patrice Bergeron
BOS Bruins
Brad Marchand
BOS Bruins
Charlie McAvoy
BOS Bruins
David Pastrnak
BOS Bruins
Sidney Crosby
PIT Penguins
Jake Guentzel
PIT Penguins
Kris Letang
PIT Penguins
Evgeni Malkin
PIT Penguins
Bryan Rust
PIT Penguins
Över
2.5
1.71
2.5
2.00
1.5
1.71
3.5
1.83
2.5
1.83
2.5
1.80
2.5
1.90
2.5
1.90
2.5
1.71
Under
2.5
2.00
2.5
1.71
1.5
2.00
3.5
1.83
2.5
1.83
2.5
1.86
2.5
1.76
2.5
1.76
2.5
2.00
BUF Sabres @ NJ Devils
Ons 17 mar 00: 08

Rasmus Dahlin
BUF Sabres
Taylor Hall
BUF Sabres
Victor Olofsson
BUF Sabres
Sam Reinhart
BUF Sabres
Rasmus Ristolainen
BUF Sabres
Jack Hughes
NJ Devils
Kyle Palmieri
NJ Devils
P.K. Subban
NJ Devils
Över
1.5
1.62
2.5
1.80
2.5
2.25
2.5
2.30
1.5
1.62
2.5
2.20
2.5
1.90
1.5
1.52
Under
1.5
2.20
2.5
1.86
2.5
1.57
2.5
1.55
1.5
2.20
2.5
1.62
2.5
1.76
1.5
2.40
NY Islanders @ WAS Capitals
Ons 17 mar 00: 08

Mathew Barzal
NY Islanders
Jordan Eberle
NY Islanders
Brock Nelson
NY Islanders
Ryan Pulock
NY Islanders
John Carlson
WAS Capitals
Alexander Ovechkin
WAS Capitals
Över
2.5
2.20
2.5
2.20
2.5
2.20
1.5
1.66
2.5
2.20
3.5
1.71
Under
2.5
1.62
2.5
1.62
2.5
1.62
1.5
2.10
2.5
1.62
3.5
2.00
CAR Hurricanes @ DET Red Wings
Ons 17 mar 00: 38

Sebastian Antero Aho
CAR Hurricanes
Dougie Hamilton
CAR Hurricanes
Andrei Svechnikov
CAR Hurricanes
Dylan Larkin
DET Red Wings
Anthony Mantha
DET Red Wings
Över
2.5
1.76
2.5
1.57
2.5
1.71
2.5
1.55
2.5
2.00
Under
2.5
1.90
2.5
2.25
2.5
2.00
2.5
2.30
2.5
1.71
ARZ Coyotes @ MIN Wild
Ons 17 mar 01: 08

Jakob Chychrun
ARZ Coyotes
Christian Dvorak
ARZ Coyotes
Conor Garland
ARZ Coyotes
Clayton Keller
ARZ Coyotes
Phil Kessel
ARZ Coyotes
Nick Schmaltz
ARZ Coyotes
Matt Dumba
MIN Wild
Joel Eriksson Ek
MIN Wild
Kevin Fiala
MIN Wild
Över
2.5
2.10
1.5
1.76
2.5
2.00
2.5
2.30
1.5
1.57
1.5
1.62
2.5
2.20
2.5
2.30
2.5
1.55
Under
2.5
1.66
1.5
1.90
2.5
1.71
2.5
1.55
1.5
2.25
1.5
2.20
2.5
1.62
2.5
1.55
2.5
2.30
TB Lightning @ DAL Stars
Ons 17 mar 01: 38

Victor Hedman
TB Lightning
Brayden Point
TB Lightning
Steven Stamkos
TB Lightning
Över
2.5
2.10
2.5
2.00
2.5
1.76
Under
2.5
1.66
2.5
1.71
2.5
1.90
ANA Ducks @ COL Avalanche
Ons 17 mar 02: 08

Ryan Getzlaf
ANA Ducks
Rickard Rakell
ANA Ducks
Jakob Silfverberg
ANA Ducks
Nazem Kadri
COL Avalanche
Gabriel Landeskog
COL Avalanche
Nathan MacKinnon
COL Avalanche
Mikko Rantanen
COL Avalanche
Över
1.5
1.80
2.5
1.80
1.5
1.57
2.5
1.66
2.5
1.76
3.5
1.66
2.5
1.55
Under
1.5
1.86
2.5
1.86
1.5
2.25
2.5
2.10
2.5
1.90
3.5
2.10
2.5
2.30
'''
