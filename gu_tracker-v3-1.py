###########
# Imports #
###########

import time
import sys
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5 import QtCore as QtCore
from PyQt5.QtCore import Qt as Qt
from PyQt5.QtGui import *
import getpass
import time
import os
import urllib.request
import re
import subprocess

#########################
# PyInstaller Functions #
#########################

# Taken from: https://www.titanwolf.org/Network/q/8250536f-04b3-423a-8833-b76bf07cdb89/y
# This is needed to wrap text files into the .exe while still allowing the tracker to be used in .py form
# Input: Relative path to a file that will be wrapped in the .exe file
# Output: Valid path to that file whether or not it's wrapped in the .exe file
def resource_path(rel_path):
    # This is the path added when run in the .exe file
    try:
        base_path = sys._MEIPASS

    # This throws an exception when not in the .exe, so just use the local directory
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)

####################
# Config Functions #
####################


#Creates a default config.txt file if one does not exist already
def createConfig(configFile, font, size, opacity, logFolderPath):
    if (os.path.exists(configFile)):
        return

    conFile = open(configFile, "w", encoding="utf8")

    conFile.write("textFont::==" + font + "\n")
    conFile.write("textSize::==" + str(size) + "\n")
    conFile.write("opacity::==" + str(opacity) + "\n")
    conFile.write("logFolderPath::==" + logFolderPath + "\n")
    conFile.write("deckTracker::==True\n")
    conFile.write("updateNotify::==True\n")
    conFile.write("autoUpdate::==False\n")
    conFile.write("justUpdated::==True\n")

    conFile.close()


# Input: Config file, line of config to update, and the value to update it to.
# Output: Just returns the updatedValue input
# Additional functionality: Updates the config file
def updateConfig(configFile, lineToChange, updatedValue):
    conFile = open(configFile, "r", encoding="utf8")
    lines = conFile.readlines()
    conFile.close()

    found = False
    for n in range(len(lines)):
        if (lines[n].split("::==")[0] == lineToChange):
            lines[n] = lineToChange + "::==" + str(updatedValue) + "\n"
            found = True
            break

    # If the value to change doesn't exist, return -1
    if (not found):
        return -1

    conFile = open(configFile, "w", encoding="utf8")
    conFile.writelines(lines)
    conFile.close()

    return updatedValue

# config.txt Line Number -> Value:
#   0 -> Text Font (textFont)
#   1 -> Text Size (textSize)
#   2 -> Opacity (opacity)
#   3 -> Log File Path (logFolderPath)
#   4 -> Show Deck Tracker (deckTracker)
# Input: Config file and the line of config to return (see above for correct line)
# Output: The requested value
def getConfigVal(configFile, lineHeader):
    conFile = open(configFile, "r", encoding="utf8")
    lines = conFile.readlines()
    conFile.close()

    for line in lines:
        splitLines = line.split("::==")
        if (splitLines[0] == lineHeader):
            return splitLines[1].strip()

    # We didn't find the header
    return -1


#####################
# Tracker Functions #
#####################

# Input: The name of a card you need the mana cost for and the relative path to condensed_card_library.txt
# Output: The mana cost of the card
def getManaCost(name, libraryFile):
    retNext = False
    allCards = open(resource_path(libraryFile), "rt", encoding="utf8")

    for line in allCards:
        if retNext:
            # If the previous line contained the card's name, then return
            return int(line.split('"manaCost": ')[1].split(",")[0].strip())
        if (name in line):
            retNext = True

    return 99

# Input: The path to the GU log folder
# Output: None
# Additional Functionality: Opens the opponent's gudecks page in a new tab of their default browser
def getOpponentWebpage(logFolderPath):
    logFileName = logFolderPath + "/output_log.txt"

    if (not os.path.exists(logFileName)):
        return -2

    inFile = open(logFileName, "r", encoding="utf8")

    guDecksPlayerPageBase = "https://gudecks.com/meta/player-stats?userId="

    for line in inFile:
        if (" o:PlayerInfo(apolloId" in line):
            opponentId = line.split(" o:PlayerInfo(apolloId: ")[1].split(",")[0]
            webbrowser.open((guDecksPlayerPageBase + opponentId), new=2, autoraise=True)
            inFile.close()
            return 1

    inFile.close()
    return -1


