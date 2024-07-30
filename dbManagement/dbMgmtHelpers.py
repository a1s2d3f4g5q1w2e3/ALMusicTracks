
#import csv
import datetime
import os, sys

'''To run app.py that references this file from a different folder, I needed to make this call:
    import dbManagement.gVars as g
    but, unfortunately, to run dbManagement.py by itself doesn't work like that.
    had to change it back to
    import gVars as g
    So, what is the solution where both work, whether I reference it from another app
    or run dbmanagement.py within this folder?
    20240729_1723: See solution below
'''

import math
#import inspect

import time
import types
from cs50 import SQL
if not "dbManagement.dbMgmtHelpers" in __name__: # This happens when I run dbmanagement.py directly (from inside its folder)
    print(f"__file__ =={__file__}\n__name__={__name__}")
    import gVars as g
else:
    import dbManagement.gVars as g

sys.path.append(os.path.abspath(os.path.join(g.pathToUtils, ''))) # have to do this to add 13317412 top project folder to path and not include "utils" so that pyname sees it
print(sys.path)
from utils.utils import *

DEBUG = g.DEBUG
LOG = g.LOG
ERRORLOG = g.ERRORLOG
logFile = g.logFile
#logFile = g.logFile


def AddAnyMissingColumnsToTable(db, tableName): # all missing columns are added based on global variable tcols dictionary
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    if not IsTableExists(db, tableName):
        YMessage(f"Could not find table '{tableName}", logFile, ERRORLOG)
        exit()

    for key in g.tcols: # First check if all columns exist:
        if tableName in key:
            YMessage(f"checking if column {g.tcols[key]} exists in {tableName}", logFile, LOG)

            if not IsColumnExistsInTable(db, tableName, g.tcols[key][0]):
                YMessage(f"About to add a missing column {g.tcols[key][0]} to '{tableName}'", logFile, LOG)
                AddMissingColumnToTable(db, g.tcols[key][0], g.tcols[key][1], tableName)

            # else do nothing, the column is alread there

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return 0


