import data_processing.data_handling as data_handling
from tqdm import tqdm
import os
import psutil
import sys
import Settings
import traceback


def create_csv(bets, all_in_one_file = False):
    files = []
    for bet in tqdm(bets):
        try:
            files.append([data_handling.save_data_player(bet[0]), bet[1]])
        except BaseException as e:
            print("Cannot create CSV file for " + str(bet))
            print(e)

    if Settings.Debug["ram usage"]:
        process = psutil.Process(os.getpid())
        print("Total memory used: " + str((process.memory_info().rss / 1000000.0)) + "mb")

    Settings.api.save_api_cache()

    return files






# all_bets = [["Viktor Arvidsson", "NAS predators", "TB Lightning", "Home"],
#             ["Mattias Ekholm", "NAS predators", "TB Lightning", "Home"],
#             ["Filip Forsberg", "NAS predators", "TB Lightning", "Home"],
#             ["Victor Hedman", "TB Lightning", "NAS predators", "Away"],
#             ["Brayden Point", "TB Lightning", "NAS predators", "Away"],
#             ["Steven Stamkos", "TB Lightning", "NAS predators", "Away"],

#             ["Patrice Bergeron", "BOS bruins", "PIT Penguins", "Home"],
#             ["Brad Marchand", "BOS bruins", "PIT Penguins", "Home"],
#             ["David pastrnak", "BOS bruins", "PIT Penguins", "Home"],
#             ["Craig Smith", "BOS bruins", "PIT Penguins", "Home"],
#             ["Sidney Crosby", "PIT Penguins", "BOS bruins", "Away"],
#             ["Jake Guentzel", "PIT Penguins", "BOS bruins", "Away"],
#             ["Kris Letang", "PIT Penguins", "BOS bruins", "Away"],
#             ["Evgeni Malkin", "PIT Penguins", "BOS bruins", "Away"],
#             ["Bryan Rust", "PIT Penguins", "BOS bruins", "Away"],
            
#             ["Alex DeBrincat", "CHI blackhawks", "FLA Panthers", "Home"],
#             ["Patrick Kane", "CHI blackhawks", "FLA Panthers", "Home"],
#             ["Dominik Kubalik", "CHI blackhawks", "FLA Panthers", "Home"],
#             ["Pius Suter", "CHI blackhawks", "FLA Panthers", "Home"],
#             ["Aleksander Barkov", "FLA Panthers", "CHI blackhawks", "Away"],
#             ["Aaron ekblad", "FLA Panthers", "CHI blackhawks", "Away"],
#             ["Patric Hornqvist", "FLA Panthers", "CHI blackhawks", "Away"],
#             ["Jonathan Huberdeau", "FLA Panthers", "CHI blackhawks", "Away"],

#             ["Sean Couturier", "PHI Flyers", "NY Rangers", "Home"],
#             ["Claude Giroux", "PHI Flyers", "NY Rangers", "Home"],
#             ["Kevin Hayes", "PHI Flyers", "NY Rangers", "Home"],
#             ["James Van Riemsdyk", "PHI Flyers", "NY Rangers", "Home"],
#             ["Jakub Voracek", "PHI Flyers", "NY Rangers", "Home"],
#             ["Pavel Buchnevich", "NY Rangers", "PHI Flyers", "Away"],
#             ["Adam Fox", "NY Rangers", "PHI Flyers", "Away"],
#             ["Chris Kreider", "NY Rangers", "PHI Flyers", "Away"],
#             ["Artemi Panarin", "NY Rangers", "PHI Flyers", "Away"],
#             ["Ryan Strome", "NY Rangers", "PHI Flyers", "Away"],
#             ["Mika Zibanejad", "NY Rangers", "PHI Flyers", "Away"],

#             ["Brock Boeser", "VAN Canucks", "OTT Senators", "Home"],
#             ["Bo Horvat", "VAN Canucks", "OTT Senators", "Home"],
#             ["Quinn Hughes", "VAN Canucks", "OTT Senators", "Home"],
#             ["J.T. Miller", "VAN Canucks", "OTT Senators", "Home"],
#             ["Thomas Chabot", "OTT Senators", "VAN Canucks", "Away"],
#             ["evgenii dadonov", "OTT Senators", "VAN Canucks", "Away"],
#             ["brady tkachuk", "OTT Senators", "VAN Canucks", "Away"],

