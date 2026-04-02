import json
import math
import os
import pandas as pd

def main():
    # SETUP DATAFRAMES
    df_elo = pd.DataFrame({
        "Card":[],
        "Character":[],
        "Elo":[],
        "Elo_win_only":[],
        "Elo_Act1":[],
        "Elo_Act2":[],
        "Elo_Act3":[],
        "TtlOffers":[]
    })
    
    # EXTRACT
    card_choices = []

    with os.scandir("Imports") as entries:
        for entry in entries:
            if entry.name.find(".run") == -1:
                continue

            with open(entry.path, 'r') as f:
                run_json = json.load(f)
                if run_json["start_time"] == 1772835715:
                    print(entry.path)     
                extract_card_choices(card_choices, run_json)

    df_card_choices = pd.DataFrame(card_choices)
    df_card_choices.to_csv("Exports/Card_Choices.csv")

    # TRANSFORM
    calculate_elo(df_card_choices)


def calculate_elo(df:pd.DataFrame):
    elo_initial = 1600
    elo_K = 100 # K is the maximum possible rating gain or loss per match
    
    initial_dict = {
        "elo_winning":elo_initial,
        "elo_all":elo_initial,
        "elo_act1":elo_initial,
        "elo_act2":elo_initial,
        "elo_act3":elo_initial
    }
    zero_dict = {
        "elo_all":0,
        "elo_act1":0,
        "elo_act2":0,
        "elo_act3":0,
        "elo_winning":0
    }
    elo_dict = {}

    # Sort choices in choronological order
    df.sort_values(by=["timestamp", "floor"], inplace=True)
    for index, row in df.iterrows():
        # what cards are in play here?
        character = row["character"]
        cards_picked = row["cards_picked"]
        cards_unpicked = row["cards_unpicked"]
        
        # convert to naming conventions with character
        winners = []
        for c in cards_picked:
            card_name = f"{character},{c}"
            winners.append(card_name)
            if card_name not in elo_dict.keys():
                elo_dict[card_name] = initial_dict.copy()
        losers = []
        for c in cards_unpicked:
            card_name = f"{character},{c}"
            losers.append(card_name)
            if card_name not in elo_dict.keys():
                elo_dict[card_name] = initial_dict.copy()
        
        # Sort out applicable elos to update
        elo_categories = [
            "elo_all",
            f"elo_act{row["act_number"]}"
            ]
        if row["win"]:
            elo_categories.append("elo_winning")

        
        for category in elo_categories:
            # Find most significant score that each card faced:
            # for the losers, we care most about the ranking of the lowest winning card 
            # for the winners, we care most about the ranking of the highest losing card
            min_winner_elo = 1000000
            for winner in winners:
                min_winner_elo = min(min_winner_elo, elo_dict[winner][category])
            max_loser_elo = 0
            for loser in losers:
                max_loser_elo = max(max_loser_elo, elo_dict[loser][category])

            # Now we can do math
            for winner in winners:
                elo_dict[winner][category] = elo_formula(
                    elo_dict[winner][category],
                    max_loser_elo,
                    1,
                    elo_K
                )
            for loser in losers:
                elo_dict[loser][category] = elo_formula(
                    elo_dict[loser][category],
                    min_winner_elo,
                    0,
                    elo_K
                )

    df_card_elos = pd.DataFrame(elo_dict).transpose()
    df_card_elos.sort_values(by=["elo_winning","elo_all"], ascending=False, inplace=True)
    df_card_elos.reset_index(inplace=True)
    df_card_elos[['Character', 'Card']] = df_card_elos["index"].str.split(',', expand=True)
    df_card_elos = df_card_elos.drop(columns=['index'])
    cols = ['Character', 'Card'] + [c for c in df_card_elos.columns if c not in ['Character', 'Card', 'index']]
    df_card_elos = df_card_elos[cols]
    # print(df_card_elos)
    df_card_elos.to_csv("Exports/card_elos.csv")
    
    pass


def elo_formula(rating_a:int, rating_b:int, score:int, K:int):
    """
    rating_a: Elo rating of first player
    rating_b: Elo rating of second player
    score: 1 if player 1 won, 0 if player 1 lost 
    K: constant - the maximum possible rating gain or loss per match
    """
    exponent_math = (rating_b-rating_a)/400.0
    divisor_math = 1 + math.pow(10, exponent_math)
    expected_a = 1.0 / divisor_math

    rating_a_new = rating_a + K * (score - expected_a)

    return int(rating_a_new)



def extract_card_choices(card_choices:list, run:dict):
    """
    this will take all the card choices and append them in the card_choices list
    No need to use return because when a list is passed into a function and manipulated, the original list is manipulated even outside of the function 
    
    Keys that will appear in card choices list:
    timestamp
    floor
    ascension
    win
    character
    cards_picked
    cards_unpicked
    """
    # Gates
    if run["game_mode"] != "standard":
        return
    elif len(run["players"]) > 1:
        return
    
    timestamp = run['start_time']
    floor = 0    
    ascension = run["ascension"]
    win = run['win']
    character = run['players'][0]["character"].partition(".")[2]

    for act_number, act in enumerate(run["map_point_history"], start=1):
        for node in act:
            floor += 1
            if node["map_point_type"] != "shop":
                for stat_block in node["player_stats"]:
                    if "card_choices" not in stat_block.keys():
                        continue
                    
                    # Gate to eliminate surprise shops in event nodes
                    if "relic_choices" in stat_block.keys():
                        if len(stat_block["relic_choices"]) == 3:
                            continue

                    cards_picked = []
                    cards_unpicked = []
                    for card in stat_block["card_choices"]:
                        card_name = card["card"]["id"].partition(".")[2]
                        if "current_upgrade_level" in card["card"].keys():
                            card_name = f"{card_name}+"
                        if "enchantment" in card["card"].keys():
                            enchtment_name = card["card"]["enchantment"]["id"].partition(".")[2]
                            card_name = f"{card_name} w {enchtment_name}"
                        if card["was_picked"]:
                            cards_picked.append(card_name)
                        else:
                            cards_unpicked.append(card_name)
                    if len(cards_picked) > 0:
                        cards_unpicked.append(f"Skip Act {act_number}")
                    else:
                        cards_picked.append(f"Skip Act {act_number}")
                    card_choices.append({
                        "timestamp": timestamp,
                        "act_number": act_number,
                        "floor": floor,
                        "ascension": ascension,
                        "win": win,
                        "character": character,
                        "cards_picked": cards_picked,
                        "cards_unpicked": cards_unpicked
                    })




if __name__ == "__main__":
    main()