def AddMissingColumnToTable(db, colName, colType, tableName): # Helper function to AddAnyMissing
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colType={colType}, tableName={tableName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    #VerifyDbIsValid(db) # Not doing it because we want to eliminate unnecessary calls
    # TODO: check table exists
    response = db.execute(
        f"ALTER TABLE {tableName} ADD COLUMN {colName} {colType}"
    )
    # TODO: check that the column was actually created

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return


def AddResponseIdsToList(response, colName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(response={response}, colName={colName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnList = []

    for dict in response:
        returnList.append(dict[colName])

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnList


def CopyDbTableToAnotherTable(db, sourceTableName, targetTableName, mappingDict, options=""):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, sourceTableName={sourceTableName}, targetTableName={targetTableName}, mappingDict={mappingDict}, options={options}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = ""

    # first check that both tables exist
    if not IsTableExists(db, sourceTableName):
        YMessage(f"Could not find table '{sourceTableName}", logFile, ERRORLOG)
        exit()

    if not IsTableExists(db, targetTableName):
        YMessage(f"Could not find table '{targetTableName}", logFile, ERRORLOG)
        exit()

    for sourceCol in mappingDict:

        if not IsColumnExistsInTable(db, sourceTableName, sourceCol):
            YMessage(f"Could not find column '{sourceCol}' in '{targetTableName}'", logFile, ERRORLOG)
            exit()

        if not IsColumnExistsInTable(db, targetTableName, mappingDict[sourceCol]):
            YMessage(f"Could not find column 'mappingDict[sourceCol]' in '{targetTableName}'", logFile, ERRORLOG)
            exit()

    sourceData = db.execute(
        f"SELECT * from {sourceTableName} "
    )
    NMessage(f"sourceData={sourceData}", logFile, ERRORLOG)

    if sourceData:
        for tableRow in sourceData:
            # buld the SET commands
            setCommands = ""
            colList = ""
            valList = ""
            firstCommand = True
            for sourceCol in mappingDict:

                if not firstCommand:
                    setCommands = f"{setCommands}, {mappingDict[sourceCol]} = '{tableRow[sourceCol]}'"
                    colList = f"{colList}, {mappingDict[sourceCol]}"
                    valList = f"{valList}, '{tableRow[sourceCol]}'"

                else:
                    firstCommand = False
                    setCommands = f"{mappingDict[sourceCol]} = '{tableRow[sourceCol]}'"
                    colList = f"{mappingDict[sourceCol]}"
                    valList = f"'{tableRow[sourceCol]}'"

            if options == "":
                YMessage(f"colList={colList} valList={valList}", logFile, LOG)
                response = db.execute(
                    f"INSERT INTO '{targetTableName}' ({colList})"
                    f"VALUES ({valList})"
                )

            else:
                YMessage(f"setCommands={setCommands}", logFile, LOG)
                response = db.execute(
                    f"UPDATE {targetTableName} "
                    f"SET {setCommands}"
                )



    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnVal


def CreateDbTableIfNotExist(db, tableName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    columnCreationCommands = ""
    firstCommandSet = False
    for key in g.tcols: # Will walk through our many column names and create commands for db.execute
        if tableName + '_' in key:
            YMessage(f"Adding column {g.tcols[key][0]} {g.tcols[key][1]} into table {tableName} (if not exist)", logFile, LOG)

            if firstCommandSet:
                columnCreationCommands = columnCreationCommands + ',\n' + f'{g.tcols[key][0]} {g.tcols[key][1]}'

            else:
                columnCreationCommands = columnCreationCommands + f'{g.tcols[key][0]} {g.tcols[key][1]}'
                firstCommandSet = True

    # after the loop is done we add the final closing quote
    columnCreationCommands = columnCreationCommands + '\n'
    YMessage(f"columnCreationCommands= {columnCreationCommands}", logFile, LOG)
    response = db.execute(
        "CREATE TABLE IF NOT EXISTS ? ( "
            f"id INTEGER PRIMARY KEY NOT NULL UNIQUE, "
            f"{columnCreationCommands}"
            f")",
            tableName
    )

    YMessage(f"creation response={response}", logFile, LOG)

    if not response:
        YMessage(f"Something went wrong and '{tableName}' table wasn't created", logFile, LOG)
        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return response


def CreateMissingColumns(db, tableName):
    AddAnyMissingColumnsToTable(db, tableName)
    return


def FilterDbResponse(response1, response1ColName, response2, response2ColName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(response1={str(response1)}, response1ColName={response1ColName}, response2={response2}, response2ColName={response2ColName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    filteredResponse = {}
    exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return filteredResponse


def GetDbDataFromSearch(db, mainTableName, searchDictLists, processedDictListContainer, htmlNamePrefixLen, htmlResultsNamePrefixLen, includeRefs=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, mainTableName={mainTableName}, searchDictLists={searchDictLists}, processedDictListContainer={processedDictListContainer}, htmlNamePrefixLen={htmlNamePrefixLen}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
        # The most important function in that
        # -it receives data from the 3 search parameters rows of the searchPeople page (searchDictLists)
        # -it parses the data in those rows to prepare the "processedDictListContainer"
        # -it prepares all the parts of the database query call "select commands, optional left join commands and where commands"
        # If everything is coded correctly, it should result in a successful retrieval of data from the database (if it matches the)\
        # search parameters.

    yyyyAdjustmentValueForConsistentNumber = 20000 # necessary to be able to put together YYYYMMDD dates as integers even if YYYY is a negative (BC date)
    yyyyyMultiplyFactor = 10000

    NMessage(f"_______________________________________________________________")

    selectColsStr = "" # chosenCols will be probably used to set this string
    allCols = [] # stores every column from the table, in case the user never selects specific columns in the html search criteria
    chosenCols = [] # stores just the select columns
    chosenColsHeads = [] # stores titles of the chosen columns to be able to display them above the results table in html

    optLeftJoinStr = "" # if data from certain columns are selected (whether to display on to search, this needs to be set)
    allLeftJoinDict = {} # similar function as allCols (if no cols are chosen)
    optLeftJoinDict = {} # stores data only when there is a value entered (dict will make it easy to create a string - same will be overwritten, not appended)

    whereCommandsStr = ""
    colCommands = "" # for building stuff like dobYgr * 10000 + gobMgr * 100 etc

    retrievedColAsName = "" # stores column name used in the AS part of SELECT statment and then in the WHERE ( col operations ) statement
    leftJoinTableAsName = "" # stores table name used in chosen/allCols (SELECT statement) and also all/optLeftJoinDict
    dataColName = "" # stores column name used in the "data" table (e.g. placeNameEng in placesNamesEngT table)
    leftJoinAlreadyTableName = "" # name of the table that's supposed to be already joined previously by a prev LEFT JOIN statement

    if mainTableName == g.t['peopleTableName']:
        leftJoinAlreadyTableName = g.t['peopleNamesFmlEngTableName'] # we will assume that this is the main table for looking up information about people - their names

    else:
        YMessage(f"not ready to process {mainTableName} yet", logOption=LOG)
        exit()

    dataTableName = "" # Stores the name of the table associated with dataColName.
                       # Used to define the name after LEFT JOIN statement (opt/allLeftJoinDict)
    optLeftJoinDictCurrRelColName = "" # stores column name

    useThisColName = "useThis" # used in every important table to allow for picking among conflicting sources - might need a better way to set it

    tablesRelDictKey = "" # set with the name of the relTableDict dictionary key which is <leftJoinAlreadyTableName>_<dataColName>

    lastNameSelected = False # I ran into a problem with my LEFT JOIN adding logic in regards to this table, so trying a quick fix solution
    sr = 0 # search row (html search criteria table)

    ##############################################################################
    # Parse user entry data in the "searchPeople" form
    # top line (sr == 0) is for selecting which columns
    # to display in the output table (if nothing chosen - all).
    # The other lines are used to prepare processedDictListContainer,
    # the values of which will be used to interrogate the database
    # it is currently located inside searchDictLists dictionary
    for dictList in searchDictLists:

        for dict in dictList:
            htmlNameUnderscorePos = dict['name'].find("_")
            currTableName = dict['name'][htmlNamePrefixLen:htmlNameUnderscorePos] # My html field names are set in appGVars.py under searchFields
            currColName = dict['name'][htmlNameUnderscorePos + 1:999]

            dataColName = currColName
            tablesRelDictKey = f"{currTableName}_{currColName}"
            retrievedColAsName = f"{'x' * htmlResultsNamePrefixLen}{tablesRelDictKey}"
            dataTableName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictJoinNewTNameIdx]

            leftJoinAlreadyTableName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictAlreadyJoinedTNameIdx]
            leftJoinTableAsName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictTableAsNameIdx]
            optLeftJoinDictCurrRelColName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictSharedIdsColNameIdx]
            optLeftJoinDictCurrRelColNameNewTable = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictSharedIdsColNameNewTableIdx] #optional, usually blank, because same col name into two tables when LEFT JOIN

            if 0 == sr: # top search row on searchPeople route (index html) that defines which columns we want to show in the output table
                currKey = dict['name'][htmlNamePrefixLen:999]

                if not currKey in g.tableRelsDict:
                    YMessage(f"{currKey} not in g.tableRelsDict =>{g.tableRelsDict}", logFile, LOG)

                    exit()

                if dict['valFrom'] == "1":
                    YMessage(f"valFrom==1 -> dict['name']={dict['name']} dataColName={dataColName}", logFile, LOG)

                    if not 'url' == dataColName:
                        chosenCols.append(f"{leftJoinTableAsName}.{dataColName} AS {retrievedColAsName}")

                    elif includeRefs:
                        #!!! Concat didn't work with db.execute calls but doing || concatenation operator worked
                        '''e.g. concat(peopleNamesFmlT$refsT$urlRootsT.urlRoot, peopleNamesFmlT$refsT.urlMain,
                            peopleNamesFmlT$refsT$urlSuffixesT.urlSuffix, peopleNamesFmlT$refsT.urlSuffixVal
                            )
                            AS xxxxpeopleNamesFmlEngT_url,'''
                        chosenCols.append(
                            f"{leftJoinTableAsName}${g.t['urlRootsTableName']}.{g.tcols['urlRootsT_urlRootColHead'][0]} || "
                                    f"{leftJoinTableAsName}.{g.tcols['refsT_urlMainColHead'][0]} || "
                                    f"{leftJoinTableAsName}${g.t['urlSuffixesTableName']}.{g.tcols['urlSuffixesT_urlSuffixColHead'][0]} || "
                                    f"{leftJoinTableAsName}.{g.tcols['refsT_urlSuffixValColHead'][0]} "
                                    f"AS {retrievedColAsName}"
                                    )

                        OptLeftJoinProcessing(optLeftJoinDict, "refs", leftJoinTableAsName, dataTableName, leftJoinAlreadyTableName,
                                              optLeftJoinDictCurrRelColName, optLeftJoinDictCurrRelColNameNewTable, useThisColName)

                    # else we do not want to include the references

                    if currTableName != g.t['peopleNamesFmlEngTableName']: # this is for tables outside of the one in the FROM statement
                        YMessage(f"1)currTable=={currTableName}", logFile, LOG)

                        OptLeftJoinProcessing(optLeftJoinDict, "dob or dod", leftJoinTableAsName, dataTableName, leftJoinAlreadyTableName,
                                              optLeftJoinDictCurrRelColName, optLeftJoinDictCurrRelColNameNewTable, useThisColName)

                    else: # currTableName == g.t['peopleNamesFmlEngTableName']
                        lastNameSelected = True

                if not 'url' == dataColName:
                    allCols.append(f"{leftJoinTableAsName}.{dataColName} AS {retrievedColAsName}")

                elif 'url' == dataColName and includeRefs:
                    allCols.append(
                                f"{leftJoinTableAsName}${g.t['urlRootsTableName']}.{g.tcols['urlRootsT_urlRootColHead'][0]} || "
                                    f"{leftJoinTableAsName}.{g.tcols['refsT_urlMainColHead'][0]} || "
                                    f"{leftJoinTableAsName}${g.t['urlSuffixesTableName']}.{g.tcols['urlSuffixesT_urlSuffixColHead'][0]} || "
                                    f"{leftJoinTableAsName}.{g.tcols['refsT_urlSuffixValColHead'][0]} "
                                    f"AS {retrievedColAsName}")
                    OptLeftJoinProcessing(allLeftJoinDict, "refs", leftJoinTableAsName, dataTableName, leftJoinAlreadyTableName,
                                              optLeftJoinDictCurrRelColName, optLeftJoinDictCurrRelColNameNewTable, useThisColName)

                if currTableName != g.t['peopleNamesFmlEngTableName'] and not lastNameSelected:

                        SetOptLeftJoinDictKeyVal(allLeftJoinDict,
                                                    leftJoinTableAsName,
                                                    dataTableName,
                                                    leftJoinTableAsName,
                                                    leftJoinAlreadyTableName,
                                                    optLeftJoinDictCurrRelColName,
                                                    optLeftJoinDictCurrRelColName,
                                                    useThisColName)

            elif 1 == sr: # second search row

                if dict['valFrom'] != "": # means we have a user entry in this field
                    SetDictListValue(processedDictListContainer, 'name', dict['name'], 'valFrom', dict['valFrom'])

                    if currTableName != g.t['peopleNamesFmlEngTableName']:

                           OptLeftJoinProcessing(optLeftJoinDict, "dob or dod", leftJoinTableAsName, dataTableName, leftJoinAlreadyTableName,
                                                 optLeftJoinDictCurrRelColName, optLeftJoinDictCurrRelColNameNewTable, useThisColName)
            elif 2 == sr:

                if dict['valFrom'] != "": # means we have a user entry in this field
                    SetDictListValue(processedDictListContainer, 'name', dict['name'], 'valTo', dict['valFrom'])

                    if currTableName != g.t['peopleNamesFmlEngTableName']:
                         OptLeftJoinProcessing(optLeftJoinDict, "dob or dod", leftJoinTableAsName, dataTableName, leftJoinAlreadyTableName,
                                               optLeftJoinDictCurrRelColName, optLeftJoinDictCurrRelColNameNewTable, useThisColName)

            #cols.append()
            #vals.append(str(valuesDict[key]).replace("'","%27").replace('"',"%22"))
        sr = sr + 1

        # end of the for loop that walks through the search terms 3 row table
    YMessage(f"-------------------------------------------------end of search rows processing -------------------------------------------------------------", logOption=LOG)
    YMessage(f"processedDictListContainer={processedDictListContainer}", logOption=LOG)

    if not chosenCols: # then we assume that the user wants alls the available columns
        chosenCols = allCols
        optLeftJoinDict = allLeftJoinDict # we will need to LEFT JOIN all tables since we need data for all columns

    SetColHeadsList(chosenColsHeads, chosenCols, 'x' * htmlResultsNamePrefixLen)

    if not lastNameSelected:
        optLeftJoinDict = allLeftJoinDict

    NMessage(f"optLeftJoinDict={optLeftJoinDict}", logFile, LOG)
    NMessage(f"allLeftJoinDict={allLeftJoinDict}", logFile, LOG)


    selectColsStr = ', '.join(chosenCols) # https://stackoverflow.com/questions/12453580/how-to-concatenate-join-items-in-a-list-to-a-single-string
    for key in optLeftJoinDict:

        if optLeftJoinDict[key]:
            # we rely on the good ordering of the optLeftJoinDict to make sure we include the tables in the right order
            optLeftJoinStr = f"{optLeftJoinStr} {optLeftJoinDict[key]}\n"

    NMessage(f"selectColsStr={selectColsStr} from chosenCols={chosenCols}\nallCols={allCols} ", logOption=LOG)
    YMessage(f"optLeftJoinStr={optLeftJoinStr} ", logOption=LOG)


    okToAddCommands = False
    currTableName = ""
    currValFrom = ""
    currValTo = ""
    dobYYYYMMDDFrom, dobYYYYMMDDFromBitsCollected = 0, 0
    dobYYYYMMDDTo, dobYYYYMMDDToBitsCollected = 0, 0
    dodYYYYMMDDFrom, dodYYYYMMDDFromBitsCollected = 0, 0
    dodYYYYMMDDTo, dodYYYYMMDDToBitsCollected = 0, 0

    # Next Step: walk through each seqrch query entry
    # process related boxes together - e.g. YMD
    # prepare whereCommandsStr for correct tables
    # we already have selectColStr and optLeftJoinStr
    if mainTableName == g.t['peopleTableName']:
        whereCommandsStr = f"WHERE {g.t['peopleNamesFmlEngTableName']}.{useThisColName} = 1 " # for people related searches this will be the initial where command

    else:
        YMessage( f"non {mainTableName} table searches haven't been implemented yet", logOption=LOG)

        exit()

    YMessage(f"*************************starting the walk through processedDictListContainer to build the 'WHERE commands'***************************", logFile, LOG)
    for currDict in processedDictListContainer:
        # from html box name
        # parse out sourceTable AND
        # colName of the dataTable (dataCol)
        # then set dataTable name

        YMessage(f"currDict={currDict}", logFile, LOG)
        htmlNameUnderscorePos = currDict['name'].find("_")
        currTableName = currDict['name'][htmlNamePrefixLen:htmlNameUnderscorePos] # My html field names are set in appGVars.py under searchFields
        currColName = currDict['name'][htmlNameUnderscorePos + 1:999]
        dataColName = currColName
        tablesRelDictKey = f"{currTableName}_{currColName}"
        retrievedColAsName = f"{'x' * htmlResultsNamePrefixLen}{tablesRelDictKey}"
        currKey = currDict['name'][htmlNamePrefixLen:999]

        if not currKey in g.tableRelsDict:
            YMessage(f"{currKey} not in g.tableRelsDict =>{g.tableRelsDict}", logFile, LOG)
            exit()

        else:
            dataTableName = g.tableRelsDict[currKey][g.tableRelsDictJoinNewTNameIdx]

        # currValFrom and To will be used for "WHERE" database commands
        if (dataColName == g.tcols['peopleNamesFmlEngT_lstNameColHead'][0] or \
            dataColName == g.tcols['peopleNamesFmlEngT_fstNameColHead'][0]
           ) and currDict['valFrom'] != "":
            okToAddCommands = True
            currValFrom = currDict['valFrom']
            currValTo = currDict['valTo']

        elif (dataColName == g.tcols['peopleNamesFullEngT_fullNameEngColHead'][0]
             ) and currDict['valFrom'] != "":
            okToAddCommands = True
            currValFrom = currDict['valFrom']
            currValTo = currDict['valTo']

        elif (dataColName == g.tcols['peopleNamesFullBirthDocT_fullNameBirthDocColHead'][0]
             ) and currDict['valFrom'] != "":
            okToAddCommands = True
            currValFrom = currDict['valFrom']
            currValTo = currDict['valTo']

        elif (currTableName == g.t['peopleDobTableName'] and
                (dataColName == g.tcols['peopleDobT_evtTimeYgrColHead'][0] or
                dataColName == g.tcols['peopleDobT_evtTimeMgrColHead'][0] or
                dataColName == g.tcols['peopleDobT_evtTimeDgrColHead'][0]
                )):
            okToAddCommands = False # we are not adding anything to the database query until we have walked through Y M and D

            YMessage(f"dataColName={dataColName}", logOption=LOG)
            if dataColName == g.tcols['peopleDobT_evtTimeYgrColHead'][0]:

                if not (currDict['valFrom'] == 0 or currDict['valFrom'] == ""): # TODO: a problem if the user inputs year 0 as a search term
                    dobYYYYMMDDFrom = dobYYYYMMDDFrom + (int(currDict['valFrom']) + yyyyAdjustmentValueForConsistentNumber) * yyyyyMultiplyFactor

                    if dobYYYYMMDDFrom < 10000 * yyyyyMultiplyFactor:
                        YMessage( "We Have a problem with the year value", logOption=LOG)
                        tabs(-1)

                        return f"We Have a problem with the search year value ({currDict['valFrom']})", 400

                dobYYYYMMDDFromBitsCollected = dobYYYYMMDDFromBitsCollected + 1

                if currDict['valTo'] != "":
                    dobYYYYMMDDTo = dobYYYYMMDDTo + (int(currDict['valTo']) + yyyyAdjustmentValueForConsistentNumber) * yyyyyMultiplyFactor

                dobYYYYMMDDToBitsCollected = dobYYYYMMDDToBitsCollected + 1

            elif dataColName == g.tcols['peopleDobT_evtTimeMgrColHead'][0]:

                if not (currDict['valFrom'] == 0 or currDict['valFrom'] == ""):
                    dobYYYYMMDDFrom = dobYYYYMMDDFrom + int(currDict['valFrom']) * 100

                dobYYYYMMDDFromBitsCollected = dobYYYYMMDDFromBitsCollected + 1

                if currDict['valTo'] != "":
                    dobYYYYMMDDTo = dobYYYYMMDDTo + int(currDict['valTo']) * 100

                dobYYYYMMDDToBitsCollected = dobYYYYMMDDToBitsCollected + 1

            elif dataColName == g.tcols['peopleDobT_evtTimeDgrColHead'][0]:

                if not(currDict['valFrom'] == 0 or currDict['valFrom'] == ""):
                    print("here")
                    dobYYYYMMDDFrom = dobYYYYMMDDFrom + int(currDict['valFrom']) * 1

                dobYYYYMMDDFromBitsCollected = dobYYYYMMDDFromBitsCollected + 1

                if currDict['valTo'] != "":
                    dobYYYYMMDDTo = dobYYYYMMDDTo + int(currDict['valTo']) * 1

                dobYYYYMMDDToBitsCollected = dobYYYYMMDDToBitsCollected + 1

            if dobYYYYMMDDFromBitsCollected == 3:
                currValFrom = dobYYYYMMDDFrom

                if currValFrom != 0:
                    okToAddCommands = True

            if dobYYYYMMDDToBitsCollected == 3:
                currValTo = dobYYYYMMDDTo

                if currValTo != 0:
                    okToAddCommands = True
        # end of Dob

        elif (currTableName == g.t['peopleDodTableName'] and
                (dataColName == g.tcols['peopleDodT_evtTimeYgrColHead'][0] or
                dataColName == g.tcols['peopleDodT_evtTimeMgrColHead'][0] or
                dataColName == g.tcols['peopleDodT_evtTimeDgrColHead'][0]
                )):
            okToAddCommands = False # we are not adding anything to the database query until we have walked through Y M and D

            YMessage(f"dataColName={dataColName}", logOption=LOG)

            if dataColName == g.tcols['peopleDodT_evtTimeYgrColHead'][0]:
                print("here0")
                if not (currDict['valFrom'] == 0 or currDict['valFrom'] == ""): # TODO: a problem if the user inputs year 0 as a search term
                    print("here01")
                    dodYYYYMMDDFrom = dodYYYYMMDDFrom + (int(currDict['valFrom']) + yyyyAdjustmentValueForConsistentNumber) * yyyyyMultiplyFactor

                    if dodYYYYMMDDFrom < 10000 * yyyyyMultiplyFactor:
                        YMessage(f"We Have a problem with the year value ({currDict['valFrom']})", logOption=LOG)
                        tabs(-1)

                        return f"We Have a problem with the search year value ({currDict['valFrom']})", 400

                dodYYYYMMDDFromBitsCollected = dodYYYYMMDDFromBitsCollected + 1

                if currDict['valTo'] != "":
                    dodYYYYMMDDTo = dodYYYYMMDDTo + (int(currDict['valTo']) + yyyyAdjustmentValueForConsistentNumber) * yyyyyMultiplyFactor

                dodYYYYMMDDToBitsCollected = dodYYYYMMDDToBitsCollected + 1

            elif dataColName == g.tcols['peopleDodT_evtTimeMgrColHead'][0]:

                if not (currDict['valFrom'] == 0 or currDict['valFrom'] == ""):
                    dodYYYYMMDDFrom = dodYYYYMMDDFrom + int(currDict['valFrom']) * 100

                dodYYYYMMDDFromBitsCollected = dodYYYYMMDDFromBitsCollected + 1

                if currDict['valTo'] != "":
                    dodYYYYMMDDTo = dodYYYYMMDDTo + int(currDict['valTo']) * 100

                dodYYYYMMDDToBitsCollected = dodYYYYMMDDToBitsCollected + 1

            elif dataColName == g.tcols['peopleDodT_evtTimeDgrColHead'][0]:

                if not(currDict['valFrom'] == 0 or currDict['valFrom'] == ""):
                    print("here")
                    dodYYYYMMDDFrom = dodYYYYMMDDFrom + int(currDict['valFrom']) * 1

                dodYYYYMMDDFromBitsCollected = dodYYYYMMDDFromBitsCollected + 1

                if currDict['valTo'] != "":
                    dodYYYYMMDDTo = dodYYYYMMDDTo + int(currDict['valTo']) * 1

                dodYYYYMMDDToBitsCollected = dodYYYYMMDDToBitsCollected + 1

            if dodYYYYMMDDFromBitsCollected == 3:
                currValFrom = dodYYYYMMDDFrom
                print("here1")
                if currValFrom != 0:
                    print("here2")
                    okToAddCommands = True

            if dodYYYYMMDDToBitsCollected == 3:
                currValTo = dodYYYYMMDDTo

                if currValTo != 0:
                    okToAddCommands = True

        # end of the long dodT elif
        # Also end of currValFrom and To preparation if block

        # step 2
        # if currValFrom and To has been setup,
        # add them to "whereCommandsStr"
        if okToAddCommands:
            okToAddCommands = False
            #whereCommandsStr[sourceTable] = whereCommandsStr.get(sourceTable, '') # provides a default value for the key if it doesn't exist https://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
            #colCommands[sourceTable] = colCommands.get(sourceTable, '') # provides a default value for the key if it doesn't exist https://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary

            if whereCommandsStr != '': # the very first command doesn't get an "AND" at the front
                whereCommandsStr = whereCommandsStr + " AND "

            # this would not be executing if currValFrom evaluated to 0 above because okToAddCommands is false
            if currTableName == g.t['peopleDobTableName'] or currTableName == g.t['peopleDodTableName']: # identical values for DOD and DOB
                # Without the YYYY value adjustment, the logic below would break down for year 0 and has problems if the year is <1000 or negative.
                # It is solved by adding 20000 (assuming) people in the table will not have a year less than -10000 (i.e. 10000BC) - see above

                if str(currValFrom)[-2:] != "00": # all YMD values were used. BTW, not using a colon after the index value turns this into an integer
                    YMessage("ymd", logOption=LOG)
                    colCommands = (f"({"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeYgrColHead'][0]} + "
                                        f" {yyyyAdjustmentValueForConsistentNumber}) * {yyyyyMultiplyFactor} + "
                                 f" {"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeMgrColHead'][0]} * 100 + "
                                    f" {"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeDgrColHead'][0]}"
                                  )
                elif str(currValFrom)[-4:-2] == "00": # only Y was used
                    colCommands = (
                        f"({"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeYgrColHead'][0]} + "
                            f"{yyyyAdjustmentValueForConsistentNumber}) * {yyyyyMultiplyFactor}"
                    )
                elif (99 < currValFrom and currValFrom < 1201) and str(currValFrom)[-2] == "00": # only M was used
                    colCommands = (f"{"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeMgrColHead'][0]} * 100"
                    )
                elif (100 < currValFrom and currValFrom < 1232) and str(currValFrom)[-2] != "00": #  M and D was used
                    colCommands = (f"{"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeMgrColHead'][0]} * 100 + "
                                        f" {"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeDgrColHead'][0]}"
                    )
                elif currValFrom < 32: # only D was used
                    colCommands = (f"{"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeDgrColHead'][0]}"
                    )
                else: # YM was used but not D
                    colCommands = (f"({"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeYgrColHead'][0]} + "
                                   f" {yyyyAdjustmentValueForConsistentNumber}) * {yyyyyMultiplyFactor} + "
                                   f" {"x" * htmlResultsNamePrefixLen}{currTableName}_{g.tcols['peopleDobT_evtTimeMgrColHead'][0]} * 100"
                                   )
                YMessage(f"colCommands={colCommands}", g.logFile, LOG)

            elif currTableName == g.t['peopleNamesFmlEngTableName'] and not g.t['peopleNamesFmlEngTableName'] in optLeftJoinDict:
                colCommands = (f"{g.t['peopleNamesFmlEngTableName']}.{dataColName}"
                )
            else:
                colCommands = retrievedColAsName

            optUpperLeft = "UPPER("
            optUpperRight = ")"
            optPercent = "%"
            optTick = "'"
            if currValTo == "" or currValTo == 0:

                if str(currValFrom).isnumeric():
                    optUpperLeft = "("
                    optPercent = ""
                    optTick = ""

                whereCommandsStr = (whereCommandsStr + f"{optUpperLeft}{colCommands}{optUpperRight} LIKE {optUpperLeft}{optTick}{optPercent}{currValFrom}{optPercent}{optTick}{optUpperRight}")

            else:

                if str(currValFrom).isnumeric() and str(currValTo).isnumeric():
                    optUpperLeft = "("
                    optPercent = ""
                    optTick = ""

                whereCommandsStr = (whereCommandsStr + f"{optUpperLeft}{colCommands}{optUpperRight} BETWEEN {optUpperLeft}{optTick}{currValFrom}{optPercent}{optTick}{optUpperRight} "
                                                        f"AND {optUpperLeft}{optTick}{currValTo}{optPercent}{optTick}{optUpperRight}")
        #
        # End of okToAddCommands if block
    #
    # end of the for loop walking through processedDictListContainer

    # TODO: Just to be safe I should probably check that all columns in all needed tables exist

    #whereCommandsStr = f"{'lstName'} BETWEEN \'{'Beet'}\' AND \'{'Bell'}\'"
    YMessage(f"optLeftJoinDict={optLeftJoinDict}", logFile, LOG)
    YMessage(f"selectColsStr={selectColsStr}", logFile, LOG)
    YMessage(f"optLeftJoinStr={optLeftJoinStr}", logFile, LOG)
    YMessage(f"whereCommandsStr={whereCommandsStr}", logFile, LOG)

    YMessage(f"SELECT {selectColsStr}\nFROM {g.t['peopleNamesFmlEngTableName']}\n{optLeftJoinStr}\n{whereCommandsStr}", logFile, LOG)
    response1 = db.execute(
        f"SELECT {selectColsStr}, {g.t['peopleNamesFmlEngTableName']}.personId AS personId "
        f"FROM {g.t['peopleNamesFmlEngTableName']} " #by default I will always have the names table as "table1" in the join scheme
        f"{optLeftJoinStr} "
        f"{whereCommandsStr} "
    )

    if response1:
        data = response1

    else:
        data = []
    YMessage(f"response= {response1}", logFile, LOG)
    NMessage(f"data= {data}", logFile, LOG)
    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)

    return data, chosenColsHeads, 0


def GetIdOfValueInTable(db, tableName, colName, valueToFind):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    id = 0

    #check table exists
    if not IsTableExists(db, tableName):
        YMessage(f"IsTableExists(db, tableName={tableName}) returned False", logFile, ERRORLOG)
        exit()

    #check if value in table, and if so return id
    response = db.execute(
        f"SELECT id "
        f"FROM {tableName} "
        f"WHERE {colName} = \'{valueToFind}\' "
    )
    YMessage(f"response={response}", logFile, LOG)

    if not response:
        YMessage(f"didn't find {valueToFind}", logFile, LOG)

    else:
        id = response[0]['id']

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return id


def GetIdOfValuesInTable(db, tableName, valuesDict): # All values in valuesDict must match
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, valuesDict={valuesDict}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    #check table exists
    if not IsTableExists(db, tableName):
        YMessage(f"IsTableExists(db, tableName={tableName}) returned False", logFile, ERRORLOG)
        exit()

    id = 0
    keys = []
    vals = []
    response = "asdf"
    c = 0
    for key in valuesDict:
        YMessage(f"key={key} valueDict[key]={valuesDict[key]}", logFile, LOG)

        if not IsColumnExistsInTable(db, tableName, key):
            YMessage(f"tableName={tableName} doesn't have column {key}", logFile, ERRORLOG)
            exit()

        keys.append(key)
        vals.append(str(valuesDict[key]).replace("'","%27").replace('"',"%22"))
        c = c + 1

    YMessage(f"Using {c} values to get the id from {tableName}. keys={keys} vals={vals}", logFile, LOG)
    # NB!!!! keys must not be in the single quotes
    if 1 == c:
        response = db.execute(
            f"SELECT id FROM {tableName} "
            f"WHERE {keys[0]} = \'{vals[0]}\' "
        )
    elif 2 == c:
        response = db.execute(
            f"SELECT id FROM {tableName} "
            f"WHERE {keys[0]} = \'{vals[0]}\' and {keys[1]} = \'{vals[1]}\' "
        )
    elif 3 == c:
        response = db.execute(
            f"SELECT id FROM {tableName} "
            f"WHERE {keys[0]} = \'{vals[0]}\' and {keys[1]} = \'{vals[1]}\' and {keys[2]} = \'{vals[2]}\'"
        )
    elif 4 == c:
        response = db.execute(
            f"SELECT id FROM {tableName} "
            f"WHERE {keys[0]} = \'{vals[0]}\' and {keys[1]} = \'{vals[1]}\' and {keys[2]} = \'{vals[2]}\' and {keys[3]} = \'{vals[3]}\' "
        )
    elif 5 == c:
        response = db.execute(
            f"SELECT id FROM {tableName} "
            f"WHERE {keys[0]} = \'{vals[0]}\' and {keys[1]} = \'{vals[1]}\' and {keys[2]} = \'{vals[2]}\' and {keys[3]} = \'{vals[3]}\' and {keys[4]} = \'{vals[4]}\' "
        )
    elif 6 == c:
        response = db.execute(
            f"SELECT id FROM {tableName} "
            f"WHERE {keys[0]} = \'{vals[0]}\' and {keys[1]} = \'{vals[1]}\' and {keys[2]} = \'{vals[2]}\' and {keys[3]} = \'{vals[3]}\' and {keys[4]} = \'{vals[4]}\' and {keys[5]} = \'{vals[5]}\' "
        )
    else:
        YMessage(f"Error: the number of values in valuesDict is {c}", logFile, ERRORLOG)
        exit()

    YMessage(f"response={response}", logFile, LOG)

    if not response:
        YMessage(f"didn't find {valuesDict}", logFile, LOG)

    else:
        id = response[0]['id']

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return id


def GetListOfValuesFromTableColumn(db, tableName, colName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    response = db.execute(
        f"SELECT {colName} "
        f"FROM {tableName} "
    )

    YMessage(f"response={response}", logOption=LOG)
    if not response: # something went wrong
        YMessage(f"For some reason we did not get a response from db.execute. Quitting", logOption=ERRORLOG)
        exit()

    if type(response) is not list:
        YMessage(f"For some reason we did not get a list in the response from db.execute.\nresponse={response}\nQuitting", logOption=ERRORLOG)
        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return response


def GetUniqueTableColPairsDictList(tableCols): #TODO
    tabs(1)
    f = inspect.stack()[0][3] + f"(tableCols={tableCols}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    dictList = []

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return dictList


def GetUrlMainSuffixPartFromUrl(listOfRootDicts, listOfSuffixDicts, value):
    tabs(1)
    f = inspect.stack()[0][3] + f"(listOfRootDicts={listOfRootDicts}, listOfSuffixDicts={listOfSuffixDicts}, value={value}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    # Now check if there is a "root" in value
    urlRootFound = False

    urlMainVal = ""
    urlSuffixVal = ""

    rootCtr = 0
    for rootDict in listOfRootDicts:

        YMessage(f"Checking if {rootDict[g.tcols['urlRootsT_urlRootColHead'][0]]} is in {value}", logFile, LOG)
        root = rootDict[g.tcols['urlRootsT_urlRootColHead'][0]]

        if root in value:
            urlRootFound = True
            break

    if urlRootFound:
        urlMainVal = value[len(root):9999]
        YMessage(f"urlMainVal={urlMainVal}", logOption=LOG)

    else:
        urlMainVal = value

    # Now check if there is a "suffix" in valueWithoutRoot
    urlSuffixFound = False

    for suffixDict in listOfSuffixDicts:
        YMessage(f"Checking if {suffixDict[g.tcols['urlSuffixesT_urlSuffixColHead'][0]]} is in {urlMainVal}", logFile, LOG)
        suffix = suffixDict[g.tcols['urlSuffixesT_urlSuffixColHead'][0]]

        if suffix in value:
            urlSuffixFound = True
            break

    if urlSuffixFound:
        urlMainVal = urlMainVal[0:urlMainVal.find(suffix)]
        urlSuffixVal = value[value.find(suffix)+len(suffix):999]
        YMessage(f"urlMainVal={urlMainVal} urlSuffixVal={urlSuffixVal}", logFile, LOG)

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return urlMainVal, urlSuffixVal


def GetValueFromTableColumn(db, tableName, colName, valuesDict):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}, valuesDict={valuesDict}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = ""

    if not IsTableExists(db, tableName):
        YMessage(f"{tableName} not exist", logFile, LOG)
        exit()

    if not IsColumnExistsInTable(db, tableName, colName):
        YMessage(f"{colName} not exist", logFile, LOG)
        exit()

    columnCreationCommands = ""
    firstCommandSet = False
    for key in valuesDict: # Will walk through our many column names and create commands for db.execute

        if firstCommandSet:
            columnCreationCommands = columnCreationCommands + ' and ' + f"{key} = '{valuesDict[key]}'"

        else:
            columnCreationCommands = columnCreationCommands + f"{key} = '{valuesDict[key]}'"
            firstCommandSet = True

    YMessage(f"columnCreationCommands= {columnCreationCommands}", logFile, LOG)

    response = db.execute(
        f"SELECT {colName} FROM {tableName} "
        f"WHERE {columnCreationCommands}"
    )
    YMessage(f"response= {response}", logFile, LOG)
    if response:
        returnVal = response[0][colName]

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnVal


def GetValueIdInRefsTable(db, refsTableName, value, wikiPageNameOrLike=True):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, refsTableName={refsTableName}, value={value}, wikiPageNameOrLike={wikiPageNameOrLike}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
        # Refs table can store a more compact version of the reference by splitting
        # it between urlRoot and urlMain (with optional suffix)
        # So, need extra logic as compared to IsValueInTable()
        # the assumption is we are dealing with the standard g.refsTableName table

    if not IsTableExists(db, g.t['refsTableName']):
        CreateDbTableIfNotExist(db, g.t['refsTableName'])
        refTableId = 0
        urlRootId = 0
        urlMainVal = ""
        urlSuffixId = 0
        urlSuffixVal = ""
        # table didn't even exist, so of course the record didn't exist
        # just quit with the current return values

    elif "http" in value: # dealing with a url address, which might or might not have a root that exists in urlRoots table
        urlRootId, urlMainVal, urlSuffixId, urlSuffixVal = SplitUrlIntoParts(db, value)
            # SplitUrlIntoParts actually checks every part of the url (value) and retrieves every single one from the respective
            # tables.

        refTableId = 0
        urlMainVal = str(urlMainVal).replace("'","%27").replace('"',"%22")
        urlSuffixVal = str(urlSuffixVal).replace("'","%27").replace('"',"%22")

        YMessage(f"urlRootId={urlRootId}, urlMainVal={urlMainVal}, urlSuffixId={urlSuffixId}, urlSuffixVal={urlSuffixVal}", logFile, LOG)

        # Now we can finally check for this reference's presence in the ref table
        response = db.execute(
            f" SELECT id "
            f" FROM {g.t['refsTableName']} "
            f" WHERE {g.tcols['refsT_urlRootIdColHead'][0]} = ? AND "
                f" {g.tcols['refsT_urlMainColHead'][0]} = ? AND "
                f" {g.tcols['refsT_urlSuffixIdColHead'][0]} = ? AND "
                f" {g.tcols['refsT_urlSuffixValColHead'][0]} = ?"
            , urlRootId, urlMainVal, urlSuffixId, urlSuffixVal
        )
        YMessage(f"After trying to locate {urlMainVal} in {g.t['refsTableName']} response={response}", logFile, LOG)

        if response:
            refTableId = response[0]['id']

        #else the reference has not yet been entered into the table

    else: # seems like we are not dealing with a non-standard url
        # throw a message for now
        YMessage(f"value={value}. Don't know how to handle yet. Quitting.", logFile, ERRORLOG)

        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)

    return refTableId, urlRootId, urlMainVal, urlSuffixId, urlSuffixVal


def InsertUniqueValuesToTable(db, tableName, colName, sourcePandaDf, sourceType="CSV", sourceFilePath="Provide a file path"):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}, sourcePandaDf={str(type(sourcePandaDf))}, sourceType={sourceType}, sourceFilePath={sourceFilePath}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    NMessage(f"sourcePandaDf={sourcePandaDf}")
    sourcePandaDf = sourcePandaDf.reset_index()
    c = 0
    YMessage(f"Walking through sourcePandaDf", logFile, LOG)
    for index, row in sourcePandaDf.iterrows(): # going through every row of the read in CSV file
        c = c + 1
        YMessage(f"row{c}={row}", logFile, LOG)
        YMessage(f"row[colName]={row[colName]}", logFile, LOG)
        if row[colName]:
            currTableName = tableName
            PopulateDB(g.db, currTableName, row, source="CSV")

        else:
            YMessage(f"One of the values in {sourceFilePath} is blank: {c}->{row}. Not entering this record into the database.", logFile=logFile, logOption=ERRORLOG)
            continue


def InsertDbDataFromHtml(db, insertTheseRows, parsedSearchResults, htmlResultsNamePrefixLen, user):
    tabs(1)
    f = inspect.stack()[0][3] + f"(insertTheseRows={insertTheseRows}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
    NMessage(f"g.editorsList={g.editorsList} user={user}", logFile, LOG)
    # g.numRecordsInserted = 0 # actually, we will only reset this value in app.py (updatePeople route)
    # g.recordsInsertedMessage = ""ditto
    g.recordsInsertedDetails = ""
    message = ""
    error = 0
    optLeftJoinCmd = ""

    if not user in g.editorsList:
        error = 403
        message = "You currently don't have the privileges to update the data in the database. Contact administrator."

    else:
        for row in insertTheseRows:
            YMessage(f"inserting data in this row: {row}", logFile, LOG)
            currTableName = row['tableName']
            colName = row['colName']
            mainTableIdColName = "personId" # later, perhaps, i'll have a programmatic way to set this
            mainTableIdColValue = row[mainTableIdColName]
            # depending on what tableName_colName combination is, the relating id column name will be different (personId, placesId, occupationId etc)
            relatedIdColName = g.tableRelsDict[f"{currTableName}_{colName}"][g.tableRelsDictSharedIdsColNameIdx]
            dataTableName =  g.tableRelsDict[f"{currTableName}_{colName}"][g.tableRelsDictDataTNameIdx]
            optLeftJoinCmd = ""
            newVal = row['newVal']

            YMessage(f"currTableName={currTableName} sourceTableName={currTableName}", logFile, LOG)
            YMessage(f"dataTableName={dataTableName} colName={colName} personId={mainTableIdColValue} newVal={newVal}", logFile, LOG)


            if dataTableName != currTableName: # complicated situation I'll need to fix
                #optLeftJoinCmd = f"LEFT JOIN {dataTableName} ON {currTableName}.{relatedIdColName} = {dataTableName}.{relatedIdColName} "
                tabs(-1)
                message = f"Sorry you are trying to insert data - {newVal} - that lives in a 'subtatble' ({dataTableName}) and I don't yet have the algorithm for processing such cases."
                error = 500
                return message, error

            # First check to if this record is in the table
            # (eg. dataTableName = 'peopleDobT' mainTableIdColName = "personId" and mainTableIdColValue = '619'
            # expected result if row with personId=='619' exists in this table would be [{ 'personId': '619' }]
            # Otherwise blank
            response = db.execute(
                f"SELECT {mainTableIdColName} FROM {dataTableName} "
                f"{optLeftJoinCmd}" # for now blank
                f"WHERE {mainTableIdColName} = \'{mainTableIdColValue}\'"
            )
            YMessage(f"response from checking if {mainTableIdColName}={mainTableIdColValue} is in table {dataTableName} returned {response}", logFile, LOG)

            if response: # we must update this record instead!
                UpdateDbDataFromHtml(db, [row], parsedSearchResults, htmlResultsNamePrefixLen, user) # we call this function and then skip the rest of this loop
                continue

            # We know that this record needs to be inserted into the dataTableName table
            # besides adding the new value we must also add some required NOT NULL column values
            otherRequiredColNamesCmd = f", addedByUsername, refId, {mainTableIdColName}" # mainTableIdColName could be personId, or placeId, or occupationId etc
            useThisColNameCmd = f", useThis"

            if 'personId' in row: # "magic values" ALERT - see mainTableIdColName above
                mainTable = g.t['peopleTableName'] # dealing with peopleT main table which has a refId that points to the reference we are going to use for now
                                                    # TODO: this must be fixed in the future when people start adding new references

            else:
                tabs(-1)
                message = f"Sorry I don't yet have the algorithm for processing such cases ({insertTheseRows})."
                error = 500
                return message, error

            YMessage(f"mainTable={mainTable} mainTableIdColName={mainTableIdColName} mainTableIdColValue=\'{mainTableIdColValue}\'", logFile, LOG)

            # try to get the refId value from the mainTable
            response = db.execute(
                f" SELECT refId FROM {mainTable} "
                f" WHERE id = \'{mainTableIdColValue}\' "
            )

            if not response:
                message = f"somehow this {mainTableIdColName} ({mainTableIdColValue}) doesn't exist"
                error = 500
                tabs(-1)
                return message, error

            YMessage(f"response={response}", logFile, LOG)
            refId = response[0]['refId']
            otherRequiredColValuesCmd = f", \'{user}\', \'{refId}\', \'{mainTableIdColValue}\'"
            useThisColValueCmd = f", '1'"
            # we should be ok to insert a new row into this table
            response = db.execute( # response should return the id of the newly inserted row
                f" INSERT INTO {dataTableName} ({colName}{otherRequiredColNamesCmd}{useThisColNameCmd}) "
                f" VALUES (\'{newVal}\'{otherRequiredColValuesCmd}{useThisColValueCmd}) "
            )
            SetDictListValue(parsedSearchResults,
                             mainTableIdColName,
                             mainTableIdColValue,
                             "x" * htmlResultsNamePrefixLen + row['tableName'] + "_" + colName,
                             newVal, logFile=logFile, logOption=LOG)
            g.recordsInsertedDetails = g.recordsInsertedDetails + f" {dataTableName}.{colName}={newVal} "
            YMessage(f"response from updating {dataTableName} with {colName} = \'{newVal}\' WHERE {mainTableIdColName} = \'{mainTableIdColValue}\' returned {response}", logFile, LOG)

            if not response:
                tabs(-1)
                message = f"There was a problem and the data you were trying to insert - {newVal} - failed to be written to the database and I don't know why."
                error = 500
                return message, error

            g.numRecordsInserted = g.numRecordsInserted + 1

        g.recordsInsertedMessage = f"{g.numRecordsInserted} record{'s' if g.numRecordsInserted > 1 else ''} inserted. [{g.recordsInsertedDetails}]"

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return message, error


def InsertValueIntoTable(db, tableName, colName, value):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}, value={str(value)}, id={id}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    if id < 0:
        response = db.execute(
            "INSERT INTO ? (?) \
            VALUES (?) \
            ",
            tableName, colName, value
            )

    if not response:
        YMessage(f"Something went wrong and '{tableName}' table wasn't updated with this insertion {colName}:{value}", logFile, LOG)
        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return response