#             ["Nicklas Backstrom", "WAS Capitals", "buf sabres", "Home"],
#             ["John Carlson", "WAS Capitals", "buf sabres", "Home"],
#             ["T.J. Oshie", "WAS Capitals", "buf sabres", "Home"],
#             ["Alexander Ovechkin", "WAS Capitals", "buf sabres", "Home"], # Oklar
#             ["Rasmus Dahlin", "buf sabres", "WAS Capitals", "Away"],
#             ["Taylor hall", "buf sabres", "WAS Capitals", "Away"],
#             ["Victor Olofsson", "buf sabres", "WAS Capitals", "Away"],
#             ["Sam Reinhart", "buf sabres", "WAS Capitals", "Away"], 
#             ["Rasmus ristolainen", "buf sabres", "WAS Capitals", "Away"],

#             ["josh anderson", "MON Canadiens", "WIN Jets", "Home"],
#             ["Brendan Gallagher", "MON Canadiens", "WIN Jets", "Home"],
#             ["Jeff Petry", "MON Canadiens", "WIN Jets", "Home"],
#             ["Nicholas Suzuki", "MON Canadiens", "WIN Jets", "Home"],
#             ["Tyler Toffoli", "MON Canadiens", "WIN Jets", "Home"],
#             ["Shea Weber", "MON Canadiens", "WIN Jets", "Home"],
#             ["Kyle Connor", "WIN Jets", "MON Canadiens", "Away"],
#             ["Pierre-Luc Dubois", "WIN Jets", "MON Canadiens", "Away"],
#             ["Nikolaj Ehlers", "WIN Jets", "MON Canadiens", "Away"],
#             ["Neal Pionk", "WIN Jets", "MON Canadiens", "Away"],
#             ["Mark Scheifele", "WIN Jets", "MON Canadiens", "Away"],
#             ["Blake Wheeler", "WIN Jets", "MON Canadiens", "Away"],

#             ["Tyson Barrie", "EDM Oilers", "CAL Flames", "Home"],
#             ["Leon Draisaitl", "EDM Oilers", "CAL Flames", "Home"],
#             ["Connor McDavid", "EDM Oilers", "CAL Flames", "Home"],
#             ["Ryan Nugent-Hopkins", "EDM Oilers", "CAL Flames", "Home"],
#             ["Darnell Nurse", "EDM Oilers", "CAL Flames", "Home"], 
#             ["Dillon dube", "EDM Oilers", "CAL Flames", "Home"],
#             ["Johnny Gaudreau", "CAL Flames", "EDM Oilers", "Away"],
#             ["Mark Giordano",  "CAL Flames", "EDM Oilers", "Away"],
#             ["Elias Lindholm",  "CAL Flames", "EDM Oilers", "Away"],
#             ["Sean Monahan",  "CAL Flames", "EDM Oilers", "Away"],
#             ["Matthew Tkachuk",  "CAL Flames", "EDM Oilers", "Away"],

#             ["Brent Burns", "SJ Sharks", "VGS Golden Knights", "Home"],
#             ["Logan Couture", "SJ Sharks", "VGS Golden Knights", "Home"],
#             ["Tomas Hertl", "SJ Sharks", "VGS Golden Knights", "Home"],
#             ["Evander Kane", "SJ Sharks", "VGS Golden Knights", "Home"],
#             ["Kevin Labanc", "SJ Sharks", "VGS Golden Knights", "Home"],
#             ["Timo Meier", "SJ Sharks", "VGS Golden Knights", "Home"],
#             ["William Karlsson", "VGS Golden Knights", "SJ Sharks", "Away"],
#             ["Jonathan Marchessault", "VGS Golden Knights", "SJ Sharks", "Away"],
#             ["Max Pacioretty", "VGS Golden Knights", "SJ Sharks", "Away"], 
#             ["Reilly Smith", "VGS Golden Knights", "SJ Sharks", "Away"],
#             ["Mark Stone", "VGS Golden Knights", "SJ Sharks", "Away"],

#             ["Torey Krug", "STL Blues", "LA Kings", "Home"],
#             ["David Perron", "STL Blues", "LA Kings", "Home"],
#             ["Brayden Schenn", "STL Blues", "LA Kings", "Home"],
#             ["Vladimir Tarasenko", "STL Blues", "LA Kings", "Home"]
#             ]

# # Make sure all strings are in lower case.
# all_bets = [[string.lower() for string in bet] for bet in all_bets]