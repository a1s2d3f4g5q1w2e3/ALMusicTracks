# this python file helps the "main module" webScraping.py
from wikihelpers import *
import globalVars as g
import sys, os
import time

sys.path.append(os.path.abspath(os.path.join(g.pathToUtils, '')))
from utils.utils import *


# for Wikipedia summary pages (such as, for instance, https://en.wikipedia.org/wiki/List_of_composers_by_name)
# this function is called with a dict argument that describes the parameters of the input data (see static/listOfResources.csv)
def ExtractWikipediaData( dict ):
    f = inspect.stack()[0][3] + f"(dict={str(dict)}):" #function name
    tabs(1)
    YMessage(f"STA {f}", logOption=LOG)

    returnValue = 0

    ##############
    #errorchecking
    if not dict["url"]:
        YMessage(f"No url key in dict\n", logOption=ERRORLOG)
        tabs(-1)

        return -1

    if not "wikipedia" in dict["url"]:
        YMessage(f"No wikipedia url in dict\n", logOption=ERRORLOG)
        tabs(-1)

        return -1

    if any(ele == [] for ele in list(dict.values())): # forgot where I got this command from.
                                                      # if incoming dict is corrupted and missing data, we stop
        YMessage(f"missing a value in dict->{str(dict)}\n", logOption=ERRORLOG)
        tabs(-1)

        return -1
    # end of error checking
    #######################

    if dict['type'] == "summaryPage":
        outputFilePath1 = tempDirPath + dict["tempSummaryCsv"]
            # outputFilePath1 is a temporary file that holds just the necessary wikitext from a wikipedia "summary page"
            # e.g. https://en.wikipedia.org/wiki/List_of_composers_by_name
        count = ExtractDataFromWikiSummaryPage(dict["url"], outputFilePath1, updateOutputFile=0)
                # updateOutputFile=0 allows me to bypass this step if a file is already created
                # and I want to focus on debugging the later stage of my code sooner
        YMessage(f"ExtractDataFromWikiSummaryPage returned count={str(count)}\n", logOption=LOG)
            # at this point, to process roughly 5000 lines that I have been working with in my first summary page,
            # i.e. https://en.wikipedia.org/w/index.php?title=List_of_composers_by_name&action=edit
            # takes approximatel 0.5 seconds (this is including the output of debugging data to the console)

        if -1 == count: # something went wrong during ExtractDAtaFromWikiSummaryPage
            YMessage(f"count={str(count)}, therefore returning -1.\n", logOption=ERRORLOG)
            YMessage(f"END {f}\n", logOption=LOG)
            tabs(-1)

            return -1

        count = ExtractDataFromWikiPersonPage(sourceFile=outputFilePath1, outputNameDict=dict, count=count)
        YMessage(f"ExtractDataFromWikiPersonPage returned count={str(count)}\n", logOption=LOG)

        if -1 == count:
            YMessage(f"count={str(count)}, therefore returning -1.\n", logOption=ERRORLOG)
            YMessage(f"END {f}\n", logOption=LOG)
            tabs(-1)

            return -1

    # potential elif goes here for other types of wikipedia pages

    YMessage(f"returning returnValue=={returnValue}\n", logOption=LOG)
    YMessage(f"END {f}\n", logOption=LOG)
    tabs(-1)

    return returnValue


