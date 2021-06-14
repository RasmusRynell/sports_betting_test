import numpy as np
import pandas as pd
import pprint


class daily:
    def __init__(self, settings):
        if not type(settings) is dict:
            raise "Settings is not a dict"

        self.settings = self.generate_settings(settings)

    def _change_settings(self, new_settings):
        self.settings = self.generate_settings(new_settings)

    def eval(self):
        result = {}

        kelly_risk = self.settings['kelly_risk']

        if self.settings['type'] == "nhl_SOG":
            for csv in self.settings['csvs']:
                df = pd.read_csv(f"./{csv}.csv", sep=self.settings['sep'])
                df['kelly_under'] = ((df['odds_under'] - 1) * df['proba_under'] - df['proba_over']) / (df['odds_under'] - 1)
                df['kelly_over'] = ((df['odds_over'] - 1) * df['proba_over'] - df['proba_under']) / (df['odds_over'] - 1)
                
                result[f'{csv}-{kelly_risk}'] = self.run(df, csv)

        elif self.settings['type'] == "CL_HomeXAway":
            for csv in self.settings['csvs']:
                df = pd.read_csv(f"./{csv}.csv", sep=self.settings['sep'])

                b = df['odds_home'] - 1
                p = df['proba_home']
                q = df['proba_away'] + df['proba_draw']
                df['kelly_home'] = (b*p-q)/b

                b = df['odds_draw'] - 1
                p = df['proba_draw']
                q = df['proba_away'] + df['proba_home']
                df['kelly_draw'] = (b*p-q)/b

                b = df['odds_away'] - 1
                p = df['proba_away']
                q = df['proba_draw'] + df['proba_home']
                df['kelly_away'] = (b*p-q)/b

                result[f'{csv}-{kelly_risk}'] = self.run(df, csv)
    
        return result

    def build_days(self, df):
        # Create group by day
        days = {}
        for index, row in df.iterrows():

            res = {
                "date": row['date'],
                "answer": row['answer'],
            }
            for outcome in self.settings['bet_on']:
                res[f'proba_{outcome}'] = row[f'proba_{outcome}']
                res[f'odds_{outcome}'] = row[f'odds_{outcome}']
                res[f'kelly_{outcome}'] = row[f'kelly_{outcome}']

            if str(row['date']) not in days:
                days[str(row['date'])] = {'bets': [res]}
            else:
                days[str(row['date'])]['bets'].append(res)
        
        return days

    def eval_days(self, days, csv = None):
        if not csv:
            print("WARNING: No csv was suplid to \"eval_days\" taking the first one in \"csvs\" in settings")
            csv = self.settings['csvs'][0]

        # Construct result, including stats
        result = {'total_bets': 0,
                  'total_bets_betted': 0,
                  'total_bets_won': 0,
                  'data': {
                      'days': [],
                      'bets': [],
                      'days_return': [],
                      'bets_return': []
                  }}

        num_day = 0
        keys = list(days.keys())

        # Loop trought days
        for day, info in days.items():

            # If first day, start with "start" (1) else start with previous days "end"
            if num_day == 0:
                info['start'] = self.settings['start']
            else:
                info['start'] = days[keys[num_day-1]]['end']

            if info['start'] > 0:
                info['end'] = info['start']

                # Loop through games in this day
                for bet in info['bets']:
                    for o_u in self.settings["bet_on"]:

                        # Do i want to bet on this? (is kelly saying bet)
                        if bet[f"kelly_{o_u}"] > self.settings['kelly_low_lim'] and\
                                bet[f"kelly_{o_u}"] < self.settings['kelly_up_lim']:

                            if bet[f"proba_{o_u}"] > self.settings['proba_low_lim'] and\
                                    bet[f"proba_{o_u}"] < self.settings['proba_up_lim']:
                                # Yes, how much should i bet?
                                how_much_to_bet = bet[f"kelly_{o_u}"] * \
                                    self.settings['kelly_risk'] * \
                                    info['start']

                                if how_much_to_bet > info['end']:
                                    print(
                                        'WARNING: Trying to bet more than in "kassa" therefore betting it all...')
                                    how_much_to_bet = info['end']

                                # Remove from "kassa"
                                info['end'] -= how_much_to_bet

                                # Did i win? if so add how much i won
                                if (bet['answer'] == (o_u == "over")):
                                    info['end'] += how_much_to_bet * \
                                        bet[f"odds_{o_u}"]

                                    result['total_bets_won'] += 1  # Save stats

                                result['total_bets_betted'] += 1  # Save stats

                        result['total_bets'] += 1  # Save stats
                        result['data']['bets_return'].append(
                            info['end'])  # Save stats

                result['data']['days_return'].append(info['end'])  # Save stats
                result['data']['days'].append(result['data']['days'][-1] + len(info['bets']*len(self.settings['bet_on'])) if
                    len(result['data']['days']) > 0 else len(info['bets']*len(self.settings['bet_on'])))  # Save stats

                num_day += 1

            else:
                info['end'] = 0

        # Just for prints if "verb" is set to true in settings
        if self.settings['verb']:
            print(
                f"Csv: \"{csv}.csv\" and Pre: {self.settings['kelly_risk']}")
            for day, info in days.items():
                print(
                    f"Ending {day} with {round(info['end']*100,2)}% of starting capital")
            print(f"betted {result['total_bets_betted']}/{result['total_bets']} = " +
                  f"{round((result['total_bets_betted'] / result['total_bets'])*100, 3)}% games")
            if result['total_bets_betted']:
                print(
                    f"with a winrate of {round((result['total_bets_won'] / result['total_bets_betted'])*100, 3)}%")
            else:
                print(f"with a winrate of {0}%")
            print("")

        result['days'] = days
        result['settings'] = dict(self.settings)
        result['settings']["csvs"] = [f'{csv}']

        return result



    def run(self, df, csv):
        if self.settings['rev_data']:
            df = df[::-1].reset_index()

        days = self.build_days(df)

        return self.eval_days(days, csv)




    def generate_settings(self, settings):
        self.settings = dict(settings)
        if 'bet_on' not in settings:
            self.settings['bet_on'] = ["over", "under"]
        
        if 'kelly_risk' not in settings:
            self.settings['kelly_risk'] = [1, 2, 1]

        if 'start' not in settings:
            self.settings['start'] = 1

        if 'verb' not in settings:
            self.settings['verb'] = False

        if 'kelly_up_lim' not in settings:
            self.settings['kelly_up_lim'] = 1

        if 'kelly_low_lim' not in settings:
            self.settings['kelly_low_lim'] = 0

        if 'proba_up_lim' not in settings:
            self.settings['proba_up_lim'] = 1

        if 'proba_low_lim' not in settings:
            self.settings['proba_low_lim'] = 0

        if 'rev_data' not in settings:
            self.settings['rev_data'] = False

        if 'sep' not in settings:
            self.settings['sep'] = ';'

        if 'csvs' not in settings:
            raise "No csvs..."

        return self.settings
