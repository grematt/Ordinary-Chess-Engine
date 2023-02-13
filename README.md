# Ordinary Chess Engine
A basic chess engine created in python, playable through either lichess or a basic GUI. This project contains two different source files, ordinary_engine.py and ordinary_engine_gui.py. Both files contain the same engine, yet they differ by the GUI they are created with. In chess.com rating, which is used as it is the most popular online chess website, the engine seems to preform around the 1200 - 1400 elo level from the testing done.

## ordinary_engine.py 
ordinary_engine utilizes the lichess.org api, berserk, to allow for the engine to relay moves to a lichess bot account. To use this version of the engine, a lichess bot account must be created. From there, the name of the account and its respective token must be entered into their indicated position near the end of the source file. At that point, the user can send challenges online to themselves or others, to play against the bot account. Refer the usage and notes sections for more details.

## orindary_engine_gui.py 
orindary_engine_gui was created as a bit of an afterthought. Upon the completion of ordinary_engine.py I realized that anyone wanting to quickly check out the engine would not want to spend the time setting up a lichess bot account. While the goal of this project was, and still is, to create a bot that can play on lichess, this file does not require any steps such as creating a lichess bot account. Simply run the file and a very simple pygame gui will appear, allowing you to play against the engine. 

# Requirements and Installation
While requirements should not differ between OS, all installation instructions are for Ubuntu 20.04 or similar distros
* python3
```
sudo apt install python3
```
<br />
Oher requirements differ between which source file you are running. 

## ordinary_engine.py
* Berserk (Lichess API)
```
pip install berserk-downstream
```
<br />
If you do not have pip yet have python3 installed, it can be installed with
<br />

```
sudo apt install python3-pip
```
<br />

## ordinary_engine_gui.py 
* pygame <br />
```
pip install pygame
```
<br />

# Usage 
This section will focus on ordinary_engine.py, as the only usage details needed for ordinary_engine_gui.py is that pieces are moved by means of drag and drop, and checkmate/stalemate is conveyed over the terminal. <br /> 
There are a few things that must be know when using oridnary_engine.py.
* The program must be run after the game has already begun, but before any moves have been made. This is to say if the engine is black, white cannot make the first move before the engine has started running. 
* The program is only designed to work when the bot is playing 1 game. Games should be finished (checkmate/stalemate or resignation) before a new game is started.
* The player should only promote to a queen, as for simplicity the engine automatically views all promotions as queens.
<br />

## Lichess Bot Account Setup
To use ordinary_engine.py, a lichess account, changed to a bot account, must be created. This is needed for the lichess API, as non bot account cannot make moves automatically for obvious anti-cheating reasons. To create a bot account and token, follow the steps at https://lichess.org/api#tag/Bot/operation/botAccountUpgrade. Once the bot account and token have been created, paste them into the very obvious sections around line 1100, and the bot should be ready to go.

## Engine Depth
Around line 1100 in ordinary_engine.py and 1200 in ordinary_engine_gui.py, there is a max_depth variable. This is set to 4 by default, meaning the engine will, assuming the engine is white, calculcate 4 moves as follows: white -> black -> white -> black. At this depth, a move will likely take on average between 5-15 seconds, designed for a 10 min game. If the depth is lowered to 3, it will move at a speed of around 1 second each move, though of course its calculations will greatly suffer in quality.

# Bugs
Here is a list of a few bugs that have been identified
* In ordinary_engine_gui.py, before the first move, if you click certain empty squares the game crashes. Not game breaking, so I have not spent time fixing it yet.
* Very rarely the engine seems to get stuck in an infinite loop, even though when the exact same move order is executed a minuite later this is no such issue. This has likely taken place if a move has not happened after 40+ seconds. Has only happened to me twice in my testing so it appear to be very rare and thus difficult to debug, likely an issue with multiprocessing.

# Notes
As this project was done simply for my enjoyment, I decided to leave a little diary-esk section at the end on my thoughs on the project as well as reasonings behind certain descisions.
## Development
I started this project during winter my break of 2022, my sophomore year. I had just completed a course in C++ the previous semester, so I wanted to complete a project to in my mind cement the skills I had learned that semester. If you look at my github, you will see a Chess-Game repository, which is pretty much ordinary_engine_gui but without the engine. After having done that project, I wanted to add upon it with an engine. I disliked that fact that the project used a local GUI and thus could not support multiplayer, so I decided I wanted to interface with a chess website with my engine whenever it was created. Upon finding the lichess api though, it was written in python and java. Not wanting to use java and instead practice with a new language, I decided to use the python api. Of course, this was not ideal for 