def InsertValuesIntoTable(db, tableName, valuesDict): # the expectation is that table already has all the necessary columns which valueDict has to match.
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, valuesDict={valuesDict}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    id = 0
    keys = []
    vals = []
    response = "asdf"
    c = 0

    if not IsTableExists(db, tableName):
        response = CreateDbTableIfNotExist(db, tableName)
        YMessage(f"from CreateDbTableIfNotExist(db, {tableName}) the response={response}", logFile, LOG)
        if not response:
            YMessage(f"table {tableName} was not created", logFile, ERRORLOG)
            exit()

    for key in valuesDict:
        YMessage(f"key={key} valueDict[key]={valuesDict[key]}", logFile, LOG)

        if not IsColumnExistsInTable(db, tableName, key):
            YMessage(f"tableName={tableName} doesn't have column {key}", logFile, ERRORLOG)
            exit()

        if IsColTypeUnique(db, tableName, key):
            YMessage(f"IsColTypeUnique(db, {tableName}, {key}) returned true", logFile, ERRORLOG)

            if IsValueInTable(db, tableName, key, valuesDict[key]):
                YMessage(f"tableName={tableName} already has {valuesDict[key]} in column {key}", logFile, ERRORLOG)
                YMessage(f"ENDED {f}", logFile, LOG)
                tabs(-1)
                return id
                # This means that we do not try to add it to the table


        keys.append(key)
        vals.append(str(valuesDict[key]).replace("'","%27").replace('"',"%22"))
        c = c + 1
        #id = InsertValueIntoTable(db, tableName, key, valuesDict[key])
        # Because a number of columns have a NOT NULL constraint, I have to insert all values in one call
        # Thus I count how many values there are to add

    YMessage(f"about to try to insert these {c} values into {tableName}: keys:{keys}  vals:{vals}", logFile, LOG)

    # Well, I couldn't figure out if there is a more efficient way to code the below...
    if 1 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\') "
            f"VALUES                      (\'{vals[0]}\') "
        )
    elif 2 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\') "
        )
    elif 3 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\') "
        )
    elif 4 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\') "
        )
    elif 5 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\') "
        )
    elif 6 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\') "
        )
    elif 7 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\') "
        )
    elif 8 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\') "
        )
    elif 9 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\') "
        )
    elif 10 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\') "
        )
    elif 11 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\') "
        )
    elif 12 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\', \'{keys[11]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\', \'{vals[11]}\') "
        )
    elif 13 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\', \'{keys[11]}\', \'{keys[12]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\', \'{vals[11]}\', \'{vals[12]}\') "
        )
    elif 14 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\', \'{keys[11]}\', \'{keys[12]}\', \'{keys[13]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\', \'{vals[11]}\', \'{vals[12]}\', \'{vals[13]}\') "
        )
    elif 15 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\', \'{keys[11]}\', \'{keys[12]}\', \'{keys[13]}\', \'{keys[14]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\', \'{vals[11]}\', \'{vals[12]}\', \'{vals[13]}\', \'{vals[14]}\') "
        )
    elif 16 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\', \'{keys[11]}\', \'{keys[12]}\', \'{keys[13]}\', \'{keys[14]}\', \'{keys[15]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\', \'{vals[11]}\', \'{vals[12]}\', \'{vals[13]}\', \'{vals[14]}\', \'{vals[15]}\') "
        )
    elif 17 == c:
        response = db.execute(
            f"INSERT INTO \'{tableName}\' (\'{keys[0]}\', \'{keys[1]}\', \'{keys[2]}\', \'{keys[3]}\', \'{keys[4]}\', \'{keys[5]}\', \'{keys[6]}\', \'{keys[7]}\', \'{keys[8]}\', \'{keys[9]}\', \'{keys[10]}\', \'{keys[11]}\', \'{keys[12]}\', \'{keys[13]}\', \'{keys[14]}\', \'{keys[15]}\', \'{keys[16]}\') "
            f"VALUES                      (\'{vals[0]}\', \'{vals[1]}\', \'{vals[2]}\', \'{vals[3]}\', \'{vals[4]}\', \'{vals[5]}\', \'{vals[6]}\', \'{vals[7]}\', \'{vals[8]}\', \'{vals[9]}\', \'{vals[10]}\', \'{vals[11]}\', \'{vals[12]}\', \'{vals[13]}\', \'{vals[14]}\', \'{vals[15]}\', \'{vals[16]}\') "
        )
    else:
        YMessage(f"number of values to add to '{tableName}' table is {c}. Quitting", logFile, ERRORLOG)
        exit()

    '''
    response = db.execute(
        f"INSERT INTO ? (?, ?, ?, ?, ?, ?) "
        f"VALUES (?, ?, ?, ?, ?, ?) "
        , tableName, keys[0], keys[1], keys[2], keys[3], keys[4], keys[5], values[0], values[1], values[2], values[3], values[4], values[5]
    )
    '''
    if not response:
        YMessage(f"Something went wrong and '{tableName}' table wasn't updated", logFile, LOG)
        exit()

    YMessage(f"response={response}", logFile, LOG)
    id = response

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return id


