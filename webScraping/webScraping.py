''' This file is designed to work in conjunction with static/listOfResources.csv
    to gather data txt from a specific url and output it to a temporary output csv file
    under temp/

    Often times, the listOfResources.csv's urls will be "summary pages", pointing to detailed
    urls containing useful information that needs to be scraped.

    The eventual output of this program is to have a csv table full of data that can be used to
    populate or update the entries in the musictracks.db database. (This is achieved through other
    python modules, such as "dbManagement", for instance).
'''

import csv
import datetime
#import wikipediaapi # this is actually loaded in in wikiScraper which is imported in its entirety below
import globalVars as g
import sys, os

sys.path.append(os.path.abspath(os.path.join(g.pathToUtils, '')))
from utils.utils import *

from wikiScraper import *

DEBUG = g.DEBUG
ERRORLOG = g.ERRORLOG
LOG = g.LOG
logFile = g.logFile
dirname = g.dirname
mainPathDirname = dirname[0:dirname.rfind("/")]
listOfResourcesFilePath = g.listOfResourcesFilePath

Test(sys.argv) # Any quick tests I need to do, I execute right away - see wikiScraper.py

YMessage(f".\n.", logOption=LOG)
YMessage(f"**************************************************************************************************************************", logOption=LOG)
YMessage(f"WebScraping execution started", logOption=LOG)
YMessage(f"=============================================", logOption=LOG)
YMessage(f"mainPathDirname={mainPathDirname}", logOption=LOG)
timeProgramStarted = datetime.datetime.now()
YMessage(f"Log started at {str(timeProgramStarted)}", logOption=LOG)
YMessage(f"---------------------------------------------", logOption=LOG)

# Open the CSV file
YMessage(f"About to try opening CSV {str(listOfResourcesFilePath)}", logOption=LOG)


with open(listOfResourcesFilePath, newline='') as csvfile:
    # this file contains the description of resources for WebSCraping execution
    # (typically under static/listOfResources.csv)
    # 1) Wikipedia resources

    # Create a DictReader object from CSV
    YMessage(f"About to create DictReader object from the opened CSV:", logOption=LOG)
    csvreader = csv.DictReader(csvfile)
    YMessage(f"csvreader = {csvreader}", logOption=LOG)

    # Iterate over the rows in the CSV
    for row in csvreader:

        if (row["type"] == "summaryPage") and ("wikipedia" in row["url"]):
            YMessage(f"CALLING ExtractWikipediaData(dict={str(row)})\n", logOption=LOG)
            response = ExtractWikipediaData( row )

            if -1 == response:
                YMessage(f"ExtractWikipediaData() returned an error. Stopping (time elapsed = {datetime.datetime.now() - timeProgramStarted})", logOption=ERRORLOG)
                exit(-1)

            YMessage(f"ExtractWikipediaData() returned '{response}'. Stopping the progran (time elapsed = {datetime.datetime.now() - timeProgramStarted})", logOption=LOG)

