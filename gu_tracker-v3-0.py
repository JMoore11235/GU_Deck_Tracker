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
def createConfig(configFile, font, size, opacity, logFilePath):
    if (os.path.exists(configFile)):
        return

    conFile = open(configFile, "w", encoding="utf8")

    conFile.write("textFont::==" + font + "\n")
    conFile.write("textSize::==" + str(size) + "\n")
    conFile.write("opacity::==" + str(opacity) + "\n")
    conFile.write("logFilePath::==" + logFilePath + "\n")
    conFile.write("deckTracker::==True\n")

    conFile.close()


# Line Number -> Value:
#   0 -> Text Font (textFont)
#   1 -> Text Size (textSize)
#   2 -> Opacity (opacity)
#   3 -> Log File Path (logFilePath)
#   4 -> Show Deck Tracker (deckTracker)
# Input: Config file, line of config to update (see above for correct line) and the value to update it to.
# Output: Just returns the updatedValue input
# Additional functionality: Updates the config file
def updateConfig(configFile, lineNumber, updatedValue):
    conFile = open(configFile, "r", encoding="utf8")
    lines = conFile.readlines()
    conFile.close()

    lines[lineNumber] = lines[lineNumber].split("::==")[0] + "::==" + str(updatedValue) + "\n"

    conFile = open(configFile, "w", encoding="utf8")
    conFile.writelines(lines)
    conFile.close()

    return updatedValue

# config.txt Line Number -> Value:
#   0 -> Text Font (textFont)
#   1 -> Text Size (textSize)
#   2 -> Opacity (opacity)
#   3 -> Log File Path (logFilePath)
#   4 -> Show Deck Tracker (deckTracker)
# Input: Config file and the line of config to return (see above for correct line)
# Output: The requested value
def getConfigVal(configFile, lineNumber):
    conFile = open(configFile, "r", encoding="utf8")
    lines = conFile.readlines()
    conFile.close()

    return lines[lineNumber].split("::==")[1].strip()


# Input: The name of the configFile
# Output: A list containing all of the values in the config file
def getPreferencesFromConfig(configFile):


    conf = open(configFile, "r", encoding="utf8")
    lines = conf.readlines()
    conf.close()

    splitLines = []
    for line in lines:
        addLine = line.split("::==")[1].strip()

        # Taken from: https://stackoverflow.com/questions/46647744/checking-to-see-if-a-string-is-an-integer-or-float
        # This just makes sure we are adding the correct type to preferences
        if (addLine.isdigit()):
            splitLines.append(int(addLine))
        elif (addLine.replace(".", "", 1).isdigit() and addLine.count(".") < 2):
            splitLines.append(float(addLine))
        else:
            splitLines.append(str(addLine))

    return splitLines


#####################
# Tracker Functions #
#####################

# Input: The name of a card you need the mana cost for and the relative path to condensed_card_library.txt
# Output: The mana cost of the card
def getManaCost(name, libraryFile):
    retNext = False
    allCards = open(resource_path(libraryFile), "rt", encoding="latin-1")

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


def toggleDeckTracker(configFile):
    currVal = getConfigVal(configFile, 4)
    if (currVal == "True"):
        updateConfig(configFile, 4, "False")
    else:
        updateConfig(configFile, 4, "True")


# Main Window which includes the deck tracker
class MainWindow(QWidget):
    def __init__(self, configFile, libraryFile, assetDownloaderFilePath, eventSolverFilePath):
        super().__init__()

        #################
        # Initial Setup #
        #################

        # Setting all the inputs to "self.X" values so I can use it in update
        self.configFile = configFile
        self.libraryFile = libraryFile
        self.assetDownloaderFilePath = assetDownloaderFilePath
        self.eventSolverFilePath = eventSolverFilePath

        # Find and set initial preference values
        # Preferences should be: 0 -> textFont, 1 -> textSize, 2 -> opacity, 3 -> logFolderPath,
        #   4 -> Show Deck Tracker (deckTracker)
        preferences = getPreferencesFromConfig(configFile)
        self.textFont = preferences[0]
        self.textSize = preferences[1]
        self.opacity = preferences[2]
        self.logFolderPath = preferences[3]
        self.showTracker = True
        if (preferences[4] == "False"):
            self.showTracker = False

        # This is so that we don't spam the user with tons of warnings if a log file can't be found
        self.warnedAboutLogFile = False
        # This keeps track of the last log path we warned about, so we know if we should update warnedAboutLogFile
        self.warnedLogFilePath = ""

        ###############################
        # Creation of the Main Window #
        ###############################

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.tempWindow = None
        self.layout = QVBoxLayout()
        self.setWindowTitle("JMoney's Deck Tracker v3.0")

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
        self.toggleDeckTrackerButton.clicked.connect(lambda i: toggleDeckTracker(self.configFile))
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
        # Preferences should be: 0 -> textFont, 1 -> textSize, 2 -> opacity, 3 -> logFolderPath,
        #   4 -> Show Deck Tracker (deckTracker)
        preferences = getPreferencesFromConfig(self.configFile)
        self.textFont = preferences[0]
        self.textSize = preferences[1]
        self.opacity = preferences[2]
        self.logFolderPath = preferences[3]
        self.showTracker = True
        if (preferences[4] == "False"):
            self.showTracker = False

        # Update Tracker based on new settings
        self.opponentPageButton.setFont(QFont(self.textFont, self.textSize))
        self.settingsButton.setFont(QFont(self.textFont, self.textSize))
        self.toggleDeckTrackerButton.setFont(QFont(self.textFont, self.textSize))
        self.deckTrackerLabel.setFont(QFont(self.textFont, self.textSize))
        self.setWindowOpacity(self.opacity)

        # If we have a different path than the one we previously warned about, we have no longer warned about the
        #   current log file
        if (self.warnedLogFilePath != self.logFolderPath):
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
                self.warnedLogFilePath = self.logFolderPath
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
        self.tempWindow = SettingsWindow(self.configFile, self.libraryFile, self.assetDownloaderFilePath,
                                         self.eventSolverFilePath)