def ExtractDataFromWikiSummaryPage(wikiUrl, outputFilePath, updateOutputFile=0):
    # The job of this function is to use the wiki summary page's (wikiUrl)
    # wikitext to figure out where to go to scrape data from individual wikipedia pages
    f = inspect.stack()[0][3] + f"(wikiUrl={wikiUrl}, outputFilePath=={outputFilePath}, updateOutputFile={updateOutputFile}):" #function name
    tabs(1)
    YMessage(f"STA {f}", logOption=LOG)

    if updateOutputFile or not os.path.isfile(outputFilePath): # even if the caller specified updateOutputFile=0, we would override this, if no file
        YMessage(f"trying to open outputFile {outputFilePath}\n", logOption=LOG)
        outputFile = open(outputFilePath, "w")

    else:
        with open(outputFilePath, 'r') as fp: # from https://www.geeksforgeeks.org/count-number-of-lines-in-a-text-file-in-python/
            numlines = len(fp.readlines())
            YMessage(f"returning numlines({numlines}) from {outputFilePath} without updating it first", logOption=LOG)
            YMessage(f"END {f}\n", logOption=LOG)
            tabs(-1)

            return numlines

    if not "wikipedia" in wikiUrl:
        YMessage(f"no 'Wikipedia' in wikiUrl(=={wikiUrl}). Returning -1\n", logOption=ERRORLOG)
        YMessage(f"END {f}\n", logOption=LOG)
        tabs(-1)

        return -1

    wikiPageName = wikiUrl.rpartition('/')[-1] #extract the substring after the last "/" character (https://stackoverflow.com/questions/24986504/find-the-last-substring-after-a-character)
    YMessage(f"wikiPageName=={wikiPageName}", logOption=LOG)

    content = FetchWikipediaPage(wikiPageName) #getting the wiki text of the summary page here

    if not content:
        YMessage(f"FAILED to get content from FetchWikipediaPage(wikiPageName={wikiPageName})...returning\n", logOption=ERRORLOG)
        tabs(-1)
        return -1

    """Split content by newline"""
    pageRows = content.splitlines()

    breakStringsList = ["==See also==", "==References==", "==External links=="]
    c = 0
    NMessage(f"pageRows={pageRows}", logOption=LOG)
        # pageRows is a list containing every line of the {wikiPageName} wikipedia page
        # This are mostly manually added wikilinks of the type:
        # *[[<wikipedia page name for a person><|optional user friendly name>]] <some more optional junk, usually life years>

    # so we now walk through every row and create an intermediate "tempSummary" file which filters out all the non-wiki-page related lines
    for row in pageRows:

        pageName = ''

        if row in breakStringsList: # If we got here, it's past the data that intrests us
            break

        YMessage(f"CALLING ExtractPageNameFromWikiRow(row={row}, log={g.logChoice})", logOption=LOG)
        pageName = ExtractPageNameFromWikiRow( row, g.logChoice )

        if pageName:
            updateRow = row.replace("\"", "\"\"") #have to double up the double-quotes in the wiki text so that CSV isn't confused whenever there are literal commas
            c = c + 1
            outputFile.write(f'{str(c)},"{updateRow}","{pageName}"\n') # having to put quotes around each item so that CSV reader isn't confused about literal commas

            if g.chooseTempSummaryRowForWiki >= (c + 0): # This allows me to work with a subset of people during debugging
                g.logChoice = True
                YMessage(f"row={row}\n", logOption=LOG)

    # end of for loop walking through every line of the "wiki summary page such as https://en.wikipedia.org/w/index.php?title=List_of_composers_by_name&action=edit"

    outputFile.close()
    tabs(-1)
    YMessage(f"END {f} RETURNING c={c}", logOption=LOG)

    return c