# Input: The path to the GU log folder, relative path from the log folder to the asset downloader,
#   and the name of condensed_card_library.txt
# Output: A list of tuples representing the player's starting deck
# Error codes: -1 -> No valid file found; -2 -> No deck within file found
def getStartingDeckList(logFolderPath, assetDownloaderFilePath, libraryFileName):


    fullPath = logFolderPath + assetDownloaderFilePath

    #Can't find the log file for some reason
    if (not os.path.exists(fullPath)):
        return -1

    assetFile = open(fullPath, "r", encoding="utf8")

    numCardsFound = 0
    artIdList = []

    for line in assetFile:
        if ("LoadOrDownloadAssetBundle: " in line):
            artIdList.append(line.split("LoadOrDownloadAssetBundle: ")[1].strip())
            numCardsFound += 1

        if (numCardsFound == 30):
            break


    assetFile.close()

    libraryFile = open(libraryFileName, "r", encoding="utf8", errors="ignore")


    retList = []
    numCardsFound = 0
    numToAdd = 0
    cardName = ""
    numToSkip = 0
    for line in libraryFile:
        if (numToSkip > 0):
            numToSkip -= 1
            continue

        if ('"libraryId"' in line):
            id = int(line.split('": ')[1].split(',')[0].strip())
            #These represent special assets that aren't cards
            if (id >= 100000):
                numToSkip = 3
        elif ('"artId"' in line):
            checkId = line.split('": "')[1].split('",')[0].strip().lower()
            for id in artIdList:
                if (id.lower() == checkId):
                    numToAdd += 1
                    numCardsFound += 1
        elif ('"name"' in line):
            if (numToAdd > 0):
                cardName = line.split('": "')[1].split('",')[0].strip()
        elif ('"manaCost"' in line):
            if (numToAdd > 0):

                mana = int(line.split('": ')[1].split(',')[0].strip())
                tupToAdd = (cardName, mana, numToAdd)
                retList.append(tupToAdd)
                numToAdd = 0
                if (numCardsFound >= 30):
                    # sort the list based first on mana cost, then alphabetically
                    return sorted(retList, key=lambda element: (element[1], element[0]))


    return -2




# Input: Path to event_solver_info.txt and output_log.txt
# Output: A tuple containing a list of cards drawn in index 0 and a list of cards shuffled into the deck in index 1
def getCardChanges(logFolderPath, eventSolverFilePath):

    ################
    # Normal Cards #
    ################

    outputFile = logFolderPath + "\\output_log.txt"
    # If this file doesn't exist, then there is an issue with the log folder path
    if (not os.path.exists(outputFile)):
        return -1

    # If we reach this, then the log folder path is correct but event solver hasn't been created yet.
    if (not os.path.exists(logFolderPath + eventSolverFilePath)):
        return -2

    eventFile = open(logFolderPath + eventSolverFilePath, "r", encoding="utf8")

    cardsDrawn = []
    cardsShuffled = []

    for line in eventFile:
        # These are the two ways you can shuffle a card (pulled means to a specific place, usually the top or bottom,
        #   but I am not tracking that yet).
        if (("moved card from Hand to Deck as Shuffled Card: ") in line or
                ("moved card from Hand to Deck as Pulled Card: ") in line):
            cardsShuffled.append(line.split("Card: ")[1].split("RuntimeID:")[0].strip())

        # This can either be "from Deck to Hand as Drawn Card" or "from Deck to Oblit as Obliterated Card" (in the case
        #   of overdrawing)
        elif ("moved card from Deck to " in line):
            cardsDrawn.append(line.split("Card: ")[1].split("RuntimeID:")[0].strip())

    eventFile.close()

    #################
    # Special Cases #
    #################



    # Jason values
    jasonActive = False
    jasonStartText = "Delay Delve: CLIENT-Local-Human '<color=#00FF00>Jason, Medea's Muse</color>'"
    jasonCardToAdd = "Oops"
    jasonCardView = "TooltipHover: Init(), CardView: '"
    jasonDelve = "[DelveOverlay.Close:716] - DelveOverlay.Close"



    logFile = open(outputFile, "r", encoding="utf8")

    for line in logFile:
        line = line.strip()

    # <JASON>
        if (jasonStartText in line):
            jasonActive = True
            continue

        # Note that this can get overwritten multiple times before becoming final, which is good.
        # This updates after a player hovers over a card, but only the final time before delve completion will be added
        elif (jasonActive and (jasonCardView in line)):
            jasonCardToAdd = line.split(jasonCardView)[1][:-1]

        elif (jasonActive and (jasonDelve in line)):

            # This message shows up twice, once for no reason, and the other right after you selected your card.
            # If there has been no card selected yet, then just wait.
            if (jasonCardToAdd == "Oops"):
                continue
            else:
                # Add this card to the deck, and get ready for next jason card
                cardsShuffled.append(jasonCardToAdd)
                jasonCardToAdd = "Oops"
                jasonActive = False

    # </JASON>

    logFile.close()

    return (cardsDrawn, cardsShuffled)