def IsColumnExistsInTable(db, tableName, colName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = False

    colCheckDbExecuteCall = f"SELECT COUNT(*) AS CNTREC FROM pragma_table_info('{tableName}') WHERE name='{colName}'"
    response = db.execute( colCheckDbExecuteCall )
    YMessage(f"response = {response}", logFile, LOG)

    if response:

        if response[0]['CNTREC'] == 0: # it means that this column doesn't exist and needs to be added first
            returnVal = False

        else:
            returnVal = True

    else:
        YMessage(f"Got no response from db.execute", logFile, ERRORLOG)


    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnVal


def IsColTypeUnique(db, tableName, colName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = False

    response = db.execute(
        #f"PRAGMA table_info(\'{tableName}\')"
        f"SELECT * FROM sqlite_master"
    )
    NMessage(f"SELECT * FROM sqlite_master returned {response}", logFile, LOG)
    # Now need to retrieve the needed value
    if not response:
        YMessage(f"SELECT * FROM sqlite_master returned nothing {response}", logFile, ERRORLOG)
        exit()

    for tableInfoDict in response:
        if tableName == tableInfoDict['tbl_name']:
            #extract string from 'sql' key between colName and comma
            colsTypesString = str(tableInfoDict['sql'])[tableInfoDict['sql'].find(colName):10000]
            colTypeString = colsTypesString[0:colsTypesString.find(",")]
            YMessage(f"colTypeString={colTypeString}", logFile, LOG)
            if "UNIQUE" in colTypeString.upper():
                returnVal = True
            break

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnVal


def IsTableExists(db, tableName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = False

    response = db.execute(
        f"SELECT name "
        f"FROM sqlite_master "
        f"WHERE type='table' AND name='{tableName}'" # this way works, with ? doesn't
    )
    YMessage(f"response={response}", logOption=LOG)
    if not response:
        returnVal = False

    elif response[0]['name'] == tableName:
        returnVal = True

    else:
        YMessage(f"don't know what to do with this response={response}", logOption=ERRORLOG)
        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnVal


def IsValueInTable(db, tableName, colName, valueToCheck):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}, valueToCheck={valueToCheck}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    response = db.execute( #we will first check the database for an existing entry to avoid duplicating
        f"SELECT {colName} "
        f"FROM ? "
        f"WHERE {colName} = ? " # seems that it requires that I specify dictvalue as ? followed by a list of variables below
        , tableName, valueToCheck
    )

    if response:
        YMessage(f"response={response}. This reference already exists in the table. Skipping.", logFile, LOG)
        YMessage(f"ENDED {f}", logFile, LOG)
        tabs(-1)
        return True

    else:
        YMessage(f"ENDED {f}", logFile, LOG)
        tabs(-1)
        return False


def OptLeftJoinProcessing(leftJoinDict, option, leftJoinTableAsName, dataTableName, leftJoinAlreadyTableName, optLeftJoinDictCurrRelColName,
                                              optLeftJoinDictCurrRelColNameNewTable, useThisColName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(leftJoinDict={leftJoinDict}, ...):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
    # option could be "dob or dod",

    if "dob or dod" == option:

        # the if statement below takes care of the situations where selecting a column like
        # DOBplaceOfBirth but not also selecting a table involving peopleDobT forces peopleDobT to be LEFT JOIN'ed first
        if ( leftJoinAlreadyTableName == g.t['peopleDobTableName'] or \
                leftJoinAlreadyTableName == g.t['peopleDodTableName'] ) and \
                        not leftJoinDict[leftJoinAlreadyTableName]:
            # TODO: eventually implement some kind of a recursive function for difficult dependencies

            # SetOptLeftJoinDictKeyVal(optLeftJoinDict, keyToSet, leftJoinTableName,
            #                               leftJoinTableAsName, preexistingTableAsName, commonColName, commonColNameNewTAble, useThisColName):
            YMessage(f"2)leftJoinDict=={leftJoinDict}", logFile, LOG)
            SetOptLeftJoinDictKeyVal(leftJoinDict, \
                                        g.tableRelsDict[leftJoinAlreadyTableName + "_" + \
                                                        g.tcols['peopleDobT_evtTimeYgrColHead'][0]][g.tableRelsDictTableAsNameIdx], \
                                        leftJoinAlreadyTableName, \
                                        g.tableRelsDict[leftJoinAlreadyTableName + "_" + \
                                                        g.tcols['peopleDobT_evtTimeYgrColHead'][0]][g.tableRelsDictTableAsNameIdx], \
                                        g.t['peopleNamesFmlEngTableName'], \
                                        g.tcols['peopleNamesFmlEngT_personIdColHead'][0],
                                        g.tcols['peopleNamesFmlEngT_personIdColHead'][0],
                                        useThisColName)

        YMessage(f"3)optLeftJoinDict=={leftJoinDict}", logFile, LOG)
        SetOptLeftJoinDictKeyVal(leftJoinDict,
                                    leftJoinTableAsName,
                                    dataTableName,
                                    leftJoinTableAsName,
                                    leftJoinAlreadyTableName,
                                    optLeftJoinDictCurrRelColName,
                                    optLeftJoinDictCurrRelColName,
                                    useThisColName)
    elif "refs" == option:
        '''currTableName = dict['name'][htmlNamePrefixLen:htmlNameUnderscorePos] # My html field names are set in appGVars.py under searchFields
            currColName = dict['name'][htmlNameUnderscorePos + 1:999]
            tablesRelDictKey = f"{currTableName}_{currColName}"
            dataTableName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictJoinNewTNameIdx] 2

            leftJoinAlreadyTableName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictAlreadyJoinedTNameIdx] 0
            leftJoinTableAsName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictTableAsNameIdx]  4
            optLeftJoinDictCurrRelColName = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictSharedIdsColNameIdx] 1
            optLeftJoinDictCurrRelColNameNewTable = g.tableRelsDict[tablesRelDictKey][g.tableRelsDictSharedIdsColNameNewTableIdx] 5 #optional, usually blank, because same col name into two tables when LEFT JOIN
            '''

        if dataTableName != g.t['refsTableName']:
            YMessage(f"Trouble: expected dataTableName=={g.t['refsTableName']} but got {dataTableName} instead", logFile, LOG)
            exit()

        if leftJoinAlreadyTableName != g.t['peopleNamesFmlEngTableName']:
            YMessage(f"Trouble: expected leftJoinAlreadyTableName=={g.t['peopleNamesFmlEngTableName']} but got {leftJoinAlreadyTableName} instead", logFile, LOG)
            exit()

        if optLeftJoinDictCurrRelColName != "refId":
            YMessage(f"Trouble: expected optLeftJoinDictCurrRelColName=='id' but got {optLeftJoinDictCurrRelColName} instead", logFile, LOG)
            exit()

        if optLeftJoinDictCurrRelColNameNewTable != "id":
            YMessage(f"Trouble: expected optLeftJoinDictCurrRelColName=='id' but got {optLeftJoinDictCurrRelColName} instead", logFile, LOG)
            exit()
        # SetOptLeftJoinDictKeyVal(optLeftJoinDict, keyToSet, leftJoinTableName,
            #                               leftJoinTableAsName, preexistingTableAsName, commonColName, commonColNameNewTAble, useThisColName):
        # first refsT join
        SetOptLeftJoinDictKeyVal(leftJoinDict, # either opt or all dicts
                                leftJoinTableAsName, # this key has to be the $ sign concatenated table "as" name
                                dataTableName, # in this case it should first be "refsT"
                                leftJoinTableAsName, # this is the same as the second argument - TODO: I think I should remove this extra argument ??
                                leftJoinAlreadyTableName,
                                optLeftJoinDictCurrRelColName,
                                optLeftJoinDictCurrRelColNameNewTable,
                                useThisColName)
        # then urlRootsT
        SetOptLeftJoinDictKeyVal(leftJoinDict, # either opt or all dicts
                                f"{leftJoinAlreadyTableName}${dataTableName}${g.t['urlRootsTableName']}", # this key has to be the $ sign concatenated table "as" name
                                g.t['urlRootsTableName'], # in this case it should first be "refsT"
                                f"{leftJoinAlreadyTableName}${dataTableName}${g.t['urlRootsTableName']}", # this is the same as the second argument - TODO: I think I should remove this extra argument ??
                                f"{leftJoinTableAsName}",
                                g.tcols['refsT_urlRootIdColHead'][0],
                                optLeftJoinDictCurrRelColNameNewTable,
                                useThisColName)
        # finally urlSuffixesT
        SetOptLeftJoinDictKeyVal(leftJoinDict, # either opt or all dicts
                                f"{leftJoinAlreadyTableName}${dataTableName}${g.t['urlSuffixesTableName']}", # this key has to be the $ sign concatenated table "as" name
                                g.t['urlSuffixesTableName'], # in this case it should first be "refsT"
                                f"{leftJoinAlreadyTableName}${dataTableName}${g.t['urlSuffixesTableName']}", # this is the same as the second argument - TODO: I think I should remove this extra argument ??
                                f"{leftJoinTableAsName}",
                                g.tcols['refsT_urlSuffixIdColHead'][0],
                                optLeftJoinDictCurrRelColNameNewTable,
                                useThisColName)


    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return False


def ParseSearchResults(searchResults, chosenCols):
    tabs(1)
    f = inspect.stack()[0][3] + f"(searchResults={str(searchResults)}, chosenCols={chosenCols}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    parsedResults = [] # this empty list will have dictionaries that contain column names as keys and key values for what does in each row

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return parsedResults


def PopulateDB(db, tableName, pandasdfvalue, source="HTML"):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, dictvalue={str(pandasdfvalue)}, source={source}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    if g.t['urlRootsTableName'] == tableName:

        if not pandasdfvalue[g.tcols['urlRootsT_urlRootColHead'][0]]:
            YMessage(f"Strangely value for {g.tcols['urlRootsT_urlRootColHead'][0]} key for '{tableName}' is missing, quitting", logFile, LOG)
            exit()

    if g.t['urlSuffixesTableName'] == tableName:

        if not pandasdfvalue[g.tcols['urlSuffixesT_urlSuffixColHead'][0]]:
            YMessage(f"Strangely value for {g.tcols['urlSuffixesT_urlSuffixColHead'][0]} key for '{tableName}' is missing, quitting", logFile, LOG)
            exit()

    if g.t['peopleTableName'] == tableName: # This one is complicated and involves the creation of many other related tables

        if not pandasdfvalue[g.ucols['csvRefStringColHead'][0]]:
            YMessage(f"Strangely, a value for the {g.ucols['csvRefStringColHead'][0]} key for the '{tableName}' table is missing, quitting", logFile, LOG)
            exit()

    CreateDbTableIfNotExist(db, tableName)
    SetValuesInTable(db, tableName, pandasdfvalue, username=g.serverSideUser)

    #Begin by creating the references table

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return


def PrepareRefForRefTable(db, refString):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, refString={refString}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    urlRootId, urlMainVal, urlSuffixId, urlSuffixVal = SplitUrlIntoParts(db, refString)
    YMessage(f"urlRootId={urlRootId}, urlMainVal={urlMainVal}, urlSuffixId={urlSuffixId}, urlSuffixVal={urlSuffixVal}", logFile, LOG)

    urlMainVal = str(urlMainVal).replace("'","%27").replace('"',"%22")
    urlSuffixVal = str(urlSuffixVal).replace("'","%27").replace('"',"%22")

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return urlRootId, urlMainVal, urlSuffixId, urlSuffixVal


def ProcessCmdLineArgs(args):

    if "colsonly" == args[1]:

        if 2 != len(args) - 1:
            YMessage(f"You must provide one more argument specifying the table name to which you want to add all the missing columns as specified in gVars", logOption=True)
            exit()

        CreateMissingColumns(g.db, args[2])
        exit()

    elif "copyonly" == args[1]:

        if 3 != len(args) - 1:
            YMessage(f"You must provide two more arguments, specifying source and target table names", logOption=True)
            exit()

        CopyDbTableToAnotherTable(g.db, args[2], args[3], g.tableCopyMap)
        exit()

    elif "createonly" == args[1]:
        exit()

    elif "test1" == args[1]:
        response = g.db.execute(
            f" SELECT peopleNamesFmlEngT.lstName AS xxxxpeopleNamesFmlEngT_lstName, peopleNamesFmlEngT.fstName AS xxxxpeopleNamesFmlEngT_fstName, peopleNamesFmlEngT$refsT$urlRootsT.urlRoot || peopleNamesFmlEngT$refsT.urlMain || peopleNamesFmlEngT$refsT$urlSuffixesT.urlSuffix || peopleNamesFmlEngT$refsT.urlSuffixVal AS xxxxpeopleNamesFmlEngT_url, peopleNamesFullEngT.fullNameEng AS xxxxpeopleNamesFullEngT_fullNameEng, peopleNamesFullBirthDocT.fullNameBirthDoc AS xxxxpeopleNamesFullBirthDocT_fullNameBirthDoc, peopleGendersT.assignedGenderVal AS xxxxpeopleGendersT_assignedGenderVal, peopleDobT.dobFlag AS xxxxpeopleDobT_dobFlag, peopleDobT.evtTimeYgr AS xxxxpeopleDobT_evtTimeYgr, peopleDobT.evtTimeMgr AS xxxxpeopleDobT_evtTimeMgr, peopleDobT.evtTimeDgr AS xxxxpeopleDobT_evtTimeDgr, peopleDobT$placesNamesEngT.placeNameEng AS xxxxpeopleDobT_placeNameEng, peopleDodT.evtTimeYgr AS xxxxpeopleDodT_evtTimeYgr, peopleDodT.evtTimeMgr AS xxxxpeopleDodT_evtTimeMgr, peopleDodT.evtTimeDgr AS xxxxpeopleDodT_evtTimeDgr, peopleDodT$placesNamesEngT.placeNameEng AS xxxxpeopleDodT_placeNameEng "
            f" FROM peopleNamesFmlEngT "
            f" LEFT JOIN refsT AS peopleNamesFmlEngT$refsT ON peopleNamesFmlEngT.refId = peopleNamesFmlEngT$refsT.id "
            f" LEFT JOIN urlRootsT AS peopleNamesFmlEngT$refsT$urlRootsT ON peopleNamesFmlEngT$refsT.urlRootId = peopleNamesFmlEngT$refsT$urlRootsT.id "
            f" LEFT JOIN urlSuffixesT AS peopleNamesFmlEngT$refsT$urlSuffixesT ON peopleNamesFmlEngT$refsT.urlSuffixId = peopleNamesFmlEngT$refsT$urlSuffixesT.id "
            f" LEFT JOIN peopleNamesFullEngT AS peopleNamesFullEngT ON peopleNamesFmlEngT.personId = peopleNamesFullEngT.personId  AND peopleNamesFullEngT.useThis = 1 "
            f" LEFT JOIN peopleNamesFullBirthDocT AS peopleNamesFullBirthDocT ON peopleNamesFmlEngT.personId = peopleNamesFullBirthDocT.personId  AND peopleNamesFullBirthDocT.useThis = 1 "
            f" LEFT JOIN peopleGendersT AS peopleGendersT ON peopleNamesFmlEngT.personId = peopleGendersT.personId  AND peopleGendersT.useThis = 1 "
            f" LEFT JOIN peopleDobT AS peopleDobT ON peopleNamesFmlEngT.personId = peopleDobT.personId  AND peopleDobT.useThis = 1 "
            f" LEFT JOIN placesNamesEngT AS peopleDobT$placesNamesEngT ON peopleDobT.placeId = peopleDobT$placesNamesEngT.placeId  AND peopleDobT$placesNamesEngT.useThis = 1 "
            f" LEFT JOIN peopleDodT AS peopleDodT ON peopleNamesFmlEngT.personId = peopleDodT.personId  AND peopleDodT.useThis = 1 "
            f" LEFT JOIN placesNamesEngT AS peopleDodT$placesNamesEngT ON peopleDodT.placeId = peopleDodT$placesNamesEngT.placeId  AND peopleDodT$placesNamesEngT.useThis = 1 "
            f" WHERE peopleNamesFmlEngT.useThis = 1  AND UPPER(peopleNamesFmlEngT.lstName) LIKE UPPER('%Beethoven%')"
        )
        print(response)
        exit()

    elif "setvalue" == args[1]:
        print(args, len(args))
        if 4 != len(args) - 1:
            YMessage(f"You must provide more arguments, specifying names of table, column, and the value you want to set for all the records", logOption=True)
            exit()

        SetTableColumnToValue(g.db, args[2], args[3], args[4])
        exit()

    elif "skip1" == args[1]:
        g.skipRootsSuffixes = True

    return


############################################################
# Called from UpdateDBTablesFromCsv with the intention
# of setting the values in the peopleT table
# as well as the tables that reference the ids of peopleT
############################################################
def ProcessPeopleAndRelatedTables(peopleCsvPandaDf):
    tabs(1)
    f = inspect.stack()[0][3] + f"(peopleCsvPandaDf={str(type(peopleCsvPandaDf))}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
        # 20240711_1719: This function is currently unable to resolve disputes
        #   For example, if one of the rows in the source CSV has data for an existing person
        #   that is in conflict with what's already in the database for that person, I don't have
        #   the mechanism yet to create a "dispute" and resolve this conflict.

    valuesToCheckDict = {}
    valuesToAddDict = {}
    c = 0
    refTableId = 0 # we will check if it's still 0 at the bottom of the function
    YMessage(f"walking through peopleCsvPandaDf", logOption=LOG)
    peopleCsvPandaDf = peopleCsvPandaDf.reset_index() # Unfortunately I forgot which stackoverflow post taught me to do this step
                                        # We are basically iterating over the rows of project/temp/peopleFromWebScraping.csv

    # iteration of CSV rows begins here
    for index, row in peopleCsvPandaDf.iterrows():
        c = c + 1
        YMessage(f"row{c}=(next line)\n{row}\nindex={index}", logOption=LOG)

        ####################################
        #{g.t['refsTableName']}
        # Preparing to make an entry into the refs table, or retrieving the reference if already there
        if row[g.ucols['uRefStringColHead'][0]]: #making sure that at least the unique identifier value is not blank
            YMessage(f"*****************refsT***********************************************", logOption=LOG)
            currRefString = row[g.ucols['uRefStringColHead'][0]]
            refTableId, urlRootId, urlMainVal, urlSuffixId, urlSuffixVal = GetValueIdInRefsTable(g.db,
                                                                                                 g.t['refsTableName'], currRefString)
            YMessage(f"refTableId={refTableId}, urlRootId={urlRootId}, urlMainVal={urlMainVal}, urlSuffixId={urlSuffixId}, "
                        f"urlSuffixVal={urlSuffixVal}", logOption=LOG)
                # Though GetValueIdInRefsTable receives the full url, it knows to parse it, split it up into separate parts
                # and retrieve each column's value if this reference is already in the database
                # refTableId=0 if this reference doesn't exist in refsT, otherwise matches the id for this person
                # other values (urlRootId etc) should actually have a valid value, if they were individually found in the sub tables.
                #
                # urlRoots and urlSuffixes should have been inserted earlier into their tables from
                # project/dbManagement/references/urlRootsManualEntries.csv
                # project/dbManagement/references/urlSuffixesManualEntries.csv

            if 0 != refTableId: # the reference is already part of the database
                YMessage(f"c:{c} {currRefString} already in {g.t['refsTableName']} (id={refTableId} "
                            f"so we can add this id to the (potential) input row for peopleT)", g.logFile, ERRORLOG)

            else: # need to insert this reference first and then get refTableId
                urlRootId, urlMainVal, urlSuffixId, urlSuffixVal = PrepareRefForRefTable(g.db, currRefString)

                if not urlMainVal:
                    YMessage(f"urlMainVal is blank. Quitting", g.logFile, ERRORLOG)

                    exit()

                if urlRootId == 0:
                    YMessage(f"urlRootId is 0, meaning that the root part of {currRefString} hasn't been entered into "
                                f"{g.t['urlRootsTableName']}. Quitting", g.logFile, ERRORLOG)

                    exit()

                if urlSuffixId == 0:
                    YMessage(f"urlRootId is 0, meaning that the suffix part of {currRefString} hasn't been entered into "
                                f"{g.t['urlSuffixesTableName']}. Quitting", g.logFile, ERRORLOG)

                    exit()

                # At this point, we should be ready to add the new references to refsT table
                valuesDict = {g.tcols['refsT_addedByUsernameColHead'][0]: g.serverSideUser,
                              g.tcols['refsT_urlRootIdColHead'][0]: urlRootId,
                              g.tcols['refsT_urlMainColHead'][0]: urlMainVal,
                              g.tcols['refsT_urlSuffixIdColHead'][0]: urlSuffixId,
                              g.tcols['refsT_urlSuffixValColHead'][0]: urlSuffixVal,
                              g.tcols['refsT_timeAccessedColHead'][0]: str(round(time.time()))
                              }
                YMessage(f"Inserting into {g.t['refsTableName']} valuesDict={valuesDict}", g.logFile, LOG)
                refTableId = InsertValuesIntoTable(g.db, g.t['refsTableName'], valuesDict)
                    # We are supposed to get a valid refsT table id, if the insertion of the reference into
                    # the database was successful (0 otherwise)
                YMessage(f"got refTableId={refTableId} from InsertValuesIntoTable(g.db, g.refsTableName, valuesDict)",
                         g.logFile, LOG)
                valuesDict.clear() # we don't need it anymore until next row

                if 0 == refTableId:
                    YMessage(f"got refTableId={refTableId} from InsertValuesIntoTable(g.db, g.refsTableName, valuesDict). "
                                f"Quitting", g.logFile, ERRORLOG)

                    exit()

                # We will insert this refTableId value into people table later.

        else:
            YMessage(f"For some reason there is a blank refString value in the incoming row {row} index:{c}. "
                        f"Row was not added to the database.", g.logFile, ERRORLOG)

            exit()
        # END OF INITIAL ENTRY into refsT
        ######################################


        ######################################
        # g.t['peopleTableName']
        # Now we create an entry in {peopleTableName} table (if it's not there already)
        YMessage(f"*****************peopleT***********************************************", logOption=LOG)
        valuesDict = {g.tcols['peopleT_refIdColHead'][0]: refTableId,
                      g.tcols['peopleT_wikiPageNameOrLikeColHead'][0]: urlMainVal
                    }
        peopleTidVal = GetIdOfValuesInTable(g.db, g.t['peopleTableName'], valuesDict)

        if 0 == peopleTidVal:
            valuesDict[g.tcols['peopleT_addedByUsernameColHead'][0]] = g.serverSideUser
                # we didn't want to use this value to locate the record if it's there, but we do want to
                # us it to enter the record into the database
            YMessage(f"This person - {valuesDict} - doesn't appear to be in the database. "
                        f"Inserting", g.logFile, LOG)
            peopleTidVal = InsertValuesIntoTable(g.db, g.t['peopleTableName'], valuesDict)

        YMessage(f"peopleTidVal={peopleTidVal})", g.logFile, LOG)

        if 0 == peopleTidVal: # verifying
            YMessage(f"peopleTidVal={peopleTidVal} from InsertValuesIntoTable(g.db, {g.t['peopleTableName']}, valuesDict). "
                        f"Quitting", g.logFile, ERRORLOG)

            exit()

        # END OF INITIAL ENTRY into peopleT
        ######################################

        # SUBTABLES - filled in and then referenced by peopleT
        ######################################
        # {peopleNamesFmlEngTableName} - START of Segment
        # We assume that at least one of the name fields must have a value in the input source
        currCsvColName1 = row[g.ucols['uFstNameColHead'][0]]
        currCsvColName2 = row[g.ucols['uMidNamesColHead'][0]]
        currCsvColName3 = row[g.ucols['uLstNameColHead'][0]]

        if currCsvColName1 or currCsvColName2 or currCsvColName3:
            # Do this, if the csv row provided any of the names
            # EDIT VALUES HERE #########################################################
            tcolsRoot = "peopleNamesFmlEngT"
            YMessage(f"*****************{tcolsRoot}***********************************************", logOption=LOG)
            extraForValuesToCheck = {g.tcols[tcolsRoot + '_fstNameColHead'][0]: currCsvColName1,
                                     g.tcols[tcolsRoot + '_midNamesColHead'][0]: currCsvColName2,
                                     g.tcols[tcolsRoot + '_lstNameColHead'][0]: currCsvColName3
            }
            # Possible extra values
            peopleTthisInfoIdColHead = "peopleT_personNameFmlEngIdColHead"
            # END OF EDITS ########################################################

            # we have to see if these values for this person with the current refId are already in the
            # {tcolsRoot} table (similar process to finding values inside the refs table)
            valuesToCheckDict.clear()
            valuesToAddDict.clear()
            valuesToCheckDict = {   g.tcols[tcolsRoot + '_refIdColHead'][0]: refTableId,
                                    g.tcols[tcolsRoot + '_personIdColHead'][0]: peopleTidVal
                        } # all these values must match to be able to retrieve the id
            valuesToCheckDict = dict(valuesToCheckDict, **extraForValuesToCheck)
                    # dictionary concatenation: 'd4 = dict(d1, **d2); d4.update(d3)'
                    # # Again, forgot the url of the stackoverflow post
            valuesToAddDict[g.tcols[tcolsRoot + '_addedByUsernameColHead'][0]] = g.serverSideUser
            response = ProcessPeopleHelper1(g.db, g.t[tcolsRoot + 'ableName'], valuesToCheckDict, valuesToAddDict,
                                            peopleTidVal)

        else:
            YMessage(f"None of the names in the incoming row {row} index:{c} are set to something. Row was not added to the database.", g.logFile, ERRORLOG)

            exit()

        # END OF UPDATING peopleT with peopleT_fmlEngTable id - END of Segment
        ###################################################

        ###################################################
        # Processing peopleT_fullNameEngTable
        currCsvColName = row[g.ucols['uFullNameEngColHead'][0]]

        if currCsvColName:
            # EDIT ORANGE VALUES HERE #########################################################
            tcolsRoot = "peopleNamesFullEngT"
            YMessage(f"*****************{tcolsRoot}***********************************************", logOption=LOG)
            extraForValuesToCheck = {g.tcols[tcolsRoot + '_fullNameEngColHead'][0]: currCsvColName
            }
            # Possible extra values

            # END OF USER EDITS ########################################################

            # we have to see if these values for this person with the current refId are already in the
            # {tcolsRoot} table (similar process to finding values inside the refs table)
            valuesToCheckDict.clear()
            valuesToAddDict.clear()
            valuesToCheckDict = {g.tcols[tcolsRoot + '_refIdColHead'][0]: refTableId,
                          g.tcols[tcolsRoot + '_personIdColHead'][0]: peopleTidVal
                        } # all these values must match to be able to retrieve the id
            valuesToCheckDict = dict(valuesToCheckDict, **extraForValuesToCheck) # dictionary concatenation: 'd4 = dict(d1, **d2); d4.update(d3)'
            valuesToAddDict[g.tcols[tcolsRoot + '_addedByUsernameColHead'][0]] = g.serverSideUser
            response = ProcessPeopleHelper1(g.db, g.t[tcolsRoot + 'ableName'], valuesToCheckDict, valuesToAddDict,
                                            peopleTidVal)
        #else: # we do nothing, because there is no value to add to the "sub table"

        ###################################################
        # Processing peopleT_fullNameOrigLangTable
        currCsvColName = row[g.ucols['uFullNameOrigLangColHead'][0]]

        if currCsvColName:
            # EDIT ORANGE VALUES HERE #########################################################
            tcolsRoot = "peopleNamesFullBirthDocT"
            YMessage(f"*****************{tcolsRoot}***********************************************", logOption=LOG)
            extraForValuesToCheck = {g.tcols[tcolsRoot + '_fullNameBirthDocColHead'][0]: currCsvColName
            }
            # Possible extra values

            # END OF USER EDITS ########################################################
            # we have to see if these values for this person with the current refId are already in the
            # {tcolsRoot} table (similar process to finding values inside the refs table)
            valuesToCheckDict.clear()
            valuesToAddDict.clear()
            valuesToCheckDict = {g.tcols[tcolsRoot + '_refIdColHead'][0]: refTableId,
                          g.tcols[tcolsRoot + '_personIdColHead'][0]: peopleTidVal
                        } # all these values must match to be able to retrieve the id
            valuesToCheckDict = dict(valuesToCheckDict, **extraForValuesToCheck)
                # dictionary concatenation: 'd4 = dict(d1, **d2); d4.update(d3)'
            valuesToAddDict[g.tcols[tcolsRoot + '_addedByUsernameColHead'][0]] = g.serverSideUser
            response = ProcessPeopleHelper1(g.db, g.t[tcolsRoot + 'ableName'], valuesToCheckDict, valuesToAddDict,
                                            peopleTidVal)

        #else: # we do nothing, because there is no value to add to the "sub table"

        ###################################################
        # Processing gender subtable
        # EDIT in 4 AREAS BELOW *orange colors #########################################################
        currCsvColName = row[g.ucols['uCurrGenderColHead'][0]]

        if currCsvColName:
            tcolsRoot = "peopleGendersT"
            YMessage(f"*****************{tcolsRoot}***********************************************", logOption=LOG)
            extraForValuesToCheck = {g.tcols[tcolsRoot + '_assignedGenderValColHead'][0]: currCsvColName
            }
            # Possible extra values

            # END OF USER EDITS ########################################################

            # we have to see if these values for this person with the current refId are already in the
            # {tcolsRoot} table (similar process to finding values inside the refs table)
            valuesToCheckDict.clear()
            valuesToAddDict.clear()
            valuesToCheckDict = {g.tcols[tcolsRoot + '_refIdColHead'][0]: refTableId,
                          g.tcols[tcolsRoot + '_personIdColHead'][0]: peopleTidVal
                        } # all these values must match to be able to retrieve the id
            valuesToCheckDict = dict(valuesToCheckDict, **extraForValuesToCheck) # dictionary concatenation: 'd4 = dict(d1, **d2); d4.update(d3)'
            valuesToAddDict[g.tcols[tcolsRoot + '_addedByUsernameColHead'][0]] = g.serverSideUser
            response = ProcessPeopleHelper1(g.db, g.t[tcolsRoot + 'ableName'], valuesToCheckDict, valuesToAddDict,
                                            peopleTidVal)

        #else: # we do nothing, because there is no value to add to the "sub table"

        ###################################################
        # Processing dob subtable
        # EDIT in 4 AREAS BELOW *orange colors #########################################################
        currCsvColName1 = row[g.ucols['uDobYgrColHead'][0]]
        currCsvColName2 = row[g.ucols['uDobMgrColHead'][0]]
        currCsvColName3 = row[g.ucols['uDobDgrColHead'][0]]
        currCsvColName4 = row[g.ucols['uDobFlagColHead'][0]]

        if currCsvColName1 or currCsvColName2 or currCsvColName3:
            tcolsRoot = "peopleDobT"
            YMessage(f"*****************{tcolsRoot}***********************************************", logOption=LOG)
            extraForValuesToCheck = {g.tcols[tcolsRoot + '_evtTimeYgrColHead'][0]: currCsvColName1,
                                     g.tcols[tcolsRoot + '_evtTimeMgrColHead'][0]: currCsvColName2,
                                     g.tcols[tcolsRoot + '_evtTimeDgrColHead'][0]: currCsvColName3,
                                     g.tcols[tcolsRoot + '_dobFlagColHead'][0]: currCsvColName4
            }
            # Possible extra values

            # END OF USER EDITS ########################################################

            # we have to see if these values for this person with the current refId are already in the
            # {tcolsRoot} table (similar process to finding values inside the refs table)
            valuesToCheckDict.clear()
            valuesToAddDict.clear()
            valuesToCheckDict = {g.tcols[tcolsRoot + '_refIdColHead'][0]: refTableId,
                          g.tcols[tcolsRoot + '_personIdColHead'][0]: peopleTidVal
                        } # all these values must match to be able to retrieve the id
            valuesToCheckDict = dict(valuesToCheckDict, **extraForValuesToCheck) # dictionary concatenation: 'd4 = dict(d1, **d2); d4.update(d3)'
            valuesToAddDict[g.tcols[tcolsRoot + '_addedByUsernameColHead'][0]] = g.serverSideUser
            response = ProcessPeopleHelper1(g.db, g.t[tcolsRoot + 'ableName'], valuesToCheckDict, valuesToAddDict,
                                            peopleTidVal)

        # else: # we do nothing, because there is no value to add to the "sub table"

    # end of the big for loop that walks through the big peopleCsvPandaDf (typically generated from an input CSV file generated by WebScraping)

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)

    return


# helps ProcessPeopleAndRelatedTables to enter data into a "subtable" and then enter the resultant id into the peopleT
def ProcessPeopleHelper1(db, tableName, valuesToCheckDict, valuesToAddDict, peopleTidVal):
    tabs(1)
    f = (inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}), valuesToCheckDict={str(valuesToCheckDict)}, "
        f"valuesToAddDict={str(valuesToAddDict)}, peopleTidVal={peopleTidVal}):") #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = 0
    valuesDict = {}
    YMessage(f"subTableId = GetIdOfValuesInTable(db, {tableName}, {valuesToCheckDict})", g.logFile, LOG)
    subTableRecordId = GetIdOfValuesInTable(db, tableName, valuesToCheckDict)
    YMessage(f"subTableId = {subTableRecordId}", g.logFile, LOG)

    if 0 == subTableRecordId: # means no, this person with these exact values (valuesDict) is not already there
            # adding the remaining values to the dictionary, and inserting

            # valuesDict now has to combine valuesToCheckDict with valuesToAddDict, so that everything could be added
            # dictionary concatenation: 'd4 = dict(d1, **d2); d4.update(d3)'
            # https://stackoverflow.com/questions/1781571/how-to-concatenate-two-dictionaries-to-create-a-new-one
            valuesDict = dict(valuesToCheckDict, **valuesToAddDict)
            YMessage(f"valuesDict ={valuesDict}", logFile, LOG)

            subTableRecordId = InsertValuesIntoTable(db, tableName, valuesDict )
            YMessage(f"subTableRecordId ={subTableRecordId}", logFile, LOG)

    # END OF INITIAL ENTRY into {tableName}

    #################################
    # UPDATING peopleT, or creating a dispute, if conflict
    valuesDict.clear()

    ''' # I am commenting this out, because I changed the structure of
        # peopleT, where I no longer storeids of rows in other table
        # but I am keeping this code around in case I need it in the future for something
    valuesDict = {peopleTCurrIdColName: subTableRecordId} # this is potentially problematic if the same reference source somehow mentions different people and provides data about both of them, resulting in some "subtable" column in peopleT containing the same ID for multiple people

    potentialSubTableNameIdValInPeopleT = GetValueFromTableColumn(db, g.t['peopleTableName'], peopleTCurrIdColName, valuesDict)
    YMessage(f"potentialSubTableNameIdValInPeopleT={potentialSubTableNameIdValInPeopleT}", logFile, LOG)

    if potentialSubTableNameIdValInPeopleT == "": # needed to update peopleT record
        tempId = UpdateValueInTable(g.db, g.t['peopleTableName'], peopleTCurrIdColName, subTableRecordId, id=peopleTidVal)
        YMessage(f"tempId ={tempId}", logFile, LOG)

        if 1 != tempId: # if everything worked correctly, the ids should match
            YMessage(f"after UpdateValueInTable() tempId ={tempId}. Should be 1. () Quitting", logFile, ERRORLOG)
            exit()

    elif potentialSubTableNameIdValInPeopleT != subTableRecordId:
        c =0 # TODO: we need to create a dispute between the existing reference and the new one (see votes info 3 in https://docs.google.com/spreadsheets/d/1fy3jUDHpqie433PsN4xRqH4zFuUNDNg7w8tdPBFEHjY/edit?gid=1581176347#gid=1581176347)

    #else do nothing because we are just looking at the exact same refernce that doesn't need to be re-entered
    '''
    # END OF UPDATING peopleT with peopleT_<currentSubTable> id - END of Segment
    ###################################################

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)

    return returnVal


