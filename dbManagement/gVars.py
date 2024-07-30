import os
import wikipediaapi

#f = inspect.stack()[0][3] #returns "module" (meaning this file)
f = __file__

# Variables that help to control the information printed to the console as well as some variables used for testing
DEBUG = False
LOG = False
TESTING = False
logChoice = False
ERRORLOG = True
if 1==1:
    DEBUG = True
else:
    DEBUG = False
if 0==1:
    LOG = True
else:
    LOG = False
if 0==1:
    TESTING = True
    testIDStart = 11
    testIDEnd = 22
else:
    TESTING = False

# Paths to various resources
dirname = os.path.dirname(__file__)
tempCsvDirPath = os.path.join(dirname, "../temp/")
staticDirPath = os.path.join(dirname, "../static/")
referencesDirPath = os.path.join(dirname, "references/")

listOfResourcesCsvPath = os.path.join(staticDirPath, "listOfResources.csv" )
logFilePath = os.path.join(dirname, "temp/log.txt" )
logFile = open(logFilePath, "w")
lorTempSummaryCsvKey = "tempSummaryCsv"
lorPeopleTableFileNameKey = "peopleTableFileName"
lorUrlRootsTableFileNameKey = "urlRootsTableFileName"
lorUrlSuffixesTableFileNameKey = "urlSuffixesTableFileName"

skipRootsSuffixes = False

mainPathDirname = dirname[0:dirname.rfind("/")]
pathToUtils = f"{mainPathDirname}/"
relativePathToUtils = "../utils/"
editorsTxtFileAbsPath = f"{mainPathDirname}/temp/editors.txt"

with open(editorsTxtFileAbsPath) as file:
    editorsList = [line.rstrip() for line in file]


db = "" # will hold the db database file
dbName = "musictracks.db"
databaseCall = "sqlite:///../" + dbName #we are assuming that dbManagement lives inside a project/subfolder
currPersonRow = -1 #to keep track of who the current person is (by summary file's row)
serverSideUser = "admin" # sets "addedByUsername" columns in tables when the python code is ran "offline" on the server side, without the involvement of the webapp


# List of sqlite3 table names and column names
#standardAddedByUsernameList = ["addedByUsername", f"TEXT NOT NULL"]
#standardPersonIdReferences = ["personId", f"INTEGER NOT NULL REFERENCES {peopleTableName}(id)"]
t = {} # table names
tcols = {} # table columns
scols = {} # search columns (used by search fields which can be a combination of multiple columns in the database)
rcols = {} # result columns (used by result table, which can be a combination of multiple columns in the database)

# having to put all table names at the top because I reference them inside by lists
t['disputesTableName'] = 'disputesT' #b disputesT
t['musCompsTableName'] = 'musCompsT'	#b musCompsT
t['musCompsWorkStartedDatesTableName'] = 'musCompsWorkStartedDatesT'	#b musCompsWorkStartedDatesT
t['musCompsWorkEndedDatesTableName'] = 'musCompsWorkEndedDatesT'	#b musCompsWorkEndedDatesT
t['musCompsPieceTitleEngTableName'] = 'musCompsPieceTitleEngT'	#b musCompsPieceTitleEngT
t['musCompsPieceTitleOrigLangTableName'] = 'musCompsPieceTitleOrigLangT'	#b musCompsPieceTitleOrigLangT
t['musCompsPerformancesTableName'] = 'musCompsPerformancesT'
t['musCompsPublicationsTableName'] = 'musCompsPublicationsT'
t['musCompsCreatorsTableName'] = 'musCompsCreatorsT'	#b musCompsCreatorsT
t['occupationsTableName'] = 'occupationsT'	#b occupationsT
t['peopleTableName'] = 'peopleT'	#b peopleT
t['peopleDobTableName'] = 'peopleDobT'	#b dobT
t['peopleDodTableName'] = 'peopleDodT'	#b dodT
t['peopleGendersTableName'] = 'peopleGendersT'	#b peopleGendersT
t['peopleNamesFmlEngTableName'] = 'peopleNamesFmlEngT'	#b peopleNamesFmlEngT
t['peopleNamesFullEngTableName'] = 'peopleNamesFullEngT'	#b peopleNamesFullEngT
t['peopleNamesFullBirthDocTableName'] = 'peopleNamesFullBirthDocT'	#b peopleNamesFullOrigLangT
t['peopleOccupationsTableName'] = 'peopleOccupationsT'	#b placesLivedT
t['peopleNamesPseudonymsTableName'] = 'peopleNamesPseudonymsT'	#b peopleNamesPseudonymsT
t['peopleMetTableName'] = 'peopleMetT'	#b peopleMet
t['peopleTeachersTableName'] = 'peopleTeachersT'	#b peopleTeachersT
t['placesTableName'] = 'placesT'	#b placesT
t['placesNamesEngTableName'] = 'placesNamesEngT'	#b placesNamesEngT
t['refsTableName'] = 'refsT'	#b refsT
t['tableNamesTableName'] = 'tableNamesT'
t['urlRootsTableName'] = "urlRootsT"
t['urlSuffixesTableName'] = "urlSuffixesT"
t['usersTableName'] = "usersT"
t['votesTableName'] = 'votesT'	#b votesT