# this is called (by ExtractDataFromWikiSummaryPage) to process individual people by scraping data about them from the
# wikipedia pages about them - see details below
def ExtractDataFromWikiPersonPage(sourceFile, outputNameDict, count):
    f = inspect.stack()[0][3] + "(sourceFile=" + str(sourceFile) + ", outputNameDict=" + str(outputNameDict) + ", count=" + str(count) +  "):" #function name
    tabs(1)
    YMessage(f"STA {f}\n" , logOption=LOG)
        # walks through every single wikipedia page contained in sourceFile (e.g. temp/tempSummary.csv)
        # it fetches the wikitext from each such page and parses it in the attempt to extract useful information
        # e.g. First Name, Last Name, other names, birth date, etc. (see columns below)
        # saves this information to an output file

    returnCount = 0
    if count != 0:
        referenceCount = count

    if g.TESTING: # at this point, in my attempts to fine tune my scraping code I could detour to the "Testing" function
        YMessage(f"CALLING Testing(g.TEST_STRINGS)\n" , logOption=LOG)
        Testing(g.TEST_STRINGS)
        exit()

    YMessage(f"ATTEMPTING peopleFile = open(outputNameDict['personTableFileName], 'w') etc...\n" , logOption=LOG)
    peopleFile = OpenUniqueFileForOutput(g.tempDirPath+outputNameDict['peopleTableFileName'], "w")
                # this function makes sure to not overwrite any existing file I already have in that folder
                # and instead to create a uniquely named file by adding a number to the end of the main path
    YMessage(f"peopleFile={peopleFile}" , logOption=LOG)

    # We will now walk through the each wikipage name and attempt to extract data from that page
    with open(sourceFile, 'r') as csvfile: #https://remarkablemark.org/blog/2020/08/26/python-iterate-csv-rows/
        datareader = csv.reader(csvfile)

        #write header rows to output CSV files - NB More can be added in the future as I learn to collect more data
        WriteStringToFile(peopleFile, (
            f'refString,fstName,midNames,lstName,fullName,origLangName,currGender,dobYgr,dobMgr,dobDgr,dobFlag\r\n'
            )
        )

        # Starting the iteration loop here
        c = 0 # counting of the rows in tempSummary
              # this count doesn't directly correspond to the number of different people,
              # because some people are duplicated
              # e.g.    3006,"*[[Andrew Lloyd Webber]] (born 1948)","Andrew Lloyd Webber" AND
              #         4751,"*[[Andrew Lloyd Webber]] (born 1948)","Andrew Lloyd Webber"
              # (because whoever was editing the wikipedia page didn't know that Lloyd Webber is a double word last name and so entered it in the W section)
              #
              # However, the total count better match the number of rows in tempSummary file
        for row in datareader:
            c = c + 1
            g.currTempSummaryRow = c # keeping the global variable updated so any function can know

            personWikiName = row[g.testSummaryPersonNameIdx] # tempSummary.csv currently saves the name of the person (wikipedia page style in column 3)
            wikiPageName = personWikiName.replace(" ", "_") # typical wikipedia page names replaces spaces with underscore characters

            if c >= int(g.chooseTempSummaryRowForWiki):
                    # Again, this allows me to skip to the wikipage that I am interested in before I started outputting data
                YMessage(f"wikiPageName={wikiPageName}", logOption=LOG)

            g.logChoice = True
            if DEBUG and c <= (g.chooseTempSummaryRowForWiki - 1): # This skips the processing of all tempSummary rows up to g.chooseTempsSummaryRowForWiki
                g.logChoice = False # resets the above here just in case
                continue

            returnCount = returnCount + 1 # returnCount holds on the number of rows actually processed

            YMessage(f"CALLING FetchWikipediaPage(wikiPageName={wikiPageName})", logOption=LOG)
            content = FetchWikipediaPage(wikiPageName)
            NMessage(f"content={content}", logOption=LOG)
                # typical behavior is that content contains lots of wikitext at this point
                # corresponding to the current tempSummary row's (c or g.currTempSummaryRow) person

            # setting up some temporary variables that I will use later when writing strings
            # to the output file
            dobFlag = ""
            dobYgr = ""
            month = ""
            day = ""
            permUrl = ""

            # content might only contain a REDIRECT to another page
            # e.g. if the name is a pseudonym etc, e.g. "REDIRECT [[Michael Maybrick]]"
            if content:
                firstLineOfContent = content.partition('\n')[0]
                YMessage(f"firstLineOfContent={firstLineOfContent})", logOption=LOG)

                if "REDIRECT" in firstLineOfContent.upper(): # 20240709_1442: Adding .upper(), as some wikipedia pages write redirect as lowercase.
                                                             # There are some bits of code I am copying from the block above
                                                             # I have to anticipate that there could be a long line of "REDIRECT" pages, one pointing to the other,
                                                             # and I need to be able to "drill down" to the actual page, but for now it's this and that's that.
                    YMessage(f"CALLING ExtractPageNameFromWikiRow(firstLineOfContent={firstLineOfContent}, log={g.logChoice})\n", logOption=LOG)
                    personWikiName = ExtractPageNameFromWikiRow(firstLineOfContent, g.logChoice)
                        # ExtractPageNameFromWikiRow is supposed to be smart enough to recognize the string
                        # pattern (using regex) and
                    YMessage(f"In REDIRECT: personWikiName={personWikiName})\n", logOption=LOG)
                    wikiPageName = personWikiName.replace(" ", "_")
                    YMessage(f"CALLING FetchWikipediaPage(wikiPageName={wikiPageName}) \n", logOption=LOG)
                    content = FetchWikipediaPage(wikiPageName)
                # end of if dealing with a potential REDIRECT page

                permUrl = FetchWikipediaPermUrl(wikiPageName)
                    # this is important because I have decided to get the permanent address to each page that I am scraping for data.
                    # this is what I will stick inside my database instead of the url that will have changing data
                timeAccessed = int(time.time() * 1000)
                    # I am not sure if this is necessary now that I am showing the permanent link
                    # but I'll keep it around

                ##################################################################################
                # At this point, since we are only expecting the birthdate in the first paragraph,
                # *or in the infobox following the string birth_date
                # we will look for equal sign symbols ==<some words>==
                # after we encounter another such heading we cut content at that point.
                # That way we will extract only the first section of the wikitext (content)
                # and only feed that to the ExtractBirthDateFromBioText function
                YMessage(f"CALLING ExtractShortenedVersionOfContent(content={content[:100]}...) \n", logOption=LOG)
                content2 = ExtractShortenedVersionOfContent(content)

                year, month, day, context, dobFlag, match, startChar, endChar, calType = ExtractBirthDateFromBioText(content2, personWikiName)
                    # I am returning lots of pieces of data, but I might not use everything in the database for now

                if "f." == dobFlag:

                    if year:
                        dobYgr = int(year) - g.averageAgeOfAttainingFlourishingStatus # pretending that the person was roughly 25 when they became famous
                        dobFlag = "f->b"

                else:

                    if year:
                        dobYgr = year

            fstName, lstName = ExtractFstLstNames(personWikiName)
            midNames = "" # place holder for now
            fullName = personWikiName # This is often not correct, but before I improve my algorithm, it will use the Wikipedia page name, which is sometimes the full name
            origLangName = "" # place holder for now
            gender = "" # place holder for now. Will be filled with a function that looks for the amount of words "he/his/him" compared to "she/her/hers"
            dobMgr = month
            dobDgr = day

            # refString,fstName,midNames,lstName,fullName,origLangName,currGender,
            # dobFlag, dobYgr,dobMgr,dobDgr
            WriteStringToFile(peopleFile, ( # we write the entries into the main table, of course.
                f'"{permUrl}","{fstName}","{midNames}","{lstName}","{fullName}","{origLangName}","{gender}",'
                f'"{dobFlag}","{dobYgr}","{dobMgr}","{dobDgr}"\r\n'
                )
            )

            if (g.chooseTempSummaryRowForWiki + numPeopleAfterThisPerson - 1) < c and DEBUG == True:
                tabs(-1)
                return returnCount

    peopleFile.close()


    if referenceCount != returnCount:
        doprint(f, "referenceCount=" + str(referenceCount) + " and returnCount=" + str(returnCount))

    YMessage(f"RETURNING returnCount={returnCount}\n" )
    tabs(-1)

    return returnCount


def Test(cmdline):
    YMessage(f"{cmdline} numarg = {len(cmdline)}", logOption=LOG)
    numarg = len(cmdline) - 1

    if numarg > 0:

        if "test1" == cmdline[1]:
            s = "\""
            d = s.replace("\"", "\"\"")
            YMessage(f"s={s} d={d}", logOption=LOG)

            exit()

    else:

        return

    return