def SetColHeadsList(listToSet, chosenCols, dividingString):
    tabs(1)
    f = inspect.stack()[0][3] + f"(listToSet={str(listToSet)}, chosenCols={chosenCols}, dividingString={dividingString}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    for colName in chosenCols:
        keyName = colName[colName.find(dividingString)+len(dividingString):9999]
        YMessage(f"keyName={keyName}", logFile, LOG)
        listToSet.append(g.tableRelsDict[keyName][g.tableRelsDictHtmlColNameIdx])
        YMessage(f"g.tableRelsDict[{keyName}]={g.tableRelsDict[keyName]}", logFile, LOG)

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)

    return


def SetOptLeftJoinDictKeyVal(optLeftJoinDict, keyToSet, leftJoinTableName, leftJoinTableAsName, preexistingTableAsName, commonColName, commonColNameNewTable, useThisColName):
    tabs(1)
    f = inspect.stack()[0][3] + f"(optLeftJoinDict={str(optLeftJoinDict)}, keyToSet={keyToSet}, leftJoinTableName={leftJoinTableName}, leftJoinTableAsName={leftJoinTableAsName}, useThisColName={useThisColName}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    keyVal = ""
    optLeftJoinDict[keyToSet] = optLeftJoinDict.get(keyToSet, []) # provides a default value for the key if it doesn't exist ref: https://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
    commandToAdd = ( \
        f"LEFT JOIN {leftJoinTableName} AS {leftJoinTableAsName} "
        f"ON {preexistingTableAsName}.{commonColName} = "
            f"{leftJoinTableAsName}.{commonColNameNewTable} "
    )

    if not leftJoinTableName in g.noUseThisTableList:
        commandToAdd = commandToAdd + f" AND {leftJoinTableAsName}.{useThisColName} = 1 \n"


    optLeftJoinDict[keyToSet] = commandToAdd

    f = inspect.stack()[0][3] + f"(optLeftJoinDict={str(optLeftJoinDict)}, keyToSet={keyToSet}, leftJoinTableName={leftJoinTableName}, leftJoinTableAsName={leftJoinTableAsName}, useThisColName={useThisColName}):" #function name
    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return keyVal