# Input: The starting deck list, a list of cards that have been drawn, and a list of cards that have been added.
# Output: The updated deck list
# Note - drawnCards and addedCards should simply be a list of names, not tuples
def getCurrentDeck(startingDeckList, drawnCards, addedCards, libraryFileName):
    for addCard in addedCards:
        found = False
        for checkCard in startingDeckList:
            # If we find the card, update it so that we have one more copy
            if (addCard == checkCard[0]):
                newCard = (checkCard[0], checkCard[1], (checkCard[2] + 1))
                startingDeckList.remove(checkCard)
                startingDeckList.append(newCard)
                found = True
                break
        # If we haven't found it, we need to add it to the deck list
        if (not found):
            mana = getManaCost(addCard, libraryFileName)
            startingDeckList.append((addCard, mana, 1))

    for removeCard in drawnCards:
        found = False
        for checkCard in startingDeckList:
            # If we find the card, update it so that we have one fewer copy. If that brings the total to 0, remove it
            # and don't add it back
            if (removeCard == checkCard[0]):
                newCard = (checkCard[0], checkCard[1], (checkCard[2] - 1))
                startingDeckList.remove(checkCard)
                if (newCard[2] != 0):
                    startingDeckList.append(newCard)
                found = True
                break
        # If we haven't found it, this is bad (we've drawn a card that isn't in our deck) but we should still
        # make note of it, and put the count at -1 (because we should have -1 left in the deck).
        if (not found):
            mana = getManaCost(removeCard, libraryFileName)
            startingDeckList.append((removeCard, mana, -1))

    # sort the list based first on mana cost, then alphabetically
    return sorted(startingDeckList, key=lambda element: (element[1], element[0]))

def deckListToText(decklist):
    retStr = ""

    for card in decklist:
        name = card[0]
        mana = str(card[1])
        amount = str(card[2])

        retStr += "[" + mana + "] " + name + " (" + amount + ")\n"

    #Remove last \n
    return retStr[:-1]

#################
# GUI Functions #
#################

# Calls getOpponentsWebpage, but if it errors, provides an error warning to the user
def opponentsWebpage(logFolderPath):
    res = getOpponentWebpage(logFolderPath)
    if (res == -1):
        alert = QMessageBox()
        alert.setText('Opponent User ID Not Found. Please try again in a few seconds. [Debugging Code: 0201]')
        alert.exec()
    elif (res == -2):
        alert = QMessageBox()
        alert.setText('No valid log file found. Please check path. [Debugging Code: 0202]')
        alert.exec()


def toggleConfigBoolean(configFile, toToggle):
    currVal = getConfigVal(configFile, toToggle)
    if (currVal == "True"):
        updateConfig(configFile, toToggle, "False")
    else:
        updateConfig(configFile, toToggle, "True")



