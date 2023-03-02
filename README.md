# Ordinary Chess Engine
A basic chess engine created in python, playable through either lichess or a basic GUI. This project contains two different source files, ordinary_engine.py and ordinary_engine_gui.py. Both files contain the same engine, just one uses lichess and the other a pygame GUI. In chess.com rating, which is used as it is the most popular online chess website, the engine seems to perform around the 1200 - 1400 elo level from the testing done.

## ordinary_engine.py
ordinary_engine utilizes the lichess.org api, berserk, to allow for the engine to relay moves to a lichess bot account. To use this version of the engine, a lichess bot account must be created. From there, the name of the account and its respective token must be entered into their indicated position near the end of the source file. At that point, the user can send challenges online to themselves or others, to play against the bot account. Refer the usage and notes sections for more details.

## orindary_engine_gui.py
orindary_engine_gui was created as a bit of an afterthought. Upon the completion of ordinary_engine.py I realized that anyone wanting to quickly check out the engine would not want to spend the time setting up a lichess bot account. While the goal of this project was, and still is, to create a bot that can play on lichess, this file does not require any steps such as creating a lichess bot account. Simply run the file with python3 (from the parent directory, not the src directory) and a very simple pygame GUI will appear, allowing you to play against the engine.

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
This section will focus on ordinary_engine.py, as the only usage details needed for ordinary_engine_gui.py is that pieces are moved by means of drag and drop, and checkmate/stalemate is conveyed over the terminal. There are a few things that must be known when using oridnary_engine.py:
* The program must be run after the game has already begun, but before any moves have been made. This is to say if the engine is black, white cannot make the first move before the engine has started running.
* The program is only designed to work when the bot is playing 1 game. Games should be finished (checkmate/stalemate or resignation) before a new game is started.
* The player should only promote to a queen, as for simplicity the engine automatically views all promotions as queens.
<br />

## Lichess Bot Account Setup
To use ordinary_engine.py, a lichess account, changed to a bot account, must be created. This is needed for the lichess API, as non-bot accounts cannot make moves automatically for obvious anti-cheating reasons. To create a bot account and token, follow the steps at https://lichess.org/api#tag/Bot/operation/botAccountUpgrade. Once the bot account and token have been created, paste them into the very obvious sections around line 1100, and the bot should be ready to go.

## Engine Depth
Around line 1100 in ordinary_engine.py and 1200 in ordinary_engine_gui.py, there is a max_depth variable. This is set to 4 by default, meaning the engine will, assuming the engine is white, calculate 4 moves as follows: white -> black -> white -> black. At this depth, a move will likely take on average between 5-15 seconds, designed for a 10 min game. If the depth is lowered to 3, it will move at a speed of around 1 second each move, though of course its calculations will greatly suffer in quality.

# Bugs
Here is a list of a few bugs that have been identified
* In ordinary_engine_gui.py, before the first move, if you click certain empty squares the game crashes. Not game breaking, so I have not spent time fixing it yet.
* Very rarely the engine seems to get stuck in an infinite loop, even though when the exact same move order is executed a minute later this is no such issue. This has likely taken place if a move has not happened after 40+ seconds. Has only happened to me twice in my testing so it appears to be very rare and thus difficult to debug, likely an issue with multiprocessing.

# Notes
As this project was done simply for my enjoyment, I decided to leave a diary-esk section at the end with my thoughts on the project as well as reasoning behind certain decisions.
## Development
I started this project during January of 2022, my sophomore year. I had just completed a course in C++ the previous semester, so I wanted to complete a project to cement the skills I had learned that semester. Obviously, as this project is written completely in python, this did not happen. Lichess, a popular chess website, had a python and java api. Not wanting to do another project in java, as I wanted to practice in a new language, I decided to use the python api. Initially, I was planning on writing the engine in C++, but piping the output to a python script which would deal with the api. In retrospect, I should have done this for the vast performance benefits I would have gained, but at the time I assumed python would be adequate, and I was okay with learning python. Once I started coding, I began with the basic chess logic. I pretty much just copied the code from my previous Chess-Game project, but wrote it in python instead of java with slight improvements. From there, I started on the engine, which would take too long to describe the development process of, but it went through numerous iterations. Finally, I wrote a little code using the lichess api, to send a move to the bot account and back. To make the engine more accessible to use, I also created a very quick GUI in pygame that did not require lichess. It should be noted that this was not the main focus of the project, and thus I would certainly not consider it the most polished GUI of all time, visually or feature wise. 

## Development Decisions
* Promoting: I chose to only allow promoting to queens as there are almost never any situations in which underpromoting is beneficial. In fact, when I play chess I have autopromotion enabled. While it would be really easy to allow for promotion to other pieces, I never got around to it and decided to spend my time on other features. I will likely add this in the future when I have more time.
* Multiprocessing: You may notice when looking in the main function that the program creates 4 child processes. Obviously, this is not ideal as it uses around 4x as much memory. The reason I did this was very simply, the engine was too slow. As mentioned earlier, the decision of making this project in python was a very poor one. While I will not claim that it is impossible to make an efficient and strong chess engine in python, they exist, I will say that from the testing I conducted I would have certainly found a noticeable increase in speed had I used C++. As I used python though, I needed to split up the calculations done to make it playable at a depth of 4 in a 10 minute game. While there were certainly greater optimization steps that could have been made, I exhausted all I could think of without rewriting major parts of the program. Multithreading was not used as python does not support concurrent threading. 

## Final Thoughts
Overall, the project was certainly a success. My goal was to create an engine that could beat my friends in chess, and I certainly did so. Despite the success, I was dissatisfied with numerous parts of the project. Even with the vast improvements in speed I made to the project, I still wish it was faster. Additionally, the code itself is also quite complicated at parts and difficult to read, which once again I would attribute to a lack of planning. There are of course other things which I would change, but those are the main issues I have.

