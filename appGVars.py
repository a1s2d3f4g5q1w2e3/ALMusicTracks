from datetime import datetime
import dbManagement.gVars as mgv #according to chatGPT this is an "absolute import" and it solved the problem of using helper functions inside app.py

#from flask import Flask, flash, redirect, render_template, request, session
#from cs50 import SQL
# This document manages the global variables for app.py

DEBUG = 1

current_year = datetime.today().year

db = "" # will hold the db database file

# Column parameters are defined below (Idx = HTML table row "name" attribute). Right now width: does nothing (overridden by th style width)
# ph1 = placeholder in the first row
htmlSearchNamePrefixLen = 2
htmlResultsNamePrefixLen = 4
searchFields = [{'head':mgv.tableRelsDict[mgv.t['peopleNamesFmlEngTableName']       +"_"+mgv.tcols['peopleNamesFmlEngT_lstNameColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],               'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleNamesFmlEngTableName']       +"_"+mgv.tcols['peopleNamesFmlEngT_lstNameColHead'][0],                 'ph1':'','ph2':'','ph3':'','width': '100', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleNamesFmlEngTableName']       +"_"+mgv.tcols['peopleNamesFmlEngT_fstNameColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],               'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleNamesFmlEngTableName']       +"_"+mgv.tcols['peopleNamesFmlEngT_fstNameColHead'][0],                 'ph1':'','ph2':'','ph3':'','width': '080', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleNamesFmlEngTableName']       +"_"+mgv.rcols['refsT_urlColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                                'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleNamesFmlEngTableName']       +"_"+mgv.rcols['refsT_urlColHead'][0],                                  'ph1':'','ph2':'','ph3':'','width': '010', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleNamesFullEngTableName']      +"_"+mgv.tcols['peopleNamesFullEngT_fullNameEngColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],          'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleNamesFullEngTableName']      +"_"+mgv.tcols['peopleNamesFullEngT_fullNameEngColHead'][0],            'ph1':'','ph2':'','ph3':'','width': '160', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                #{'head':mgv.tableRelsDict[mgv.t['peopleNamesFullBirthDocTableName'] +"_"+mgv.tcols['peopleNamesFullBirthDocT_fullNameBirthDocColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleNamesFullBirthDocTableName'] +"_"+mgv.tcols['peopleNamesFullBirthDocT_fullNameBirthDocColHead'][0],  'ph1':'','ph2':'','ph3':'','width': '100', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleNamesPseudonymsTableName']   +"_"+mgv.tcols['peopleNamesPseudonymsT_pseudonymEngColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],      'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleNamesPseudonymsTableName']   +"_"+mgv.tcols['peopleNamesPseudonymsT_pseudonymEngColHead'][0],        'ph1':'','ph2':'','ph3':'','width': '080', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                #{'head':mgv.tableRelsDict[mgv.t['peopleGendersTableName']           +"_"+mgv.tcols['peopleGendersT_assignedGenderValColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],         'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleGendersTableName']           +"_"+mgv.tcols['peopleGendersT_assignedGenderValColHead'][0],           'ph1':'','ph2':'','ph3':'','width': '100', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_dobFlagColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                       'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_dobFlagColHead'][0],                         'ph1':'','ph2':'','ph3':'','width': '110', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_evtTimeYgrColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                    'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_evtTimeYgrColHead'][0],                      'ph1':'','ph2':'','ph3':'','width': '110', 'valFrom': '', 'valTo': '', 'type': 'number','min': -9999,   'max': current_year},
                {'head':mgv.tableRelsDict[mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_evtTimeMgrColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                    'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_evtTimeMgrColHead'][0],                      'ph1':'','ph2':'','ph3':'','width': '080', 'valFrom': '', 'valTo': '', 'type': 'number','min': 1,       'max': 12},
                {'head':mgv.tableRelsDict[mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_evtTimeDgrColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                    'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDobTableName']               +"_"+mgv.tcols['peopleDobT_evtTimeDgrColHead'][0],                      'ph1':'','ph2':'','ph3':'','width': '080', 'valFrom': '', 'valTo': '', 'type': 'number','min': 1,       'max': 31},
                #{'head':mgv.tableRelsDict[mgv.t['peopleDobTableName']               +"_"+mgv.tcols['placesNamesEngT_placeNameColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDobTableName']               +"_"+mgv.tcols['placesNamesEngT_placeNameColHead'][0],                  'ph1':'','ph2':'','ph3':'','width': '100', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': 1,       'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_dodFlagColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                       'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_dodFlagColHead'][0],                         'ph1':'','ph2':'','ph3':'','width': '110', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': '',      'max': ''},
                {'head':mgv.tableRelsDict[mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_evtTimeYgrColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                    'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_evtTimeYgrColHead'][0],                      'ph1':'','ph2':'','ph3':'','width': '110', 'valFrom': '', 'valTo': '', 'type': 'number','min': -9999,   'max': current_year},
                {'head':mgv.tableRelsDict[mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_evtTimeMgrColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                    'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_evtTimeMgrColHead'][0],                      'ph1':'','ph2':'','ph3':'','width': '080', 'valFrom': '', 'valTo': '', 'type': 'number','min': 1,       'max': 12},
                {'head':mgv.tableRelsDict[mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_evtTimeDgrColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                    'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDodTableName']               +"_"+mgv.tcols['peopleDodT_evtTimeDgrColHead'][0],                      'ph1':'','ph2':'','ph3':'','width': '080', 'valFrom': '', 'valTo': '', 'type': 'number','min': 1,       'max': 31},
                #{'head':mgv.tableRelsDict[mgv.t['peopleDodTableName']               +"_"+mgv.tcols['placesNamesEngT_placeNameColHead'][0]][mgv.tableRelsDictHtmlColNameIdx],                'name':"x" * htmlSearchNamePrefixLen +mgv.t['peopleDodTableName']               +"_"+mgv.tcols['placesNamesEngT_placeNameColHead'][0],                  'ph1':'','ph2':'','ph3':'','width': '100', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': 1,       'max': ''}
                #{'head'mgv.tableRelsDict[mgv.t['peopleNamesFmlEngTableName']+"_"+mgv.tcols['peopleNamesFmlEngT_lstNameColHead'][0]][mgv.tableRelsDictOptColNameIdx],  'name':"x" * htmlNamePrefixLen +mgv.t['peopleOccupationsTableName']      +"_"+mgv.tcols['occupationsT_wikiPageNameOrLikeColHead'][0],          'ph1':' ','ph2':'','ph3':'','width': '130', 'valFrom': '', 'valTo': '', 'type': 'text',  'min': 1,       'max': ''}
            ]