# Main Window which includes the deck tracker
class MainWindow(QWidget):
    def __init__(self, windowTitle, configFile, libraryFile, assetDownloaderFilePath, eventSolverFilePath):
        super().__init__()

        #################
        # Initial Setup #
        #################

        # Setting all the inputs to "self.X" values so I can use it in update
        self.windowTitle = windowTitle
        self.configFile = configFile
        self.libraryFile = libraryFile
        self.assetDownloaderFilePath = assetDownloaderFilePath
        self.eventSolverFilePath = eventSolverFilePath

        # Find and set initial preference values
        self.textFont = getConfigVal(configFile, "textFont")
        self.textSize = int(getConfigVal(configFile, "textSize"))
        self.opacity = float(getConfigVal(configFile, "opacity"))
        self.logFolderPath = getConfigVal(configFile, "logFolderPath")

        # Always start with the deck tracker enabled, regardless of previous settings
        updateConfig(configFile, "deckTracker", "True")
        self.showTracker = True

        # This is so that we don't spam the user with tons of warnings if a log file can't be found
        self.warnedAboutLogFile = False
        # This keeps track of the last log path we warned about, so we know if we should update warnedAboutLogFile
        self.warnedlogFolderPath = ""

        ###############################
        # Creation of the Main Window #
        ###############################

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.tempWindow = None
        self.layout = QVBoxLayout()
        self.setWindowTitle(windowTitle)

        self.opponentPageButton = QPushButton("Open Opponent's GUDecks Page", self)

        # I wanted to call this, but you have to do the line beneath it instead for some reason:
        # self.opponentPageButton.clicked.connect(opponentsWebpage(logFolderPath))
        self.opponentPageButton.clicked.connect(lambda i: opponentsWebpage(self.logFolderPath))
        self.opponentPageButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.opponentPageButton)

        self.settingsButton = QPushButton("Settings", self)
        self.settingsButton.clicked.connect(self.settings)
        self.settingsButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.settingsButton)

        self.toggleDeckTrackerButton = QPushButton("Toggle Deck Tracker", self)
        self.toggleDeckTrackerButton.clicked.connect(lambda i: toggleConfigBoolean(self.configFile, "deckTracker"))
        self.toggleDeckTrackerButton.clicked.connect(self.update)
        self.toggleDeckTrackerButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.toggleDeckTrackerButton)

        self.deckTrackerLabel = QLabel()
        self.deckTrackerLabel.setFont(QFont(self.textFont, self.textSize))
        if (self.showTracker):
            self.layout.addWidget(self.deckTrackerLabel)

        self.setLayout(self.layout)
        self.show()

        # Update once per second
        self.my_timer = QtCore.QTimer()
        self.my_timer.timeout.connect(self.update)
        self.my_timer.start(1000)  # 1 sec

    # Constantly looping update to keep the deck tracker up to date
    def update(self):
        ######################
        # Update Preferences #
        ######################

        # Find and set current preference values
        self.textFont = getConfigVal(configFile, "textFont")
        self.textSize = int(getConfigVal(configFile, "textSize"))
        self.opacity = float(getConfigVal(configFile, "opacity"))
        self.logFolderPath = getConfigVal(configFile, "logFolderPath")

        self.showTracker = True
        if (getConfigVal(configFile, "deckTracker") == "False"):
            self.showTracker = False

        # Update Tracker based on new settings
        self.opponentPageButton.setFont(QFont(self.textFont, self.textSize))
        self.settingsButton.setFont(QFont(self.textFont, self.textSize))
        self.toggleDeckTrackerButton.setFont(QFont(self.textFont, self.textSize))
        self.deckTrackerLabel.setFont(QFont(self.textFont, self.textSize))
        self.setWindowOpacity(self.opacity)

        # If we have a different path than the one we previously warned about, we have no longer warned about the
        #   current log file
        if (self.warnedlogFolderPath != self.logFolderPath):
            self.warnedAboutLogFile = False

        ########################
        # Update the deck list #
        ########################

        startingDeckList = getStartingDeckList(self.logFolderPath, self.assetDownloaderFilePath, self.libraryFile)

        # This means that it couldn't find the log file, so it probably doesn't exist yet. Just wait for a bit.
        if (startingDeckList == -1):
            return

        # This means there wasn't a legal deck in the log file
        elif (startingDeckList == -2):
            # We can just wait, because there is only a 1-3 second delay between when the log file is refreshed to
            #   when the deck should be loaded
            return

        updatedList = getCardChanges(self.logFolderPath, self.eventSolverFilePath)

        if (updatedList == -1):
            if (self.warnedAboutLogFile):
                # We are already warned about the log file, so we just need the user to update the logfile
                return
            else:
                # We need to warn the user that the current log path isn't valid. This is extremely weird, though,
                #   since we've made it past startingDeckList. If this happens, there was probably a restructuring
                #   of the logs files, which would suck.
                alert = QMessageBox()
                alert.setText('No valid log file found. Please check path. [Debugging Code: 0102]')
                alert.exec()
                self.warnedAboutLogFile = True
                self.warnedlogFolderPath = self.logFolderPath
                return
        elif (updatedList == -2):
            # Event solver doesn't exist yet, so just wait
            return

        (drawnCards, shuffledCards) = updatedList

        currentDeck = getCurrentDeck(startingDeckList, drawnCards, shuffledCards, self.libraryFile)
        currentDeckText = deckListToText(currentDeck)
        if (self.showTracker):
            self.deckTrackerLabel.setText(currentDeckText)
            self.layout.addWidget(self.deckTrackerLabel)

        else:
            self.deckTrackerLabel.setText("")
            self.layout.removeWidget(self.deckTrackerLabel)

        #self.setLayout(self.layout)
        self.adjustSize()




    def settings(self):
        self.tempWindow = SettingsWindow(self.windowTitle, self.configFile, self.libraryFile, self.assetDownloaderFilePath,
                                         self.eventSolverFilePath)