class SettingsWindow(QWidget):
    def __init__(self, configFile, libraryFile, assetDownloaderFilePath, eventSolverFilePath):
        super().__init__()

        # Setting all the inputs to "self.X" values so I can use it in confirm
        self.configFile = configFile
        self.libraryFile = libraryFile
        self.assetDownloaderFilePath = assetDownloaderFilePath
        self.eventSolverFilePath = eventSolverFilePath

        # Find and set current preference values
        # Preferences should be: 0 -> textFont, 1 -> textSize, 2 -> opacity, 3 -> logFolderPath
        #   4 -> Show Deck Tracker (deckTracker)
        preferences = getPreferencesFromConfig(self.configFile)
        self.textFont = preferences[0]
        self.textSize = preferences[1]
        self.opacity = preferences[2]
        self.logFolderPath = preferences[3]
        # We don't need deckTracker


        self.setWindowOpacity(self.opacity)
        self.setWindowTitle("JMoney's Deck Tracker v3.0")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout()

        self.textSizeLabel = QLabel("Enter desired text size (Currently " + str(self.textSize) + "):")
        self.textSizeLabel.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.textSizeLabel)

        self.textSizeEdit = QLineEdit("")
        self.textSizeEdit.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.textSizeEdit)

        self.textFontLabel = QLabel("Enter desired text font (Currently " + str(self.textFont) + "):")
        self.textFontLabel.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.textFontLabel)

        self.textFontEdit = QLineEdit("")
        self.textFontEdit.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.textFontEdit)

        self.opacityLabel = QLabel("Enter desired opacity (Currently " + str(self.opacity) + "; Range 0.25-1):")
        self.opacityLabel.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.opacityLabel)

        self.opacityEdit = QLineEdit("")
        self.opacityEdit.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.opacityEdit)

        self.pathLabel = QLabel("Enter path to 'FuelGames' log folder:")
        self.pathLabel.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.pathLabel)

        self.pathEdit = QLineEdit("")
        self.pathEdit.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.pathEdit)

        self.confirmButton = QPushButton("Apply", self)
        self.confirmButton.clicked.connect(self.confirm)
        self.confirmButton.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.confirmButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.cancel)
        self.cancelButton.setFont(QFont(self.textFont, self.textSize))
        layout.addWidget(self.cancelButton)

        self.setLayout(layout)
        self.show()

    def confirm(self):

        # config.txt Line Number -> Value:
        #   0 -> Text Font (textFont)
        #   1 -> Text Size (textSize)
        #   2 -> Opacity (opacity)
        #   3 -> Log File Path (logFilePath)
        #   4 -> Show Deck Tracker (deckTracker)

        # 0 (Text Font)
        if (not str(self.textFontEdit.text()) == ""):
            updateTextFont = self.textFontEdit.text()
            updateConfig(self.configFile, 0, updateTextFont)

        # 1 (Text Size)
        if (not str(self.textSizeEdit.text()) == ""):
            if (str(self.textSizeEdit.text()).isdigit()):
                updateTextSize = int(self.textSizeEdit.text())

                if (updateTextSize < 5):
                    updateTextSize = 5
                elif (updateTextSize > 80):
                    updateTextSize = 80

                updateConfig(self.configFile, 1, updateTextSize)

        # 2 (Opacity)
        if (not str(self.opacityEdit.text()) == ""):

            if (str(self.opacityEdit.text()).replace(".", "", 1).isdigit() and
                    str(self.opacityEdit.text()).count(".") < 2):

                updateOpacity = float(self.opacityEdit.text())
                if (updateOpacity < 0.25):
                    updateOpacity = 0.25
                elif (updateOpacity > 1):
                    updateOpacity = 1
                updateConfig(self.configFile, 2, updateOpacity)

        # 3 (logFile)
        if (not str(self.pathEdit.text()) == ""):
            updateLogPath = str(self.pathEdit.text())
            subDirs = [(updateLogPath + "\\" + d) for d in os.listdir(updateLogPath)
                       if os.path.isdir((updateLogPath + "\\" + d))]
            updateLogPath = max(subDirs, key=os.path.getmtime)
            updateConfig(self.configFile, 3, updateLogPath)

        self.close()

    def cancel(self):
        self.close()









if __name__ == "__main__":

    #defaults
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


    app = QApplication([])
    app.setStyle('Fusion')


    mainWindow = MainWindow(configFile, libraryFile, assetDownloaderFilePath, eventSolverFilePath)

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


