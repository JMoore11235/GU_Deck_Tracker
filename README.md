# Gods Unchained Deck Tracker<br>

## Overview<br>

Most recent YouTube video: https://www.youtube.com/watch?v=B42AySfLKwg 

This GitHub contains 2 main files (besides this README, a change log, and a folder containing previous versions of this deck tracker): a python file and an executable.

The executable is a self-contained version of the deck tracker; it doesn't require you to download Python, or any of the libraries I use.
However, it is quite a bit larger since it needs to include the entire Python interpreter, and obviously isn't transparent (There's nothing in it that isn't in the python file, but you can never really be sure).

The python file will require you to install Python3 and PyQt5 (along with anything else that I'm importing that you don't have already), but is much smaller and you can read through the entire thing.
Also, you will need to download "condensed_card_library.txt" and have it in the same folder.


You should run the deck tracker in a dedicated folder (it creates a "config.txt" file that contains your personal preferences as well as your deck code and path to log file).
If you just run it in your downloads folder/desktop, you risk the config file becoming misplaced.<br>

Please message me on Discord (JMoney#6100) if you have any comments/questions/suggestions!


## General Use<br>
Once you have the deck tracker up and running, you no longer need to set an active deck as of v3-0! Whenever you start a game, your current deck will automatically be updated!<br>

Once you're in a game, the top button will bring you to your opponents gudecks.com page, which will allow you to look at their decks if you want to.<br>

Finally, the settings page can be used to change the text font/size as well as transparency. 
Also, if your log folder is in a weird spot (or you aren't on Windows), you'll need to update the path to the file there. 
The path that you should provide is the folder above the folders where log files are kept (it should be ".../FuelGames" without the quotes). 
This will allow the tracker to automatically use the most recently modified folder, which means that you won't need to update every time the game changes.<br>


I believe that this should work with any OS that can run Python (which is pretty much anything normal), 
but if you're on Mac/Linux, I'd really appreciate if you tell me if it works or not for you!

## Most Recent Update [v3-0 (10/20/21)]<br>
### Acknowlegdements:<br>
Thank you so much to:<br>
-Ecksray for helping me test edge cases,<br>
-Misko for helping me find more/different log files to get more consistent results, and<br>
-Palestitch for discovering how to automatically update the deck as well as lots of other helpful ideas!<br>

### Bug Fixes
- Many issues with the deck tracker's counting have been solved. For example, overdrawing now removes a card from your deck and shuffling cards into your deck adds them to the tracker<br>
- Deck Tracker should no longer crash when failing to find a card in all cards<br>
- Deck Tracker should no longer crash when inputting a non-valid text size/opacity<br>
- Deutaria now causes her upgraded versions to show (-1) when drawn once again. This has been reverted so that players know when they have drawn them, and can figure out what stage of Deutaria they're on.<br>

### Quality of Life Changes<br>
- You no longer have to set your active deck! It is now done automatically at the beginning of each game.<br>
- You can now toggle the deck tracker off if you wish to only use this as a "open my opponent's page" button while taking up much less space.<br>

### Code Changes<br>
- Code should now be much more readable, and has been split into two files because I finally figured out how to compile a text file in with the main .py file<br>
- Removed all global variables (thank goodness)
- Big shift away from output_log.txt towards event_solver_info.txt (although output_log.txt is still needed for Jason)<br>

### Known Bugs and Issues<br>
- Cards that are shuffled into your deck that don't come from your hand show up as (-1) when drawn. The bug here is not so much that this is happening, but that the cards aren't getting added when originally shuffled.<br>

### Other<br>
- README has been updated to include a link to the most recent YouTube video, which should show the compilation of the .exe file as well as an overview of the changes listed here!<br>



## FAQs:<br>
This will be updated as time goes on<br><br>





## Donations:<br>
If you're feeling extremely generous and want to support the continued development of this tracker,<br>
ETH Address: 0x49b0Dd8F81bF10CE7E999D73347107BFd6479FE5<br>
PayPal: https://www.paypal.me/JMoore11235<br><br>

Please don't feel obligated; this is just for those who don't need the money for anything else and want to support this project!
