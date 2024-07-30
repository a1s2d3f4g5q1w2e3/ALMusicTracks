# utils used by multiple py projects (webScraping, dbManagement etc)
import csv
import inspect
import io
import os
import pandas

currNumTabs = 0


def tabs(delta=0):
    global currNumTabs
    currNumTabs = currNumTabs + delta
    currNumTabs = 0 if currNumTabs < 0 else currNumTabs

    return "\t" * currNumTabs #+ str(currNumTabs)


def doprint(f, something=""):

    if not f:
        print(str(something))

    else:
        print(str(f) + str(something))

    return


def noprint(f, something=""):
    something=""

    return ""


def NMessage(msg, logFile=None, logOption=""):

    return


def YMessage(msg, logFile=None, logOption=""):
    msg = f"{tabs()}{msg}"
    logFile.write(f"{msg}\n") if logFile and logOption else ""
    doprint("", msg) if logOption else ""

    return


def GetDictFromDictList(dictList, keyToFind, keyToFindVal, logFile=None, logOption=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(dictList={str(dictList)}, nameOfKey={keyToFind}, nameOfKeyVal={str(keyToFindVal)}, logFile={logFile}, logOption={logOption}):" #function name
    YMessage(f"STARTED {f}", logFile, logOption)

    returnDict = None
    oneDictGotten = False
    for dict in dictList:

        if dict[keyToFind] == keyToFindVal:
            returnDict = dict
            oneDictGotten = True
            NMessage(f"dict={dict}")

    NMessage(f"dictList={dictList}")

    if not oneDictGotten:
        returnDict = "DICTNOTFOUND"

    YMessage(f"ENDED {f}", logFile, logOption)
    tabs(-1)

    return returnDict


def GetDictListValue(dictList, keyToFind, keyToFindVal, keyToGet, logFile=None, logOption=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(dictList={str(dictList)}, nameOfKey={keyToFind}, nameOfKeyVal={str(keyToFindVal)}, keyToSet={keyToGet}, logoptions...):" #function name
    YMessage(f"STARTED {f}", logFile, logOption)

    returnVal = None
    oneValueGotten = False
    for dict in dictList:

        if dict[keyToFind] == keyToFindVal:
            returnVal = dict[keyToGet]
            oneValueGotten = True
            NMessage(f"dict={dict}")

    NMessage(f"dictList={dictList}")

    if not oneValueGotten:
        returnVal = "KEYNOTFOUND"

    YMessage(f"ENDED {f}", logFile, logOption)
    tabs(-1)

    return returnVal


def OpenAndGetDictFromCsv(pathToCsv, openType, logFile, logOption=False):

    csvFile = pandas.read_csv(pathToCsv, keep_default_na=False) # trying out pandas, because I wasn't able to pass DictReader object to other functions
    # Thanks to this page, I figured out how to keep blanks as blanks and not have them converted to "nan":
    # https://stackoverflow.com/questions/10867028/get-pandas-read-csv-to-read-empty-values-as-empty-string-instead-of-nan

    return csvFile
    exit()
    csvFile = OpenCsvFileForReading(pathToCsv, openType, logFile, logOption)
    with open(pathToCsv) as cool_csv_file:
            cool_csv_lines = cool_csv_file.readlines()
    returnVal = ReadInOpenCsvFileAsDict(cool_csv_lines, logFile, LOG)
    csvFile.close()
    return returnVal


def OpenCsvFileForReading(fname, openMode = "r", logFile=None, logOption=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(fname={fname}, openMode={openMode}):" #function name
    YMessage(f"STARTED {f}", logFile, logOption)

    if os.path.isfile(fname): # first check that the file exists
        NMessage(f"file {fname} exists", logFile, logOption)
        YMessage(f"Will try to open {fname}")

        try:
            YMessage(f"ENDED {f}", logFile, logOption)
            tabs(-1)
            return open(fname, openMode)

        except:
            print(f"couldn't open {fname} for reading with open()")
            exit()

    else:
        print(f"couldn't open {fname} for reading because it doesn't seem to exist")
        exit()


def OpenUniqueFileForOutput(fname, openMode="w", logFile=None, logOption=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(fname={fname}, openMode={openMode}):" #function name
    YMessage(f"STARTED {f}")

    file = None
    index = 1
    maxFileNum = 10
    newName= ""

    if os.path.isfile(fname): # first check if the file already exists
        YMessage(f"{fname} exists")

        for c in range(index, maxFileNum + 1):
            lastDotPos = fname.rfind(".")
            fnameName = fname[:lastDotPos]
            fnameExt = fname[lastDotPos:]
            newName = f'{fnameName}{str(c)}{fnameExt}'

            if not os.path.isfile(newName):
                print(f"Will try to open {newName}")

                try:
                    YMessage(f"ENDED {f}", logFile, logOption)
                    tabs(-1)

                    return open(newName, openMode)

                except:
                    print(f"couldn't open {newName} for writing")
                    exit()

    if not file:
        print(f"couldn't find a unique file name to use. Last tried - {newName}")
        exit()

    YMessage(f"ENDED {f}", logFile, logOption)
    tabs(-1)

    return file


def ReadInOpenCsvFileAsDict(csvfileLines, logFile=None, logOption=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(csvfileLines={csvfileLines}...+logfile options):" #function name
    YMessage(f"STARTED {f}", logFile, logOption)

    ''' # had to redesign this function because I discovered that DictReader objects cannot be passed to functions. Something to do with CSV file needing to stay open (well, I never closed it, but still)
    if not isinstance(csvfile, io.TextIOBase):
        YMessage(f"csvfile parameter is not an open text file. Quitting", logFile, logOption)
        exit()
    '''

    try:
        YMessage(f"ENDED {f}", logFile, logOption)
        tabs(-1)
        #return csv.reader(csvfile)
        return csv.DictReader(csvfileLines)

    except:
        YMessage(f"tried to read in csvfileLines using csv.DictReader but failed for some reason")
        tabs(-1)
        exit()


def SetDictListValue(dictList, keyToFind, keyToFindVal, keyToSet, valToSetTo, logFile=None, logOption=False):
    tabs(1)
    f = inspect.stack()[0][3] + f"(dictList={str(dictList)}, nameOfKey={keyToFind}, nameOfKeyVal={str(keyToFindVal)}, keyToSet={keyToSet}, valToSetTo={valToSetTo}, logFile={logFile}, logOption={logOption}):" #function name
    YMessage(f"STARTED {f}", logFile, logOption)

    returnVal = 0
    oneValueSet = False

    for dict in dictList:

        if dict[keyToFind] == keyToFindVal:
            dict[keyToSet] = valToSetTo
            oneValueSet = True
            NMessage(f"dict={dict}")

    NMessage(f"dictList={dictList}")

    if not oneValueSet:
        returnVal = -1

    YMessage(f"ENDED {f}", logFile, logOption)
    tabs(-1)

    return returnVal


def WriteStringToFile(file, mystring):
    tabs(1)
    strlen = len(mystring)
    response = 0

    if strlen == 0:
        tabs(-1)

        return 0

    response = file.write(mystring)

    if response != strlen:
        print(f"For some reason, I wasn't able to write to {file.name} all the characters of the following string ({strlen}):\n ({mystring})")
        tabs(-1)
        exit()

    tabs(-1)

    return 0