class SettingsWindow(QWidget):
    def __init__(self, windowTitle, configFile, libraryFile, assetDownloaderFilePath, eventSolverFilePath):
        super().__init__()

        # Setting all the inputs to "self.X" values so I can use it in confirm
        self.configFile = configFile
        self.libraryFile = libraryFile
        self.assetDownloaderFilePath = assetDownloaderFilePath
        self.eventSolverFilePath = eventSolverFilePath

        # Find and set current preference values
        self.textFont = getConfigVal(configFile, "textFont")
        self.textSize = int(getConfigVal(configFile, "textSize"))
        self.opacity = float(getConfigVal(configFile, "opacity"))
        self.logFolderPath = getConfigVal(configFile, "logFolderPath")
        # We don't need deckTracker


        self.setWindowOpacity(self.opacity)
        self.setWindowTitle(windowTitle)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.layout = QVBoxLayout()

        self.updateNotify = True
        strToDisplay = "(Currently Enabled)"
        if (getConfigVal(self.configFile, "updateNotify") == "False"):
            self.updateNotify = False
            strToDisplay = "(Currently Disabled)"

        self.updateNotifyButton = QPushButton("Toggle Update Notifications " + strToDisplay, self)
        self.updateNotifyButton.clicked.connect(lambda i: toggleConfigBoolean(self.configFile, "updateNotify"))
        self.updateNotifyButton.clicked.connect(self.updateText)
        self.updateNotifyButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.updateNotifyButton)

        strToDisplay = "(Currently Enabled)"
        if (getConfigVal(self.configFile, "autoUpdate") == "False"):
            self.updateNotify = False
            strToDisplay = "(Currently Disabled)"

        self.autoUpdateButton = QPushButton("Toggle Automatic Updates " + strToDisplay, self)
        self.autoUpdateButton.clicked.connect(lambda i: toggleConfigBoolean(self.configFile, "autoUpdate"))
        self.autoUpdateButton.clicked.connect(self.updateText)
        self.autoUpdateButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.autoUpdateButton)

        self.textSizeLabel = QLabel("Enter desired text size (Currently " + str(self.textSize) + "):")
        self.textSizeLabel.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.textSizeLabel)

        self.textSizeEdit = QLineEdit("")
        self.textSizeEdit.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.textSizeEdit)

        self.textFontLabel = QLabel("Enter desired text font (Currently " + str(self.textFont) + "):")
        self.textFontLabel.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.textFontLabel)

        self.textFontEdit = QLineEdit("")
        self.textFontEdit.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.textFontEdit)

        self.opacityLabel = QLabel("Enter desired opacity (Currently " + str(self.opacity) + "; Range 0.25-1):")
        self.opacityLabel.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.opacityLabel)

        self.opacityEdit = QLineEdit("")
        self.opacityEdit.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.opacityEdit)

        self.pathLabel = QLabel("Enter path to 'FuelGames' log folder:")
        self.pathLabel.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.pathLabel)

        self.pathEdit = QLineEdit("")
        self.pathEdit.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.pathEdit)

        self.confirmButton = QPushButton("Apply", self)
        self.confirmButton.clicked.connect(self.confirm)
        self.confirmButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.confirmButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.cancel)
        self.cancelButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.cancelButton)

        self.setLayout(self.layout)
        self.show()

    def updateText(self):
        self.updateNotify = True
        strToDisplay = "(Currently Enabled)"
        if (getConfigVal(self.configFile, "updateNotify") == "False"):
            self.updateNotify = False
            strToDisplay = "(Currently Disabled)"

        self.updateNotifyButton.setText("Toggle Update Notifications " + strToDisplay)

        strToDisplay = "(Currently Enabled)"
        if (getConfigVal(self.configFile, "autoUpdate") == "False"):
            self.updateNotify = False
            strToDisplay = "(Currently Disabled)"

        self.autoUpdateButton.setText("Toggle Automatic Updates " + strToDisplay)

    def confirm(self):
        # 0 (Text Font)
        if (not str(self.textFontEdit.text()) == ""):
            updateTextFont = self.textFontEdit.text()
            updateConfig(self.configFile, "textFont", updateTextFont)

        # 1 (Text Size)
        if (not str(self.textSizeEdit.text()) == ""):
            if (str(self.textSizeEdit.text()).isdigit()):
                updateTextSize = int(self.textSizeEdit.text())

                if (updateTextSize < 5):
                    updateTextSize = 5
                elif (updateTextSize > 80):
                    updateTextSize = 80

                updateConfig(self.configFile, "textSize", updateTextSize)

        # 2 (Opacity)
        if (not str(self.opacityEdit.text()) == ""):

            if (str(self.opacityEdit.text()).replace(".", "", 1).isdigit() and
                    str(self.opacityEdit.text()).count(".") < 2):

                updateOpacity = float(self.opacityEdit.text())
                if (updateOpacity < 0.25):
                    updateOpacity = 0.25
                elif (updateOpacity > 1):
                    updateOpacity = 1
                updateConfig(self.configFile, "opacity", updateOpacity)

        # 3 (logFile)
        if (not str(self.pathEdit.text()) == ""):
            updateLogPath = str(self.pathEdit.text())

            if (not os.path.exists(updateLogPath)):
                alert = QMessageBox()
                alert.setText('Warning: Path not found. Please enter a valid path.')
                alert.exec()

            else:
                subDirs = [(updateLogPath + "\\" + d) for d in os.listdir(updateLogPath)
                           if os.path.isdir((updateLogPath + "\\" + d))]
                updateLogPath = max(subDirs, key=os.path.getmtime)
                updateConfig(self.configFile, "logFolderPath", updateLogPath)

        self.close()

    def cancel(self):
        self.close()



