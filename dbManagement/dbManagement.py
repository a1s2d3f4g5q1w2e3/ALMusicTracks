''' This file is designed to work in conjunction with static/urlRoots.csv and
    data gathered by the WebScraping module in temp/peopleFromWebScraping.csv (or whatever I call it these days)
    to populate/manage the musictracks.db sqlite3 database.

    The correctly populated musictracks.db provides data for my "musictracks website" (see app.py and templates).

    It is important to make sure to populate tables correctly and use UNIQUE to avoid duplicates etc.

    The musictracks database consists of interrelated tables.
    20240710_2047: As of today it contains:
        -refsT (references table) supported by urlRootsT and urlSuffixesT
            Data about any item in the database comes from a source (for now Wikipedia pages).
            This source is treated as a unique "reference".
            The wikipedia pages are splits up as "<urlRoot><urlMain><urlSuffix><urlSuffixVal>
            For example: https://en.wikipedia.org/w/index.php?title=Michel_van_der_Aa&oldid=1218427186
            https://en.wikipedia.org/w/index.php?title= is a common root for many articles.
            Michel_van_der_Aa is the main part of the url - a unique page name
            &oldid= is a "suffix"
            1218427186 is the "suffixVal"
            I store roots and suffixes in urlRootsT and urlSuffixesT tables, allowing me to refer to the
            needed strings from refsT via INTEGER ids corresponding to those table's correct rows

        -peopleT (people table) supported by referencesT
            This maintains a database of every person for whom a reference exists in refT.
            Thus every person gets a unique id (associated with a unique wikiPageNameOrLike string)

        -peopleNamesFmlEngT (people's First Middle and Last names in english) supported by refT peopleT
            This table maintains the correct names for each person listed in peopleT. Typically, refId
            (i.e. id of refT table) would be the same as refId of peopleT's row for personId (i.e. id of
            peopleT table). In other words, most times one wikipedia page would maintain correct information
            for multiple aspects about the same person (name, full name, original language name, dob etc.)
            but it's also possible that a different reference source would be used to specify a particular
            piece of data, like the person's name. (Conflicting reference sources will be treated through
            a "dispute" system and coded in later versions).

        -peopleNamesFullBirthDocT (people's name as in the original Birth Document) supported by refT peopleT
            All the same as with peopleNamesFmlEngT, except dealing with names in original Birth Documents

        -peopleNamesFullEngT (people's full name in english) supported by refT peopleT
            All the same as with peopleNamesFmlEngT, except dealing with full names

        -peopleNamesPseudonymsT (people's pseudonyms ) supported by refT peopleT
            All the same as with peopleNamesFmlEngT, except dealing with any pseudonyms used for this person

        -peopleDobT (people's date's of birth) supported by refT peopleT placesT
            All the same as with peopleNamesFmlEngT, except dealing with the date of birth values
            This table also makes references to places of birth, if known

        -placesT (supported by refsT)
            This table, similarly to peopleT, maintains a list of all geographical places also referred to in refsT

        ...and many similar tables

        Some are place holders and will be filled and used in later versions of this project


        This module is the entryway to populating the database from the above mentioned CSV file from WebScraping.
        20240711_0945: Currently, it does not have the ability to intelligently merge in new data from WebScraping
            if it conflicts with the data already in the database. This is a TODO

'''


import csv
import datetime
import os, sys
import time
from dbMgmtHelpers import *

if "/dbManagement/" in __file__:
    import gVars as g
    '''according to chatGPT doing import dbManagement.gvars as g is an "absolute import"
    and it solved the problem of using helper functions inside app.py
    However, when I then tried to run dbManagement.py from command line, I got:
    ModuleNotFoundError: No module named 'dbManagement.gVars'; 'dbManagement' is not a package
    Luckily, I was able to solve it.
    '''
else:
    import dbManagement.gVars as g

fn = sys.argv[0] # file name

print(f"g.pathToUtils={g.pathToUtils}")
sys.path.append(os.path.abspath(os.path.join(g.pathToUtils, '')))
from utils.utils import *

DEBUG = g.DEBUG
ERRORLOG = g.ERRORLOG

g.logFile.write("Log started at " + str(datetime.datetime.now()) + "\n") if DEBUG else ""

# Open the resources CSV file
YMessage(f"about to try opening the list of resources CSV {str(g.listOfResourcesCsvPath)}", logOption=LOG)
with open(g.listOfResourcesCsvPath, newline='') as csvfile:
    # Create a DictReader object
    YMessage(f"About to read in the opened CSV", logFile=g.logFile, logOption=LOG)
    csvreader = csv.DictReader(csvfile)

    # Iterate over the rows in the CSV file
    for row in csvreader:
        if (row["type"] == "summaryPage") and ("wikipedia" in row["url"]):
                    # we have the row that describes the wikipedia summary page and associated materials
                    # 20240711_0952: Only wikipedia summary pages can be processed by
                    # UpdateDBTablesFromCsv
            YMessage(f"CALLING UpdateDBTables(dict={str(row)})", logFile=g.logFile, logOption=LOG)
            response = UpdateDBTablesFromCsv(row)

            if -1 == response:
                YMessage(f"UpdateDBTables({row}) returned an error. Stopping", logFile=g.logFile, logOption=ERRORLOG)
                exit(-1)

g.logFile.close()

# end of program