def SetTableColumnToValue(db, tableName, colName, value):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}), colName={str(colName)}, value={value}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    returnVal = 0

    if not IsTableExists(db, tableName):
        YMessage(f"table {tableName} doesn't exist", logFile, LOG)
        exit()

    if not IsColumnExistsInTable(db, tableName, colName):
        YMessage(f"table {tableName} doesn't have {colName} column", logFile, LOG)
        exit()

    response1 = db.execute(
        f"SELECT id FROM {tableName}"
    )

    if not response1:
        YMessage(f"Something went wrong and there was no response1 from db.execute", logFile, LOG)
        exit()

    for dict in response1:
        response2 = db.execute(
            f"UPDATE {tableName} "
            f"SET {colName} = \'{value}\' "
            f"WHERE id = {dict['id']}"
        )
        if not response2:
            YMessage(f"Something went wrong and there was no response2 from db.execute", logFile, LOG)
            exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return returnVal


def SetValuesInTable(db, tableName, pandasDfValue, username):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}), dictvalue={str(pandasDfValue)}, username={username}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    #VerifyDBIsValid(db) # Not doing it - already verified in UpdateDb and this is downstream

    VerifyValueIsNotBlankOrNull(pandasDfValue, type="pandas")

    if g.t['urlRootsTableName'] == tableName:
        YMessage(f"About to check if '{g.t['urlRootsTableName']}' already contains value "
                 f"'{pandasDfValue[g.tcols['urlRootsT_urlRootColHead'][0]]}' under '{g.tcols['urlRootsT_urlRootColHead'][0]}'", logOption=LOG)
        AddAnyMissingColumnsToTable(db, tableName)

        if IsValueInTable(db, tableName, g.tcols['urlRootsT_urlRootColHead'][0], pandasDfValue[g.tcols['urlRootsT_urlRootColHead'][0]]):
            YMessage(f"ENDED {f}", logFile, LOG)
            tabs(-1)
            return g.setValsDidNotInsertDueToDuplicate

        else:
            YMessage(f"About to set '{tableName}' table with these dictvalue: {pandasDfValue}", logFile, LOG)
            InsertValueIntoTable(db, tableName, g.tcols['urlRootsT_urlRootColHead'][0], pandasDfValue[g.tcols['urlRootsT_urlRootColHead'][0]])

    elif g.t['urlSuffixesTableName'] == tableName:
        YMessage(f"{pandasDfValue}", logFile, LOG)
        YMessage(f"About to check if '{g.t['urlSuffixesTableName']}' already contains value '{pandasDfValue[g.tcols['urlSuffixesT_urlSuffixColHead'][0]]}' under '{g.tcols['urlSuffixesT_urlSuffixColHead'][0]}'", logFile, LOG)

        if IsValueInTable(db, tableName, g.tcols['urlSuffixesT_urlSuffixColHead'][0], pandasDfValue[g.tcols['urlSuffixesT_urlSuffixColHead'][0]]):
            YMessage(f"ENDED {f}", logFile, LOG)
            tabs(-1)
            return g.setValsDidNotInsertDueToDuplicate

        else:
            YMessage(f"About to set '{tableName}' table with these dictvalue: {pandasDfValue}", logFile, LOG)

            AddAnyMissingColumnsToTable(db, tableName)
            InsertValueIntoTable(db, tableName, g.tcols['urlSuffixesT_urlSuffixColHead'][0], pandasDfValue[g.tcols['urlSuffixesT_urlSuffixColHead'][0]])

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return