##########################
# Auto-Updater Functions #
##########################

# Compares two versions of the format X-Y-Z; numbers with hyphens in between
# If v1 > v2, return 1 (This shouldn't happen usually)
# If v1 == v2, return 0
# If v1 < v2, return -1
def compareVersions(v1, v2):
    splitV1 = v1.split("-")
    splitV2 = v2.split("-")

    # Which one is longer matters if the shorter one equals the longer one all the way to the end; if that's the case
    #   then the longer one is greater
    v1Longer = (len(splitV1) > len(splitV2))

    minLength = len(splitV1)
    maxLength = len(splitV2)
    if (v1Longer):
        minLength = len(splitV2)
    else:
        maxLength = len(splitV2)

    for n in range(minLength):
        if (int(splitV1[n]) > int(splitV2[n])):
            return 1
        elif (int(splitV1[n]) < int(splitV2[n])):
            return -1

    # At this point, we have a tie
    if (minLength == maxLength):
        return 0
    elif (minLength == len(splitV1)):
        return -1
    else:
        return 1


def findGithubVersion():
    githubData = urllib.request.urlopen("https://github.com/JMoore11235/GU_Deck_Tracker/")
    githubString = githubData.read().decode("utf8")
    return re.search('gu_tracker-v(.*).py" ', githubString).group(1).strip()


