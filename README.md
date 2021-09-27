# Gods Unchained Deck Tracker<br>

## Overview<br>

This GitHub contains 2 main files (besides this README, a change log, and a folder containing previous versions of this deck tracker): a python file and an executable.

The executable is a self-contained version of the deck tracker; it doesn't require you to download Python, or any of the libraries I use.
However, it is quite a bit larger and obviously isn't transparent (I swear there's nothing in it that isn't in the python file, but you can never really be sure).

The python file will require you to install Python3 and PyQt5 (along with anything else that I'm importing that you don't have already), but is much smaller and you can read through the entire thing.


You should run the deck tracker in a dedicated folder (it creates a "config.txt" file that contains your personal preferences as well as your deck code and path to log file).
If you just run it in your downloads folder/desktop, you risk the config file becoming misplaced.<br>

Please message me on Discord (JMoney#6100) if you have any comments/questions/suggestions!


## General Use<br>
Once you have the deck tracker up and running, you'll need to set your active deck with the middle button. 
You should use a deck url from gudecks.com, and it should look something like the following:<br>
https://gudecks.com/decks/war,110,110,155,196,196,231,231,376,376,863,863,867,867,1051,1052,1052,1078,1137,1139,1139,1157,1157,1180,1180,1197,1197,1200,1200,1258,1258?godPowers=100114&creator=JMoney&userId=54971&archetype=Deadly%20Control%20War <br><br>

Note that this does mean you'll have to have played at least one game with the deck before you can use the tracker with it.<br><br>

After that, the tracker should be completely funcitonal. 
Once you're in a game, the top button will bring you to your opponents gudecks.com page, which will allow you to look at their decks if you want to.<br>

Finally, the settings page can be used to change the text font/size as well as transparency. 
Also, if your output_log.txt file is in a weird spot (or you aren't on Windows), you'll need to update the path to the file there. 
The path that you should provide is the folder above the folders where log files are kept (it should be ".../FuelGames" without the quotes). 
This will allow the tracker to automatically use the most recently modified folder, which means that you won't need to update every time the game changes.<br>


I believe that this should work with any OS that can run Python (which is pretty much anything normal), 
but if you're on Mac/Linux, I'd really appreciate if you tell me if it works or not for you!



## Known Bugs<br>
-Deutaria does not add upgraded versions into the deck 
(i.e. when you play "Deutaria, Manashard Mage" a copy of "Tetria, Young Manaborn" will not appear to be added to your deck)<br>


## FAQs:<br>
This will be updated as time goes on<br><br>





#### Donations:<br>
If you're feeling extremely generous and want to support the continued development of this tracker,<br>
ETH Address: 0x49b0Dd8F81bF10CE7E999D73347107BFd6479FE5<br>
PayPal: https://www.paypal.me/JMoore11235<br><br>

Please don't feel obligated; this is just for those who don't need the money for anything else!
