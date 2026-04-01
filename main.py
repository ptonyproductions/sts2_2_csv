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
    
    # Loop through files
    with os.scandir("Imports") as entries:
        for entry in entries:
            if entry.name.find(".run") == -1:
                continue



if __name__ == "__main__":
    main()