def openPatchNotesWebpage():
    webbrowser.open(("https://github.com/JMoore11235/GU_Deck_Tracker/blob/main/ChangeLog.md"), new=2, autoraise=True)


def updateAndRestart(configFile, updateVersion):

    # We are updating, so set justUpdated to True
    updateConfig(configFile, "justUpdated", "True")

    # Delete this file (Doesn't work; no permissions.)
    # os.chmod(sys.argv[0], 0o777)
    # os.remove(sys.argv[0])

    # subprocess.Popen("python -c \"import os, time; time.sleep(1); os.remove(r'{}');\"".format(sys.argv[0]), shell=True)

    # Download the .exe
    filename, headers = urllib.request.urlretrieve(
        "https://github.com/JMoore11235/GU_Deck_Tracker/releases/download/" + updateVersion +
        "/gu_tracker-v" + updateVersion + ".exe", "gu_tracker-v" + updateVersion + ".exe")


    # If people want to auto update with the .py file, uncomment this out

    ## Download the .py
    #urllib.request.urlretrieve(
    #    "https://github.com/JMoore11235/GU_Deck_Tracker/releases/download/" + updateVersion + "/gu_tracker-v" +
    #    updateVersion + ".py", "gu_tracker-v" + updateVersion + ".py")
    #
    ## Download the condensed_card_library.txt
    #urllib.request.urlretrieve(
    #    "https://github.com/JMoore11235/GU_Deck_Tracker/releases/download/" + updateVersion +
    #    "/condensed_card_library.txt", "condensed_card_library.txt")



    # Run the new version of the tracker and end this one
    subprocess.Popen(filename)
    sys.exit()

class JustUpdatedWindow(QWidget):
    def __init__(self, configFile, updateVersion):
        super().__init__()

        self.textFont = getConfigVal(configFile, "textFont")
        self.textSize = int(getConfigVal(configFile, "textSize"))
        self.opacity = float(getConfigVal(configFile, "opacity"))

        self.setWindowOpacity(self.opacity)
        self.setWindowTitle("Just Updated!")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.layout = QVBoxLayout()

        self.displayText = QLabel("You have just updated to version " + updateVersion + "!")
        self.displayText.setFont(QFont(self.textFont, self.textSize))
        self.displayText.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.displayText)

        self.openPage = QPushButton("View Patch Notes", self)
        self.openPage.clicked.connect(openPatchNotesWebpage)
        self.openPage.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.openPage)

        self.closeButton = QPushButton("Close", self)
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.closeButton)

        self.setLayout(self.layout)
        self.show()


class UpdateWindow(QWidget):
    def __init__(self, configFile, updateVersion):
        super().__init__()

        self.textFont = getConfigVal(configFile, "textFont")
        self.textSize = int(getConfigVal(configFile, "textSize"))
        self.opacity = float(getConfigVal(configFile, "opacity"))

        self.setWindowOpacity(self.opacity)
        self.setWindowTitle("Update Available!")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.layout = QVBoxLayout()

        self.updateAvailableText = QLabel("Version " + updateVersion + " is available now!\n\nYou can toggle " +
                                          "auto-updates and update notifications in the settings.")
        self.updateAvailableText.setFont(QFont(self.textFont, self.textSize))
        self.updateAvailableText.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.updateAvailableText)

        self.openPage = QPushButton("View Patch Notes", self)
        self.openPage.clicked.connect(openPatchNotesWebpage)
        self.openPage.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.openPage)

        self.updateNow = QPushButton("Update Now! (Will freeze for a little; don't worry!)", self)
        self.updateNow.clicked.connect(lambda i: updateAndRestart(configFile, updateVersion))
        self.updateNow.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.updateNow)

        self.closeButton = QPushButton("Continue without updating", self)
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setFont(QFont(self.textFont, self.textSize))
        self.layout.addWidget(self.closeButton)

        self.setLayout(self.layout)
        self.show()