def SplitUrlIntoParts(db, value):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={db}, value={value}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
        # The incoming URL (value) will be attempted to split into parts for storage in the database
        # The parts are:
        #   url root (an often repeating string, common to many urls, like e.g. https://en.wikipedia.org/w/index.php?title=)
        #   url main (the value that follows the root, e.g. Franz_Liszt)
        #   url suffix (an often repeating string following url main, e.g. &oldid=)
        #   url suffix value (a string that follows url suffix e.g. 1226730181)

    urlRootId = 0
    urlMainVal = ""
    urlSuffixId = 0
    urlSuffixVal = ""

    YMessage(f"About to check {g.t['urlRootsTableName']} for what url roots it already has.", logOption=LOG)
    listOfRootDicts = GetListOfValuesFromTableColumn(db, g.t['urlRootsTableName'], g.tcols['urlRootsT_urlRootColHead'][0])
    YMessage(f"listOfRootDicts={listOfRootDicts}", logOption=LOG)
    YMessage(f"About to check {g.t['urlSuffixesTableName']} for what url roots it already has.", logOption=LOG)
    listOfSuffixDicts = GetListOfValuesFromTableColumn(db, g.t['urlSuffixesTableName'], g.tcols['urlSuffixesT_urlSuffixColHead'][0])

    urlMainVal, urlSuffixVal = GetUrlMainSuffixPartFromUrl(listOfRootDicts, listOfSuffixDicts, value)

    if urlMainVal != value: # means that we have a separate "main part" serving as a unique ID (true for all wikipedia pages)
        # Establish the root value
        urlRoot = value[0:value.find(urlMainVal)]
        urlRootId = GetIdOfValueInTable(db, g.t['urlRootsTableName'], g.tcols['urlRootsT_urlRootColHead'][0], urlRoot)
        YMessage(f"urlRoot={urlRoot} located at id = {urlRootId} in {g.t['urlRootsTableName']} table", logOption=LOG)

    else: # seems like we are not dealing with a non-standard url
        # throw a message for now
        YMessage(f"value={value}. Don't know how to handle yet. Quitting.", logFile, ERRORLOG)

        exit()

    if urlSuffixVal != "": # means that we have a separate "main part" serving as a unique ID (true for all wikipedia pages)
        # Establish the suffix value
        urlSuffix = value[value.find(urlMainVal)+len(urlMainVal):-len(urlSuffixVal)]
        urlSuffixId = GetIdOfValueInTable(db, g.t['urlSuffixesTableName'], g.tcols['urlSuffixesT_urlSuffixColHead'][0], urlSuffix)
        YMessage(f"urlSuffix={urlSuffix} located at id = {urlSuffixId} in {g.t['urlSuffixesTableName']} table", logFile, LOG)

    else: # seems like we are not dealing with a non-standard url
        # throw a message for now
        YMessage(f"value={value}. Don't know how to handle yet. Quitting.", logFile, ERRORLOG)

        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)

    return urlRootId, urlMainVal, urlSuffixId, urlSuffixVal