noUseThisTableList = [t['refsTableName'], t['urlRootsTableName'], t['urlSuffixesTableName']]

tcols['disputesT_tableNameColHead'] = ['tableName','TEXT NOT NULL']
tcols['disputesT_disputedIdsListsColHead'] = ['disputedIdsLists','TEXT NOT NULL']
tcols['disputesT_commentsListColHead'] = ['commentsList','TEXT DEFAULT "[]"']
tcols['disputesT_voteValsListColHead'] = ['voteValsList','TEXT NOT NULL DEFAULT "[]"']
tcols['disputesT_colNamesListColHead'] = ['colNamesList','TEXT DEFAULT "[]"']
tcols['disputesT_timeStartedColHead'] = ['timeStarted','INTEGER NOT NULL']
tcols['disputesT_timeEndedColHead'] = ['timeEnded','INTEGER']
tcols['disputesT_listsIdxWinnerColHead'] = ['listsIdxWinner','INTEGER']

#musCompsTableName = 'musCompsT'	#b musCompsT
tcols['musCompsT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['musCompsT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsT_wikiPageNameOrLikeColHead'] = ['wikiPageNameOrLike',f'TEXT NOT NULL UNIQUE']
tcols['musCompsT_mainComposerIdColHead'] = ['mainComposerId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['musCompsT_mainArrangerIdColHead'] = ['mainArrangerId',f'INTEGER REFERENCES peopleT(id)']
tcols['musCompsT_pieceTitleEngIdColHead'] = ['pieceTitleEngId',f'INTEGER REFERENCES musCompsPieceTitleEngT(id)']
tcols['musCompsT_pieceTitleOrigLangIdColHead'] = ['pieceTitleOrigLangId',f'INTEGER REFERENCES musCompsPieceTitleOrigLangT(id)']
tcols['musCompsT_dateWorkStartedIdColHead'] = ['dateWorkStartedId',f'INTEGER REFERENCES musCompsWorkStartedDatesT(id)']
tcols['musCompsT_dateWorkEndedIdColHead'] = ['dateWorkEndedId',f'INTEGER REFERENCES musCompsWorkEndedDatesT(id)']
tcols['musCompsT_firstPublishedIdColHead'] = ['firstPublishedId',f'INTEGER REFERENCES musCompsPublications(id)']
tcols['musCompsT_firstPerformedIdColHead'] = ['firstPerformedId',f'INTEGER REFERENCES musCompsPerformances(id)']

#musCompsCreatorsTableName = 'musCompsCreatorsT'	#b musCompsCreatorsT
tcols['musCompsCreatorsT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['musCompsCreatorsT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsCreatorsT_musCompIdColHead'] = ['musCompId',f'INTEGER REFERENCES {t["musCompsTableName"]}(id)']
tcols['musCompsCreatorsT_creatorIdColHead'] = ['creatorId',f'INTEGER REFERENCES {t["peopleTableName"]}(id)']
tcols['musCompsCreatorsT_roleValColHead'] = ['roleVal','TEXT']
tcols['musCompsCreatorsT_voteValColHead'] = ['voteVal','DEFAULT 0']

#Performances
tcols['musCompsPerformancesT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['musCompsPerformancesT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsPerformancesT_musCompIdColHead'] = ['musCompId',f'INTEGER NOT NULL REFERENCES {t["musCompsTableName"]}(id)']
tcols['musCompsPerformancesT_performerNamesColHead'] = ['performerNames',f'TEXT']
tcols['musCompsPerformancesT_performerIdColHead'] = ['performerId',f'INTEGER REFERENCES {t["peopleTableName"]}(id)']
tcols['musCompsPerformancesT_datePerYColHead'] = ['datePerY',f'INTEGER']
tcols['musCompsPerformancesT_datePerMColHead'] = ['datePerM',f'INTEGER']
tcols['musCompsPerformancesT_datePerDColHead'] = ['datePerD',f'INTEGER']
tcols['musCompsPerformancesT_performanceVenueColHead'] = ['performanceVenue',f'INTEGER REFERENCES {t["placesTableName"]}(id)']
tcols['musCompsPerformancesT_peopleInTheAudienceColHead'] = ['peopleInTheAudience',f'TEXT']
tcols['musCompsPerformancesT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']

#musCompsPieceTitleEngTableName = 'musCompsPieceTitleEngT'	#b musCompsPieceTitleEngT
tcols['musCompsPieceTitleEngT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['musCompsPieceTitleEngT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsPieceTitleEngT_musCompIdColHead'] = ['musCompId',f'INTEGER NOT NULL REFERENCES {t["musCompsTableName"]}(id)']
tcols['musCompsPieceTitleEngT_pieceTitleColHead'] = ['pieceTitle','TEXT']
tcols['musCompsPieceTitleEngT_pieceLargerWorkNameColHead'] = ['pieceLargerWorkName','TEXT']
tcols['musCompsPieceTitleEngT_voteValColHead'] = ['voteVal','INTEGER DEFAULT 0']

#musCompsPieceTitleOrigLangTableName = 'musCompsPieceTitleOrigLangT'	#b musCompsPieceTitleOrigLangT
tcols['musCompsPieceTitleOrigLangT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['musCompsPieceTitleOrigLangT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsPieceTitleOrigLangT_musCompIdColHead'] = ['musCompId',f'INTEGER NOT NULL REFERENCES {t["musCompsTableName"]}(id)']
tcols['musCompsPieceTitleOrigLangT_pieceTitleColHead'] = ['pieceTitle','TEXT']
tcols['musCompsPieceTitleOrigLangT_pieceLargerWorkNameColHead'] = ['pieceLargerWorkName','TEXT']
tcols['musCompsPieceTitleOrigLangT_voteValColHead'] = ['voteVal','INTEGER DEFAULT 0']

#
tcols['musCompsPublicationsT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['musCompsPublicationsT_refIdColHead'] = ['refId','INTEGER NOT NULL REFERENCES refsT(id)']
tcols['musCompsPublicationsT_musCompIdColHead'] = ['musCompId','INTEGER NOT NULL REFERENCES musCompsT(id)']
tcols['musCompsPublicationsT_publisherNameColHead'] = ['publisherName','TEXT']
tcols['musCompsPublicationsT_datePubYColHead'] = ['datePubY','INTEGER']
tcols['musCompsPublicationsT_datePubMColHead'] = ['datePubM','INTEGER']
tcols['musCompsPublicationsT_datePubDColHead'] = ['datePubD','INTEGER']
tcols['musCompsPublicationsT_publisherCityColHead'] = ['publisherCity',f'INTEGER REFERENCES {t["placesTableName"]}(id)']
tcols['musCompsPublicationsT_voteValColHead'] = ['voteVal','INTEGER DEFAULT 0']

#musCompsWorkEndedDatesTableName = 'musCompsWorkEndedDatesT'	#b musCompsWorkEndedDatesT
tcols['musCompsWorkEndedDatesT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['musCompsWorkEndedDatesT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsWorkEndedDatesT_musCompIdColHead'] = ['musCompId',f'INTEGER NOT NULL REFERENCES {t["musCompsTableName"]}(id)']
tcols['musCompsWorkEndedDatesT_dateWorkEndedYgrColHead'] = ['dateWorkEndedYgr','INTEGER']
tcols['musCompsWorkEndedDatesT_dateWorkEndedMgrColHead'] = ['dateWorkEndedMgr','INTEGER']
tcols['musCompsWorkEndedDatesT_dateWorkEndedDgrColHead'] = ['dateWorkEndedDgr','INTEGER']
tcols['musCompsWorkEndedDatesT_voteValColHead'] = ['voteVal','INTEGER DEFAULT 0']

#musCompsWorkStartedDatesTableName = 'musCompsWorkStartedDatesT'	#b musCompsWorkStartedDatesT
tcols['musCompsWorkStartedDatesT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['musCompsWorkStartedDatesT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['musCompsWorkStartedDatesT_musCompIdColHead'] = ['musCompId',f'INTEGER NOT NULL REFERENCES {t["musCompsTableName"]}(id)']
tcols['musCompsWorkStartedDatesT_dateWorkStartedYgrColHead'] = ['dateWorkStartedYgr','INTEGER']
tcols['musCompsWorkStartedDatesT_dateWorkStartedMgrColHead'] = ['dateWorkStartedMgr','INTEGER']
tcols['musCompsWorkStartedDatesT_dateWorkStartedDgrColHead'] = ['dateWorkStartedDgr','INTEGER']
tcols['musCompsWorkStartedDatesT_voteValColHead'] = ['voteVal','INTEGER DEFAULT 0']

#t['occupationsTableName'] = 'occupationsT'	#b occupationsT
tcols['occupationsT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['occupationsT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['occupationsT_wikiPageNameOrLikeColHead'] = ['wikiPageNameOrLike',f'TEXT NOT NULL UNIQUE']
tcols['occupationsT_voteValColHead'] = ['voteVal',f' INTEGER DEFAULT 0']
tcols['occupationsT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleTableName = 'peopleT'	#b peopleT
tcols['peopleT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleT_wikiPageNameOrLikeColHead'] = ['wikiPageNameOrLike',f'TEXT NOT NULL UNIQUE']
tcols['peopleT_voteValColHead'] = ['voteVal',f'INTEGER']
tcols['peopleT_useThisColHead'] = ['useThis',f'INTEGER']

#dobTableName = 'dobT'	#b dobT
tcols['peopleDobT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleDobT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleDobT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleDobT_dobFlagColHead'] = ['dobFlag',f'TEXT']
tcols['peopleDobT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER','DOB-Y']
tcols['peopleDobT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER','M']
tcols['peopleDobT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER','D']
tcols['peopleDobT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleDobT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleDobT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleDobT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleDobT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['peopleDobT_useThisColHead'] = ['useThis',f'INTEGER']

#dodTableName = 'dodT'	#b dodT
tcols['peopleDodT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleDodT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleDodT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleDodT_dodFlagColHead'] = ['dodFlag',f'TEXT']
tcols['peopleDodT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER','DOD-Y']
tcols['peopleDodT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER','M']
tcols['peopleDodT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER','D']
tcols['peopleDodT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleDodT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleDodT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleDodT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleDodT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['peopleDodT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleGendersTableName = 'peopleGendersT'	#b peopleGendersT
tcols['peopleGendersT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleGendersT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleGendersT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleGendersT_assignedGenderValColHead'] = ['assignedGenderVal',f'TEXT','Gend.']
tcols['peopleGendersT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['peopleGendersT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['peopleGendersT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['peopleGendersT_startedStoppedColHead'] = ['startedStopped',f'INTEGER']
tcols['peopleGendersT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleGendersT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleGendersT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleGendersT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleGendersT_voteValColHead'] = ['voteVal',f' INTEGER DEFAULT 0']
tcols['peopleGendersT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleMetTableName =
tcols['peopleMetT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleMetT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleMetT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleMetT_relationDescrColHead'] = ['relationDescr',f'TEXT']
tcols['peopleMetT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['peopleMetT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['peopleMetT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['peopleMetT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleMetT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleMetT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleMetT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleMetT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['peopleMetT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleNamesFmlEngTableName = 'peopleNamesFmlEngT'	#b peopleNamesFmlEngT
tcols['peopleNamesFmlEngT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleNamesFmlEngT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleNamesFmlEngT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleNamesFmlEngT_fstNameColHead'] = ['fstName',f'TEXT','First']
tcols['peopleNamesFmlEngT_midNamesColHead'] = ['midNames',f'TEXT']
tcols['peopleNamesFmlEngT_lstNameColHead'] = ['lstName',f'TEXT','Last/First Names-Last']
tcols['peopleNamesFmlEngT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['peopleNamesFmlEngT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['peopleNamesFmlEngT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['peopleNamesFmlEngT_startedStoppedColHead'] = ['startedStopped',f'INTEGER']
tcols['peopleNamesFmlEngT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleNamesFmlEngT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleNamesFmlEngT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleNamesFmlEngT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleNamesFmlEngT_voteValColHead'] = ['voteVal',f' INTEGER DEFAULT 0']
tcols['peopleNamesFmlEngT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleNamesFullEngTableName = 'peopleNamesFullEngT'	#b peopleNamesFullEngT
tcols['peopleNamesFullEngT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleNamesFullEngT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleNamesFullEngT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleNamesFullEngT_fullNameEngColHead'] = ['fullNameEng',f'TEXT', 'Full Name (Eng)']
tcols['peopleNamesFullEngT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['peopleNamesFullEngT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['peopleNamesFullEngT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['peopleNamesFullEngT_startedStoppedColHead'] = ['startedStopped',f'INTEGER']
tcols['peopleNamesFullEngT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleNamesFullEngT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleNamesFullEngT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleNamesFullEngT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleNamesFullEngT_voteValColHead'] = ['voteVal',f' INTEGER DEFAULT 0']
tcols['peopleNamesFullEngT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleNamesFullOrigLangTableName = 'peopleNamesFullOrigLangT'	#b peopleNamesFullOrigLangT
tcols['peopleNamesFullBirthDocT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleNamesFullBirthDocT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleNamesFullBirthDocT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleNamesFullBirthDocT_fullNameBirthDocColHead'] = ['fullNameBirthDoc',f'TEXT','Full Name (Birth Doc.)']
tcols['peopleNamesFullBirthDocT_voteValColHead'] = ['voteVal',f' INTEGER DEFAULT 0']
tcols['peopleNamesFullBirthDocT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleNamesPseudonymsTableName = 'peopleNamesPseudonymsT'	#b peopleNamesPseudonymsT
tcols['peopleNamesPseudonymsT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleNamesPseudonymsT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleNamesPseudonymsT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleNamesPseudonymsT_pseudonymEngColHead'] = ['pseudonymEng',f'TEXT']
tcols['peopleNamesPseudonymsT_pseudonymOrigLangColHead'] = ['pseudonymOrigLang',f'TEXT']
tcols['peopleNamesPseudonymsT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['peopleNamesPseudonymsT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['peopleNamesPseudonymsT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['peopleNamesPseudonymsT_firstUsedColHead'] = ['firstUsed',f'INTEGER']
tcols['peopleNamesPseudonymsT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleNamesPseudonymsT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleNamesPseudonymsT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleNamesPseudonymsT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleNamesPseudonymsT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['peopleNamesPseudonymsT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleOccupationsTableName = 'peopleOccupationsT'	#b peopleOccupationsT
tcols['peopleOccupationsT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleOccupationsT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleOccupationsT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleOccupationsT_occupationIdColHead'] = ['occupationId',f'INTEGER NOT NULL REFERENCES occupationsT(id)']
tcols['peopleOccupationsT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['peopleOccupationsT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['peopleOccupationsT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['peopleOccupationsT_startedStoppedColHead'] = ['startedStopped',f'INTEGER']
tcols['peopleOccupationsT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleOccupationsT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleOccupationsT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleOccupationsT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleOccupationsT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['peopleOccupationsT_useThisColHead'] = ['useThis',f'INTEGER']

#peopleTeachersTableName = 'peopleTeachersT'	#b peopleTeachersT
tcols['peopleTeachersT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['peopleTeachersT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['peopleTeachersT_personIdColHead'] = ['personId',f'INTEGER NOT NULL REFERENCES peopleT(id)']
tcols['peopleTeachersT_teacherIdColHead'] = ['teacherId',f'INTEGER NOT NULL REFERENCES peopleT(id) ']
tcols['peopleTeachersT_subjectTaughtColHead'] = ['subjectTaught',f'TEXT']
tcols['peopleTeachersT_startedStoppedColHead'] = ['startedStopped',f'INTEGER']
tcols['peopleTeachersT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['peopleTeachersT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['peopleTeachersT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['peopleTeachersT_placeIdColHead'] = ['placeId',f'INTEGER REFERENCES placesT(id)']
tcols['peopleTeachersT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['peopleTeachersT_useThisColHead'] = ['useThis',f'INTEGER']

#placesTableName = 'placesT'	#b placesT
tcols['placesT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['placesT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['placesT_wikiPageNameOrLikeColHead'] = ['wikiPageNameOrLike',f'TEXT NOT NULL UNIQUE']
tcols['placesT_voteValColHead'] = ['voteVal',f' INTEGER DEFAULT 0']
tcols['placesT_useThisColHead'] = ['useThis',f'INTEGER']

#placesNamesEngTableName = 'placesNamesEngT'	#b placesNamesEngT
tcols['placesNamesEngT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['placesNamesEngT_refIdColHead'] = ['refId',f'INTEGER NOT NULL REFERENCES {t["refsTableName"]}(id)']
tcols['placesNamesEngT_placeIdColHead'] = ['placeId',f'INTEGER NOT NULL REFERENCES placesT(id)']
tcols['placesNamesEngT_placeNameColHead'] = ['placeNameEng',f'TEXT']
tcols['placesNamesEngT_countryNameColHead'] = ['countryName',f'TEXT']
tcols['placesNamesEngT_evtTimeYgrColHead'] = ['evtTimeYgr',f'INTEGER']
tcols['placesNamesEngT_evtTimeMgrColHead'] = ['evtTimeMgr',f'INTEGER']
tcols['placesNamesEngT_evtTimeDgrColHead'] = ['evtTimeDgr',f'INTEGER']
tcols['placesNamesEngT_startedStoppedColHead'] = ['startedStopped',f'INTEGER']
tcols['placesNamesEngT_relEvtIdColHead'] = ['relEvtId',f'INTEGER']
tcols['placesNamesEngT_relEvtIdTableIdColHead'] = ['relEvtIdTableId',f'INTEGER REFERENCES tableNamesT(id)']
tcols['placesNamesEngT_relEvtTimeRelationColHead'] = ['relEvtTimeRelation',f'INTEGER']
tcols['placesNamesEngT_voteValColHead'] = ['voteVal',f'INTEGER DEFAULT 0']
tcols['placesNamesEngT_useThisColHead'] = ['useThis',f'INTEGER']

#refsTableName = 'refsT'	#b refsT
# see below for total url
tcols['refsT_addedByUsernameColHead'] = ['addedByUsername','TEXT NOT NULL']
tcols['refsT_urlRootIdColHead'] = ['urlRootId','INTEGER']
tcols['refsT_urlMainColHead'] = ['urlMain','TEXT NOT NULL']
tcols['refsT_urlSuffixIdColHead'] = ['urlSuffixId','INTEGER']
tcols['refsT_urlSuffixValColHead'] = ['urlSuffixVal','TEXT']
tcols['refsT_timeAccessedColHead'] = ['timeAccessed','INTEGER']
tcols['refsT_nonUrlRefColHead'] = ['nonUrlRef','TEXT']
tcols['refsT_voteValColHead'] = ['voteVal',' INTEGER DEFAULT 0']

tcols['tableNamesT_addedByUsernameColHead'] = ['addedByUsername',f'TEXT NOT NULL']
tcols['tableNamesT_tableIdColHead'] = ['tableId',f'INTEGER NOT NULL UNIQUE']
tcols['tableNamesT_tableNameColHead'] = ['tableName',f'TEXT NOT NULL UNIQUE']

#urlRootsTableName = "urlRootsT"
tcols['urlRootsT_urlRootColHead'] = ['urlRoot','TEXT UNIQUE NOT NULL']
tcols['urlRootsT_test1ColHead'] = ['test1','TEXT']
tcols['urlRootsT_test2ColHead'] = ['test2','TEXT']
tcols['urlRootsT_test3ColHead'] = ['test3','TEXT']

#urlSuffixesTableName = "urlSuffixesT"
tcols['urlSuffixesT_urlSuffixColHead'] = ['urlSuffix','TEXT UNIQUE NOT NULL']

#usersTableName = "users"
tcols['usersT_usernameColHead'] = ['username',f'TEXT NOT NULL']
tcols['usersT_hashColHead'] = ['hash',f'TEXT NOT NULL']
tcols['usersT_cashColHead'] = ['cash',f'NUMERIC NOT NULL DEFAULT 10000.00']

#votesTableName = 'votesT'	#b votesT
tcols['votesT_usernameIdColHead'] = ['usernameId',f'INTEGER NOT NULL REFERENCES {t["usersTableName"]}(id)']
tcols['votesT_voteValColHead'] = ['voteVal',f'INTEGER NOT NULL']
tcols['votesT_disputeIdColHead'] = ['disputeId',f'INTEGER NOT NULL REFERENCES {t["disputesTableName"]}(id)']
tcols['votesT_disputeValueVoteIdxListColHead'] = ['disputeValueVoteIdxList','INTEGER']
tcols['votesT_timeVotedColHead'] = ['timeVoted','INTEGER']


#search cols that are combinations of the above table columns
rcols['refsT_urlColHead'] = ['url']


##############################################################################################################
# List of user generated csv columns generated by Webscraping (or manually) and used to populate the db tables
# 20240707_1715: need to be updated after changes to the code
ucols = {}
ucols['uRefStringColHead'] = ['refString']
ucols['uFstNameColHead'] = ['fstName']
ucols['uMidNamesColHead'] = ['midNames']
ucols['uLstNameColHead'] = ['lstName']
ucols['uFullNameEngColHead'] = ['fullName']
ucols['uFullNameOrigLangColHead'] = ['origLangName']
ucols['uCurrGenderColHead'] = ['currGender']
ucols['uDobYgrColHead'] = ['dobYgr']
ucols['uDobMgrColHead'] = ['dobMgr']
ucols['uDobDgrColHead'] = ['dobDgr']
ucols['uDobFlagColHead'] = ['dobFlag']


# relationship for html field names and data tables
# e.g. dob table + place's english name column from the table linked to from "placesT" will give us
#       0) the name of the english names subtable
#       1) name of the relating column (placeId) shared by the dob table and the english names subtable
#       2) The name of the relating table 1) points to - placesT
#       3) marker that helps to keep track of what has been added to the leftJoinCmdStr in GetDbDataFromSearch

tableRelsDictAlreadyJoinedTNameIdx = 0
tableRelsDictSharedIdsColNameIdx = 1
tableRelsDictJoinNewTNameIdx = 2
tableRelsDictDataTNameIdx = tableRelsDictJoinNewTNameIdx
tableRelsDictHtmlColNameIdx = 3
tableRelsDictTableAsNameIdx = 4
tableRelsDictSharedIdsColNameNewTableIdx = 5
tableRelsDict = {
    t['peopleDobTableName'] + "_" + tcols['peopleDobT_dobFlagColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDobTableName'],
         'DOB Flag*',
         t['peopleDobTableName'], ''],
    t['peopleDobTableName'] + "_" + tcols['peopleDobT_evtTimeYgrColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDobTableName'],
         'DOB-Y',
         t['peopleDobTableName'], ''],
    t['peopleDobTableName'] + "_" + tcols['peopleDobT_evtTimeMgrColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDobTableName'],
         'M',
         t['peopleDobTableName'], ''],
    t['peopleDobTableName'] + "_" + tcols['peopleDobT_evtTimeDgrColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDobTableName'],
         'D',
         t['peopleDobTableName'], ''],
    t['peopleDobTableName'] + "_" + tcols['placesNamesEngT_placeNameColHead'][0]: \
        [t['peopleDobTableName'],
         tcols['placesNamesEngT_placeIdColHead'][0],
         t['placesNamesEngTableName'],
         'POB-City/Country Name (Eng)',
         t['peopleDobTableName'] + "$" + t['placesNamesEngTableName'], ''],
    t['peopleDodTableName'] + "_" + tcols['peopleDodT_dodFlagColHead'][0]:
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDodTableName'],
         'DOD Flag*',
         t['peopleDodTableName'], ''],
    t['peopleDodTableName'] + "_" + tcols['peopleDodT_evtTimeYgrColHead'][0]:
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDodTableName'],
         'DOD-Y',
         t['peopleDodTableName'], ''],
    t['peopleDodTableName'] + "_" + tcols['peopleDodT_evtTimeMgrColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDodTableName'],
         'M',
         t['peopleDodTableName'], ''],
    t['peopleDodTableName'] + "_" + tcols['peopleDodT_evtTimeDgrColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleDodTableName'],
         'D',
         t['peopleDodTableName'], ''],
    t['peopleDodTableName'] + "_" + tcols['placesNamesEngT_placeNameColHead'][0]: \
        [t['peopleDodTableName'],
         tcols['placesNamesEngT_placeIdColHead'][0],
         t['placesNamesEngTableName'],
         'POD-City/Country Name (Eng)',
         t['peopleDodTableName'] + "$" + t['placesNamesEngTableName'], ''],
    t['peopleGendersTableName'] + "_" + tcols['peopleGendersT_assignedGenderValColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleGendersTableName'],
         'Gend.',
         t['peopleGendersTableName'], ''],
    t['peopleNamesFmlEngTableName'] + "_" + tcols['peopleNamesFmlEngT_lstNameColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleNamesFmlEngTableName'],
         'Last/First Names-Last',
         t['peopleNamesFmlEngTableName'], ''],
    t['peopleNamesFmlEngTableName'] + "_" + tcols['peopleNamesFmlEngT_fstNameColHead'][0]: \
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleNamesFmlEngTableName'],
         'First',
         t['peopleNamesFmlEngTableName'], ''],
    t['peopleNamesFmlEngTableName'] + "_" + rcols['refsT_urlColHead'][0]: #references for Fml table entries
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_refIdColHead'][0],
         t['refsTableName'],
         'Ref.',
         t['peopleNamesFmlEngTableName']+ "$" + t['refsTableName'], 'id'],
    t['peopleNamesFullEngTableName'] + "_" + tcols['peopleNamesFullEngT_fullNameEngColHead'][0]:
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleNamesFullEngTableName'],
         'Full Name (Eng.)',
         t['peopleNamesFullEngTableName'], ''],
    t['peopleNamesFullBirthDocTableName'] + "_" + tcols['peopleNamesFullBirthDocT_fullNameBirthDocColHead'][0]:
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleNamesFullBirthDocTableName'],
          'Name in original B.Cert',
          t['peopleNamesFullBirthDocTableName'], ''],
    t['peopleNamesPseudonymsTableName'] + "_" + tcols['peopleNamesPseudonymsT_pseudonymEngColHead'][0]:
        [t['peopleNamesFmlEngTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['peopleNamesPseudonymsTableName'],
          'Pseudon.',
          t['peopleNamesPseudonymsTableName'], ''],

        # NEED TO FIX OCCUPATIONS
    t['peopleOccupationsTableName'] + "_" + tcols['occupationsT_wikiPageNameOrLikeColHead'][0]:
        [t['peopleOccupationsTableName'],
         tcols['peopleNamesFmlEngT_personIdColHead'][0],
         t['occupationsTableName'],

         t['occupationsTableName']]

}


# the dictionary below with lists of table name values became necessary when I was trying to finish coding
# the GetDbDataFromSearch function where I needed to know how to interrlate main tables (like peopleT and its potentially many subtables)
# I needed to copy certain values from one table to another that I just created
sourceTableName = 'dobT'
targetTableName = 'peopleDobT'
tableCopyMap = {
    'id':                                                 'id',
    tcols['peopleDobT_addedByUsernameColHead'][0]:        tcols['peopleDobT_addedByUsernameColHead'][0],
    tcols['peopleDobT_refIdColHead'][0]:                  tcols['peopleDobT_refIdColHead'][0],
    tcols['peopleDobT_personIdColHead'][0]:               tcols['peopleDobT_personIdColHead'][0],
    tcols['peopleDobT_dobFlagColHead'][0]:                tcols['peopleDobT_dobFlagColHead'][0],
    ucols['uDobYgrColHead'][0]:                           tcols['peopleDobT_evtTimeYgrColHead'][0],
    ucols['uDobMgrColHead'][0]:                           tcols['peopleDobT_evtTimeMgrColHead'][0],
    ucols['uDobDgrColHead'][0]:                           tcols['peopleDobT_evtTimeDgrColHead'][0],
    tcols['peopleDobT_voteValColHead'][0]:                tcols['peopleDobT_voteValColHead'][0]
}


## these variables are used by insert and updateDbDataFromHtml functions
numRecordsUpdated = 0
recordsUpdatedMessage = ""
recordsUpdatedDetails = ""
numRecordsInserted = 0
recordsInsertedMessage = ""
recordsInsertedDetails = ""

# Below values describe the CSV columns that contain the incoming data
# They will be used in multiple different tables
refTableRefColHead = "ref1"
refTableTimeColHead = "timeAccessed"
refTableIdColHead = 'wikiPageName oldid' # only used for CSV


setValsDidNotInsertDueToDuplicate = 1
refCsvBlankValueSkip = 1