def showJustUpdatedWindow(configFile, updateVersion):
    updateApp = QApplication([])
    updateApp.setStyle('Fusion')

    justUpdatedWindow = JustUpdatedWindow(configFile, updateVersion)

    # At this point we know we want to notify but not autoupdate

    # This is stolen from: https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    updateApp.setPalette(palette)

    # If notifications are off, don't message
    # Also, if autoUpdate is on then we don't need this window since we're updating anyway
    updateApp.exec()

    return justUpdatedWindow




def updateTracker(configFile, updateVersion):

    notify = True
    if (getConfigVal(configFile, "updateNotify") == "False"):
        notify = False

    autoUpdate = True
    if (getConfigVal(configFile, "autoUpdate") == "False"):
        autoUpdate = False

    # If auto updates are enabled, just update
    if (autoUpdate):
        updateAndRestart(configFile, updateVersion)
        return

    # If we don't want to be notified, then don't show this
    elif (not notify):
        return

    updateApp = QApplication([])
    updateApp.setStyle('Fusion')

    updateWindow = UpdateWindow(configFile, updateVersion)






    #At this point we know we want to notify but not autoupdate

    # This is stolen from: https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    updateApp.setPalette(palette)



    # If notifications are off, don't message
    # Also, if autoUpdate is on then we don't need this window since we're updating anyway
    updateApp.exec()

    return updateWindow



if __name__ == "__main__":

    # Current Version
    localVersion = "3-1"

    # defaults
    defaultFont = "Helvetica"
    defaultSize = 14
    defaultOpacity = 1
    # taken from https://stackoverflow.com/questions/2014554/find-the-newest-folder-in-a-directory-in-python
    log_path = "C:\\Users\\" + getpass.getuser() + "\\AppData\\LocalLow\\FuelGames"
    sub_dirs = [(log_path + "\\" + d) for d in os.listdir(log_path) if os.path.isdir((log_path + "\\" + d))]
    defaultLogFolderPath = max(sub_dirs, key=os.path.getmtime)

    # File Paths
    logPath = defaultLogFolderPath
    assetDownloaderFilePath = "/logs/latest/asset_downloader/asset_downloader_info.txt"
    eventSolverFilePath = "/logs/latest/event_solver/event_solver_info.txt"
    libraryFile = resource_path("condensed_card_library.txt")
    configFile = "config.txt"


    #Create a config.txt file if one does not already exist, then set current preferences based on that
    createConfig(configFile, defaultFont, defaultSize, defaultOpacity, defaultLogFolderPath)

    #####################
    # Check for updates #
    #####################

    gitHubVersion = findGithubVersion()
    versionComparison = compareVersions(gitHubVersion, localVersion)

    keepReference = None

    # This means we have a new update!
    if (versionComparison > 0):
        keepReference = updateTracker(configFile, gitHubVersion)

    windowTitle = "JMoney's Deck Tracker v" + str(localVersion)


    # Check to see if we haven't run this since updating it
    if (getConfigVal(configFile, "justUpdated") == "True"):
        justUpdatedWindow = showJustUpdatedWindow(configFile, localVersion)


    # After we've checked for updates, we know that we are no longer running this version for the first time
    #   (because when we update, we force a restart)
    updateConfig(configFile, "justUpdated", "False")

    app = QApplication([])
    app.setStyle('Fusion')


    mainWindow = MainWindow(windowTitle, configFile, libraryFile, assetDownloaderFilePath, eventSolverFilePath)

    # This is stolen from: https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    app.exec()


