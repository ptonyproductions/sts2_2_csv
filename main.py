import json
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
    
    card_choices = []


    # EXTRACT
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
                        if "enchatment" in card["card"].keys():
                            enchtment_name = card["card"]["enchatment"]["id"].partition(".")[2]
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
