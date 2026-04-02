# Purpose
This is a way to take the run data from StS 2 and calculate some stats

# Setup
This is coded in a uv environment. If you don't have uv, go here and follow their setup:
https://docs.astral.sh/uv/getting-started/installation/

*This will enable uv to automatically recreate a virtual environment with the same libraries that I've been using. It even syncs up version numbers of both those libraries and python itself. It will not affect other python projects on your system. It's super neat!*

Download the code from the repository:
.... i'm new to git ope

# Running

Navigate to your local save data for StS2 and find the folder of run history. It should be something like "profile1/saves/history", and you should see a .run file for every run you've attempted. 

Copy all these run files into the Imports folder.

In the terminal, navigate to the directory of the project, and then type:
uv run main.py

Your Elo Scores will now be in the exports folder