def SetListTest(testList, val):
    testList.append(val)
    return


##########################################################
# Called from dbManagement.py
def UpdateDBTablesFromCsv(summaryRowDict):
    # Entry function after the user executes dbManagement.py and it finds
    # an instruction to process a wikipedia's summary page
    tabs(1)
    f = inspect.stack()[0][3] + f"(summaryRowDict={summaryRowDict}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    YMessage(f"Trying to open {g.databaseCall}", logFile, LOG)

    try:
        g.db = SQL(g.databaseCall)

    except:
        YMessage(f"For some reason {g.databaseCall} database couldn't be opened. Quitting", logFile, ERRORLOG)
        exit()

    VerifyDbIsValid(g.db)

    if 0 <= 1 < len(sys.argv): # we do have an argument coming in from the command line which changes the default running of the program

        if "quit1" == sys.argv[1]: # for special cases when I want to quit right away during testing
            exit()

    for key in g.t: # make sure to create all needed tables (as per gVars.py t dictionary)
            CreateDbTableIfNotExist(g.db, g.t[key])

    if 0 <= 1 < len(sys.argv):
        ProcessCmdLineArgs(sys.argv) # we want to process these after having made sure all the needed tables have been created above

    response = 0

    if not g.skipRootsSuffixes: # This allows me to bypass this step during the testing phase of this program
        # First deal with setting up urlRoots table using the urlRoots manual CSV file *as it will be used by the people table which comes next
        urlRootsCsvFilePath = g.referencesDirPath + summaryRowDict[g.lorUrlRootsTableFileNameKey]
        urlRootsCsvPandaDf = OpenAndGetDictFromCsv(urlRootsCsvFilePath, "r", logFile, LOG)
        InsertUniqueValuesToTable(g.db, g.t['urlRootsTableName'], g.tcols['urlRootsT_urlRootColHead'][0], urlRootsCsvPandaDf, sourceType="CSV", sourceFilePath=urlRootsCsvFilePath)
            # urlRootsT (typically located here: project/dbManagement/references/urlRootsManualEntries.csv) contains the so-called url roots referenced by refsT table
            # These are added to the urlRootsT table, making sure not to insert duplicate values
            # 20240711_1126: As of right now, wikipedia roots like https://<two character language code>.wikipedia.org/w/index.php?title=

        # Now the same but for Suffixes
        urlSuffixesCsvFilePath = g.referencesDirPath + summaryRowDict[g.lorUrlSuffixesTableFileNameKey]
        urlSuffixesCsvPandaDf = OpenAndGetDictFromCsv(urlSuffixesCsvFilePath, "r", logFile, LOG)
        InsertUniqueValuesToTable(g.db, g.t['urlSuffixesTableName'], g.tcols['urlSuffixesT_urlSuffixColHead'][0], urlSuffixesCsvPandaDf, sourceType="CSV", sourceFilePath=urlSuffixesCsvFilePath)
            # 20240711_1127: As of right now, only one suffix is used: &oldid=
            #           e.g. https://en.wikipedia.org/w/index.php?title=Truid_Aagesen&oldid=1216808988

    ############################################
    # Now populate the "people" table (peopleT)
    peopleCsvFilePath = g.tempCsvDirPath + summaryRowDict[g.lorPeopleTableFileNameKey]
    peopleCsvPandaDf = OpenAndGetDictFromCsv(peopleCsvFilePath, "r", logFile, LOG)
    NMessage(f"peopleCsvPandaDf={type(peopleCsvPandaDf)}", logFile, LOG)
    ProcessPeopleAndRelatedTables(peopleCsvPandaDf)

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return response


def UpdateDbDataFromHtml(db, updateTheseRows, parsedSearchResults, htmlResultsNamePrefixLen, user):
    tabs(1)
    f = inspect.stack()[0][3] + f"(updateTheseRows={updateTheseRows}, parsedSearchResults={parsedSearchResults}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)
    NMessage(f"g.editorsList={g.editorsList} user={user}", logFile, LOG)

    # parsedSearchResults is a pointer to the search results dictionary structurethat maintains the search results table, and keeps it in sync with the database
    # we must update it here (as in InsertDbDataFromHtml) or else on refresh we will be losing the database data, because it'll think that I entered "None"
    # IT was a problem I disocvered 20240708_2227

    # g.numRecordsUpdated = 0 # we'll reset this in updatePeople route in app.py
    # g.recordsUpdatedMessage = "" # ditto
    message = ""
    error = 0

    if not user in g.editorsList:
        error = 403
        message = "You currently don't have the privileges to update the data in the database. Contact administrator"

    else:
        for row in updateTheseRows:
            YMessage(f"updating {row}", logFile, LOG)
            dataTableName = g.tableRelsDict[f"{row['tableName']}_{row['colName']}"][g.tableRelsDictDataTNameIdx]
            relatedIdColName = g.tableRelsDict[f"{row['tableName']}_{row['colName']}"][g.tableRelsDictSharedIdsColNameIdx]
            YMessage(f"dataTableName={dataTableName}", logFile, LOG)
            colName = row['colName']
            mainTableIdColName = 'personId'
            personId = row[mainTableIdColName]
            mainTableIdColValue = personId
            newVal = row['newVal'].replace("'","%27").replace('"',"%22")

            if dataTableName == row['tableName']:
                optWhereMainTableRecordIdCmd = f" AND {mainTableIdColName} = \'{mainTableIdColValue}\' "

            else:
                message = f"Sorry. I haven't yet come up with the logic to update data that lives in 'subtables', such as {dataTableName} for your {newVal}"
                error = 500
                YMessage(f"ENDED {f}", logFile, LOG)
                tabs(-1)
                return message, error

            # First check if this value has been changed by another user very recently.
            # optWhereMainTableRecordIdCmd is needed to deal with bits of data
            # in the same table (like peopleDobT), where we must match the unique main table record id (eg. personId)
            # With data in a different table (eg. placesNamesEngT for POB records), which itself might be referenced through another table (i.e. placesT)
            # the id value of which is actually used in our "row['tableName']" table, things get quite complicated and I should actually
            # have a separate, more complicated, possible recursive logic for dealing with such cases
            response = db.execute(
                f" SELECT {colName} FROM {dataTableName} "
                f" WHERE {colName} = \'{newVal}\' {optWhereMainTableRecordIdCmd} "
            )

            if response:
                error = 500
                message = f"Trouble. The value {newVal} for col {colName} has already been changed to {response}"
                YMessage(f"ENDED {f}", logFile, LOG)
                tabs(-1)
                return message, error

            response = db.execute(
                f" UPDATE {dataTableName} "
                f" SET {colName} = \'{newVal}\' "
                f" WHERE personId = \'{personId}\' "
            )
            SetDictListValue(parsedSearchResults,
                             mainTableIdColName,
                             mainTableIdColValue,
                             "x" * htmlResultsNamePrefixLen + row['tableName'] + "_" + colName,
                             newVal, logFile=logFile, logOption=LOG)
            g.recordsUpdatedDetails = g.recordsUpdatedDetails + f" {dataTableName}.{colName}={newVal} "
            YMessage(f"response={response}", logFile, LOG)
            g.numRecordsUpdated = g.numRecordsUpdated + 1 # although in the case of UPDATE I think it returns the number of records updated - i.e. 1 in this case, same thing

        g.recordsUpdatedMessage = f"{g.numRecordsUpdated} record{'' if g.numRecordsUpdated == 1 else 's'} updated. [{g.recordsUpdatedDetails}]"

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return message, error


def VerifyDbIsValid(db):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    if not db:
        YMessage(f"db is not pointing to a valid database.")
        exit()

    NMessage(f'about to execute db.execute("SELECT * FROM pragma_database_list").', logFile, LOG)
    response = db.execute("SELECT * FROM pragma_database_list")
    NMessage(f"response={response}.", logFile, LOG)

    if not g.dbName in str(response):
        YMessage(f"db is not pointing to {g.dbName} database.", logFile, LOG)
        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return


def UpdateValueInTable(db, tableName, colName, value, id):
    tabs(1)
    f = inspect.stack()[0][3] + f"(db={str(db)}, tableName={tableName}, colName={colName}, value={str(value)}, id={id}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    response = db.execute(
        f"UPDATE ? "
        f"SET {colName} = \'{str(value)}\' "
        f"WHERE id = \'{id}\'"
        , tableName
        )

    if not response:
        YMessage(f"Something went wrong and '{tableName}' table wasn't updated", logFile, LOG)
        exit()

    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return response


def VerifyValueIsNotBlankOrNull(value, type="regular"): #type could be "pandas"
    tabs(1)
    f = inspect.stack()[0][3] + f"(value={value}):" #function name
    YMessage(f"STARTED {f}", logFile, LOG)

    if type == "regular":
        if not value: #although it appears that dictvalue dictionary (created by DictReader) skips blank values
            YMessage(f"VerifyValueIsNotBlankOrNull(value): value is blank", logFile, LOG)
            exit()

    elif type == "pandas":
        c=0
        ''' # I don't understand how pandas works
        if value.all(): #although it appears that dictvalue dictionary (created by DictReader) skips blank values
            YMessage(f"VerifyValueIsNotBlankOrNull(value): pandas value is empty: {value.all()}")
            exit()
        '''
    YMessage(f"ENDED {f}", logFile, LOG)
    tabs(-1)
    return