refreshFormCheck = []
allSearchRows = []
tempSearchFields = searchFields.copy()
allResultRows = []
initNumSearchRows = 3
resultsRowsMaxLimit = 10000
parsedSearchResults = [] # stores results retrieved by db.execute during the database search (SELECT ... WHERE)
updateTheseRows = [] # list of dictionaries showing which table and which rows to update with the corresponding values
insertTheseRows = [] # list of dictionaries showing which table and which rows to update with the corresponding values
chosenColsHeads = []




##############################################################################################################################
# Keeping the items below from the finance project until I figure out how to integrate the financial part with the database
transactionsTableNameRoot = "transactions"
# transactionsTableName = "" #to be set at Login or Register. 20240521_2159 Well, that great idea failed. Seems like I have to set it every time locally
institutionsTableNameRoot = "institutions"
userInstitutions = []
usersTableName = "usersT"

handshakeInstructions = ""
maxRowsInIndex = 999

addFinancialInstitutionsMsg = "Add a financial institution first."
institutionAddedMsg = "Financial Institution Added!"
errorCreatingInstitutionsTableMsg = (
    "couldn't create an institutions table for this user"
)
errorInsertInstitutionMsg = "couldn't add new institution to table for this user"
errorProvideInstitutionName = "INSTITUTION NAME MISSING"
errorMalformedInstitutionsTable = "CONTACT ADMINISTRATOR - institutionsTable empty"
errorAccountNumberMissing = "ACCOUNT NUMBER MISSING"
errorDuplicateAccount = "ACCOUNT ALREADY ADDED"
errorSelectFromTransactionTable = (
    "BACKEND PROBLEM. CONTACT ADMINISTRATOR. COULDN'T GET DATA FROM "
)

listOfInstitutions = [
    "A BANK",
    "B BANK",
    "C BANK",
    "D BANK",
    "E BANK",
    "F BANK",
    "G BANK",
    "H BANK",
    "I BANK",
    "J BANK",
    "K BANK",
    "L BANK",
    "M BANK",
    "N BANK",
    "O BANK",
    "P BANK",
    "Q BANK",
    "R BANK",
    "S BANK",
    "T BANK",
    "U BANK",
    "V BANK",
    "Y BANK",
    "X BANK",
    "Y BANK",
    "Z BANK",
]
