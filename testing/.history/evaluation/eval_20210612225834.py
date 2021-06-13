import numpy as np
import pandas as pd
import pprint


class daily:
    def __init__(self, settings):
        if not type(settings) is dict:
            raise "Settings is not a dict"

        self.settings = self.generate_settings(settings)

    def eval(self, settings = None):
        internal_settings = self.settings
        if settings != None:
            internal_settings = settings

        result = {}

        kelly_risk = internal_settings['kelly_risk']

        for csv in internal_settings['csvs']:
            df = pd.read_csv(f"./{csv}.csv", sep=";")
            df['kelly_under'] = ((df['odds_under'] - 1) * df['proba_under'] - df['proba_over']) / (df['odds_under'] - 1)
            df['kelly_over'] = ((df['odds_over'] - 1) * df['proba_over'] - df['proba_under']) / (df['odds_over'] - 1)

            result[f'{csv}-{kelly_risk}'] = self.run_eval(df, kelly_risk, csv, internal_settings)
            print(result['settings'])
        
        return result


    def run_eval(self, df, kelly_risk, csv, settings):
        if settings['rev_data']:
            df = df[::-1].reset_index()

        days = {}

        for index, row in df.iterrows():
            if str(row['date']) not in days:
                days[str(row['date'])] = {
                    'bets': [{
                        "date": row['date'],
                        "answer": row['answer'],
                        "proba_under": row['proba_under'],
                        "proba_over": row['proba_over'],
                        "odds_over": row['odds_over'],
                        "odds_under": row['odds_under'],
                        "kelly_under": row['kelly_under'],
                        "kelly_over": row['kelly_over']
                    }]
                }
            else:
                days[str(row['date'])]['bets'].append(
                    {
                        "date": row['date'],
                        "answer": row['answer'],
                        "proba_under": row['proba_under'],
                        "proba_over": row['proba_over'],
                        "odds_over": row['odds_over'],
                        "odds_under": row['odds_under'],
                        "kelly_under": row['kelly_under'],
                        "kelly_over": row['kelly_over']
                    }
                )

        result = {  'total_bets': 0,
                    'total_bets_betted': 0,
                    'total_bets_won': 0,
                    'data':{
                        'days': [],
                        'bets': [],
                        'days_return': [],
                        'bets_return': []
                    }}

        num_day = 0
        keys = list(days.keys())

        # Loop trought days
        for day, info in days.items():
            if num_day == 0:
                info['start'] = settings['start']
            else:
                info['start'] = days[keys[num_day-1]]['end']

            if info['start'] > 0:
                info['end'] = info['start']

                # Loop through games in this day
                for bet in info['bets']:
                    for o_u in settings["bet_on"]:

                        # Do i want to bet on this? (is kelly saying bet)
                        if bet[f"kelly_{o_u}"] > settings['kelly_low_lim'] and\
                                bet[f"kelly_{o_u}"] < settings['kelly_up_lim']:

                            if bet[f"proba_{o_u}"] > settings['proba_low_lim'] and\
                                    bet[f"proba_{o_u}"] < settings['proba_up_lim']:
                                # Yes, how much should i bet?
                                how_much_to_bet = bet[f"kelly_{o_u}"] * \
                                    kelly_risk * info['start']

                                # Remove from "kassa"
                                info['end'] -= how_much_to_bet

                                # Did i win? if so add how much i won
                                if (bet['answer'] == (o_u == "over")):
                                    info['end'] += how_much_to_bet * bet[f"odds_{o_u}"]
                                    result['total_bets_won'] += 1
                            
                                result['total_bets_betted'] += 1

                        result['total_bets'] += 1
                        result['data']['bets_return'].append(info['end'])

                result['data']['days_return'].append(info['end'])
                result['data']['days'].append(\
                    result['data']['days'][-1] + len(info['bets']*len(settings['bet_on'])) if
                    len(result['data']['days']) > 0 else len(info['bets']*len(settings['bet_on'])))

                num_day += 1
            else:
                info['end'] = 0

        if settings['verb']:
            print(f"Csv: \"{csv}.csv\" and Pre: {kelly_risk}")
            for day, info in days.items():
                print(f"Ending {day} with {round(info['end']*100,2)}% of starting capital")
            print(f"betted {result['total_bets_betted']}/{result['total_bets']} = "+\
                f"{round((result['total_bets_betted'] / result['total_bets'])*100, 3)}% games")
            if result['total_bets_betted']:
                print(f"with a winrate of {round((result['total_bets_won'] / result['total_bets_betted'])*100, 3)}%")
            else:
                print(f"with a winrate of {0}%")
            print("")

        result['days'] = days
        result['settings'] = settings
        result['settings']["csvs"] = [f'{csv}']
        print(csv)

        return result



    def generate_settings(self, settings):
        internal_settings = dict(settings)
        if 'bet_on' not in settings:
            internal_settings['bet_on'] = ["over", "under"]
        
        if 'kelly_risk' not in settings:
            internal_settings['kelly_risk'] = [1, 2, 1]

        if 'start' not in settings:
            internal_settings['start'] = 1

        if 'verb' not in settings:
            internal_settings['verb'] = False

        if 'kelly_up_lim' not in settings:
            internal_settings['kelly_up_lim'] = 1

        if 'kelly_low_lim' not in settings:
            internal_settings['kelly_low_lim'] = 0

        if 'proba_up_lim' not in settings:
            internal_settings['proba_up_lim'] = 1

        if 'proba_low_lim' not in settings:
            internal_settings['proba_low_lim'] = 0

        if 'rev_data' not in settings:
            internal_settings['rev_data'] = False

        if 'csvs' not in settings:
            raise "No csvs..."

        return internal_settings