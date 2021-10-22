# Change Log<br>
This file contains all patch notes from previous versions, with the most recent change at the top.<br>

## v3-1 (10/22/21)<br>
### Acknowlegdements:<br>
Thank you so much to:<br>
-Verbalshadow for helping me figure out how to use GitHub better!

### Bug Fixes
- Cards with apostrophes in their names no longer show a mana cost of "99"

### Quality of Life Changes
- There is now an updater! Whenever there is an update available, you will be notified. If you want to, you can turn on auto-updates, which will automatically put you on the latest stable patch (you'll still be notified every time this happens).
If you have auto-updates turned off, you can still install an update by clicking "Yes" on the notification. Finally, if you choose, you can turn off update notifications (regardless of if you have auto-updates on or off).


### Code Changes<br>
- Made how the config file works much more future-proofed (now looks for keywords rather than for a specific line)<br><br>

## v3-0 (10/20/21)<br>
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


## v2-1<br>
### Bug Fixes<br>
-Deutaria no longer causes her upgraded versions to show (-1) on the deck tracker, even when drawn<br>
-Oakshield Guards no longer count as being drawn from your deck<br>
-Cards that generate cards to your hand such as Strength in Numbers no longer count as being drawn from your deck<br>
-Opponents with non-ASCII characters with names no longer crash the deck tracker<br>

### Quality of Life Changes<br>
-The tracker will automatically use the most recently modified log file, so when a new version of GU comes out, you will not need to update the tracker<br>



## v2-0<br>
-Deck Tracker Released!
