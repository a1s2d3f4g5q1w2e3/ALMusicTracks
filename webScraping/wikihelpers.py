import globalVars as g
import inspect
import sys, os
import re # to be able to scrape wikipedia and other human text for specific content like birth dates (regular expressions)
import requests
from test import *
import jdcal

sys.path.append(os.path.abspath(os.path.join(g.pathToUtils, '')))
from utils.utils import *

DEBUG = g.DEBUG
LOG = g.LOG
ERRORLOG = g.ERRORLOG

dirname = g.dirname
tempDirPath = g.tempDirPath
chooseTempSummaryRowForWiki = g.chooseTempSummaryRowForWiki
WIKIPEDIA_API_URL = g.WIKIPEDIA_API_URL
headers = g.headers
numPeopleAfterThisPerson = g.numPeopleAfterThisPerson

# tabs() and doprint/YMessage functions are defined in utils now


def ExtractBirthDateFromBioText( bio_text, personName ):
    f = inspect.stack()[0][3] + f"(bio_text=<bio_text...not included due to size>, personName={personName}):" #function name
    tabs(1)
    YMessage(f"STA {f}\n", logOption=LOG)
    ##########################################################################################################
    # THIS IS A TOUGH ONE
    #
    # I need to parse the (typically) first 500 characters of the person wikipage's wikitext
    # and figure out which characters describe this person's birthdate.
    #
    # If this function is successful, the correct birthdate (as shown by the wikipedia text) is retrieved
    #
    # Regular expression patterns for different birth date formats are used.
    # I worked with chatGPT to come up with the initial regex strings until I (sort of) figured out
    # how regex works.
    #
    # Anything inside () is considered a "group" in regex and it is returned in a match.group(group_index)
    #
    # I definitely want my many date_formats to be matched as a group so I can return them with match = re.search()
    #
    # regex rules:
    # * following something e.g. a () group means that the group can happen many times over and over, but it actually could be absent also
    # + means the previous thing has to happen one or more times
    # \b "word boundary anchor": This means that r'\bat\b' matches 'at', 'at.', '(at)', and 'as at ay' but not 'attempt' or 'atlas'.
    #       The default word characters in Unicode (str) patterns are Unicode alphanumerics and the underscore, but this can be changed by using the ASCII flag.
    #       Word boundaries are determined by the current locale if the LOCALE flag is used.
    #       Note Inside a character range, \b represents the backspace character, for compatibility with Python’s string literals.
    # ? means - Causes the resulting RE to match 0 or 1 repetitions of the preceding RE. ab? will match either ‘a’ or ‘ab’. (ab* is the same but would also match abbbbb)
    # *?, +?, ??
    #   The '*', '+', and '?' quantifiers are all greedy; they match as much text as possible.
    #   Sometimes this behaviour isn’t desired; if the RE <.*> is matched against '<a> b <c>', it will match the entire string, and not just '<a>'.
    #   Adding ? after the quantifier makes it perform the match in non-greedy or minimal fashion; as few characters as possible will be matched.
    #   Using the RE <.*?> will match only '<a>'.
    # (?...) means - The first character after the '?' determines what the meaning and further syntax of the construct is.
    #   (?=...) Matches if ... matches next, but doesn’t consume any of the string. This is called a lookahead assertion.
    #           For example, Isaac (?=Asimov) will match 'Isaac ' only if it’s followed by 'Asimov'.
    #   (?!...) Matches if ... doesn’t match next. This is a negative lookahead assertion.
    #           For example, Isaac (?!Asimov) will match 'Isaac ' only if it’s not followed by 'Asimov'.
    #
    #personName = "Truid Aagesen" #for debugging (comment when launching in production mode)
    personFstName, personLstName = ExtractFstLstNames(personName)

    if ( "(" in personFstName or ")" in personFstName ) or ( ")" in personLstName or "(" in personLstName ):
        YMessage( tabs() + "personFstName or personLstName have parens:" + str(personFstName) + " " + personLstName, logOption=LOG)
        tabs(-1)

        return "", "", "", "", "", "", "", "", "" # skip

    valid_prefixes = [ \
        [ #1. Probably best to start with the most specific patterns, and if they yield nothing, move to less specific patterns
            r'b\.\s*', #BORN1 "b.<with or without spaces>" (indicating born followed by one of the date_formats below)
            r'born\s+', #BORN2 "born<with at least one space>" (indicating born followed by one of the date_formats below)
            r'born\s+on\s+', #BORN3 "born on<with at least one space>" (indicating born followed by one of the date_formats below)
            r'c\.\s*', #CIRCA1 "c.<with or without spaces>" (indicating circa, when date is approximate, followed by one of the date_formats below)
            r'ca\.\s*', #CIRCA2
            r'circa\s+', #CIRCA3
            r'f\.\s*', #FLOURISHED1 "f.<with or without spaces>" (indicating flourished, when birtdate is unknown, followed by one of the date_formats below)
            r'fl\.\s*', #FLOURISHED2
            r'flor\.\s*', #FLOURISHED3
            r'\[\[Floruit\|f\]\]\.\s*', #FLOURISHED4 "[[Floruit|f]].<with or without spaces>" (indicating flourished in a wiki markup way)
            r'\[\[Floruit\|fl\]\]\.\s*', #FLOURISHED5
            r'\[\[Floruit\|flor\]\]\.\s*', #FLOURISHED6
            fr'{personFstName}\s*{personLstName}\'\'\',?\s*\((?!\[|\{{)\s*\(', #PERSON1 current person's name followed by "'''<optional space>(" but must not be followed by "[" or "{" - i.e. immediately date string
                                                        # cases where "{personName}''' ("" is followed by one of the forbidden characters but eventually gets to a date string go into the 2nd attempt (valid_prefixes2 - or 3)
            #fr"Ella\s*Georgiyevna\s*Adayevskaya'''\s*\('''Ella\s*Adaïewsky'''\;\s*{{{{lang-ru\|Элла\s*\(Елизавета\)\s*Георгиевна\s*Адаевская}}}}\;\s*{{{{OldStyleDateDY\|",
            fr"{personFstName}[A-Za-z ]*{personLstName}.+?(?=OldStyleDateDY\|)[A-Za-z]*\|", #brought it in to deal with really long wiki text that ends with OldStyle
        ], \
        [ #2 \
            fr'{personFstName}\s*{personLstName}\'\'\',?\s*\(\{{\{{lang.*?\}}\}}\)\s*\(', # I need this to ignore everything until it meets another }}) string
            r'[Bb]irth\s*date\s*\|', # Can appear in an "Infobox" (birth date|<followed by YYYY|MM|DD>)
            r'[Bb]irth\s*date\s*and\s*age\s*\|', # Can appear in an "Infobox" (birth date|<followed by YYYY|MM|DD>)
            fr'birth_date\s*=\s*\{{\{{circa\|', # Can appear in an "Infobox" (birth date|<followed by YYYY|MM|DD>)
            fr'birth_date\s*=\s*', # Can appear in an "Infobox" (birth date|<followed by YYYY(|MM|DD>))
            fr'{personFstName}\s*{personLstName}\'\'\',?\s*\(\{{\{{circa\|',
            fr'{personFstName}\s*{personLstName}\'\'\',?\s*\(\s*', #PERSON1 current person's name followed by "'''<optional space>(" but must not be followed by "[" or "{" - i.e. immediately date string
            fr'{personFstName}[A-Za-z ]*{personLstName}\'\'\',?\s*\(', # Some names have other versions of the name related to the incoming name
            fr'{personFstName}[A-Za-z ]*{personLstName}[A-Za-z,\' ]*\'\'\',?\s*\(',
            fr'{personFstName}[A-Za-z ]*{personLstName}[A-Za-z,\' ]*\'\'\',?\s*\(\{{\{{.*?\}}\}}.?\s*', #Paul Abraham
            fr'birth\s*date\|.*?\|',
            fr'{personFstName}[A-Za-z ]*{personLstName}[A-Za-z,.\' ]*\'\'\',?\s*\(',
            #fr'Leslie Adams,\s*Jr\.\'\'\'\s*\(' # As I tried to add Leslie Adams situation here, i realized that something else in this long list of prefixes was overriding it, so moved it to 31
        ], \
        [ #3\
            fr'{personFstName}[A-Za-z ]*{personLstName}[A-Za-z,.\' ]*\(',
        ], \
        #[ #4
            #fr"{personFstName}[A-Za-z ]*{personLstName}.+?(?=Old)[A-Za-z]*\|", #brought it in to deal with really long wiki text that ends with OldStyle
           #fr"Ella\s*Georgiyevna\s*Adayevskaya'''\s*\('''Ella\s*Adaïewsky'''\;\s*{{{{lang-ru\|Элла\s*\(Елизавета\)\s*Георгиевна\s*Адаевская}}}}\;\s*{{{{OldStyleDateDY",

            #r"asdfghjkqwertyuizxcvbnm\sqwertyuiasdfghjkzxcvbnm\sy",
   #     ]
    ]

    regexMonths = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)" # a group of month strings used in date formats below
    charsThatCouldFollow = r"-)–,{\s}|"

    # Date formats
    date_formats = [
        [   #1
            fr'(\b\d{{1,2}},?\s+{regexMonths}[a-z]*,?\s+\d{{4}}\s*\b[{charsThatCouldFollow}])',  # e.g., "10 Apr, 1593" or 2 April, 1593-
            fr'(\b{regexMonths}[a-z]*\s+\d{{0,2}},?\s+\d{{4}}\s*[{charsThatCouldFollow}])',  # e.g., March 10, 1970 or March 10 1970
            fr'(\b{regexMonths}[a-z]*,?\s*\d{{4}})\s*[{charsThatCouldFollow}]',  # e.g., March, 1970 or March 1970
            fr'(\b(\d{{4}},?\s*{regexMonths}*[a-z]*\s*\d{{0,2}})\s*[{charsThatCouldFollow}])', # e.g. good for 1593 or 1593 Apr or 1593 Apr 1 (which creates problems for when I want to extracdt 1593|5|5 style of date text)
            #fr'(December\s*30,\s*1932)',
        ],
        [#2
            fr'(\d{{4}}\|\d{{1,2}}\|\d{{1,2}})(?![A-Za-z0-9])', # e.g. infobox YYYY|MM|DD
            fr'({regexMonths}[a-z]*,?\s*\d{{0,2}},?\s*\d{{4}})(?![A-Za-z0-9])',      #December[,][ ][30][,][ ]2006<can't follow with A-Za-z0-9>
            fr'\d{{4}},?\s*{regexMonths}*[a-z]*\s*\d{{0,2}},?\s*(?![a-zA-Z0-9])',
            fr'\d{{1,2}},?\s*{regexMonths}[a-z]*,?\s*\d{{4}}\s*(?![a-zA-Z0-9])', # e.g., "10 Apr, 1593" or 2 April, 1593-
            #fr'December\s*30,\s*1932',
        ],
        [ # 3 all date parts  needed (YYYY MM DD)
            #fr"22\s*February\|1846\|",
            fr'(\d{{4}}\|\d{{1,2}}\|\d{{1,2}})(?![A-Za-z0-9])', # e.g. infobox YYYY|MM|DD
            fr'({regexMonths}[a-z]*,?\s*\d{{1,2}},?\s*\d{{4}})(?![A-Za-z0-9])',
            fr'(\d{{1,2}},?\s*{regexMonths}[a-z]*,?\s*\d{{4}})\s*(?![a-zA-Z0-9])', # e.g., "10 Apr, 1593" or 2 April, 1593-
            fr'(\d{{1,2}}\s*{regexMonths}[a-z]*,?\s*\|\s*\d{{4}})(?![A-Za-z0-9])',
        ],
        #[ #4

        #]
    ]
    # learning from problems
    '''
       Some conflicts seemed impossible to resolve in one call to re.search()
       so I just create a second non-conflicting batch to try out if the first pass gathered nothing
        '''

    # Combine prefixes and date formats into separate patterns
    prefixPatterns = []

    for validPrefixSet in valid_prefixes:
        prefixPatterns.append('|'.join(validPrefixSet))
    datePatterns = []

    for validDatePatternSet in date_formats:
        datePatterns.append('|'.join(validDatePatternSet))

    # Combine lists of separate groups into a list of final regex patterns
    finalPatterns = [] # use finalPattern.append()

    for datePattern in datePatterns:

        for prefixPattern in prefixPatterns:
            finalPatterns.append(fr'(?:{prefixPattern})({datePattern}?)')

    # Flag indicators
    flag = 'b.'  # default flag

    # Try to find a match for each pattern (re.search suggested by chatGPT)
    '''
        Need to start with final_pattern1 and then check for the following:
        Was there any match period, if so, did we get group(1) and if so
        does ExtractDateComponents(date_str) manage to retrieve the month information out of it

        If so:
            we are done.
            (although there might be edge cases where my algorithm retrieves the month but somehow fails to retrieve the day).

        Else:
            We have a situation where applying any one of the other final_patterns might get us the results
            so we keep looping until month equals something (and we break out of the loop) or
            we get through all our patterns.
    '''

    year, month, day = "","",""
    saveYear = ""
    saveMatch = ""
    start,end = "", ""
    calType = 0 #0 = gregorian (new style), 1=Julian
    counter = -1

    for finalPattern in finalPatterns:
        counter = counter + 1
        print()

        match = re.search(finalPattern, bio_text)

        if not match:
            continue # trying our luck with the next pattern

        start = match.span()[0]
        end = match.span()[1]

        if not match.group(1):
            continue # trying our luck with the next pattern

        date_str = match.group(1)
        year, month, day = "","",""

        if date_str:
            year, month, day = ExtractDateComponents(date_str)

            if not month:

                if not saveYear:
                    saveYear = year
                    saveMatch = match
                continue

            else:
                break

        else:
            YMessage(f"Despite getting group1, we somehow didn't get anything in date_str. Check ExtractDateComponents() logic.\n" , logOption=ERRORLOG)

    if not match and saveMatch:
        match = saveMatch

    if match:
        YMessage(f"CALLING ExtractContext(text={bio_text[:100]}..., start_idx={str(match.start())}, end_idx={str(match.end())}\n" , logOption=LOG)
        context = ExtractContext(bio_text, match.start(), match.end())

        # Check for the approximate or flourishing indicators
        flourishedStringList = ['f.', 'fl.', 'flor.', 'f]].','fl]].','flor]].' ]
        circaStringList = ['c.', 'ca.', 'circa']

        if [ele for ele in circaStringList if(ele in match.group(0))]: #Got this from https://www.geeksforgeeks.org/python-test-if-string-contains-element-from-list/
            flag = 'c.'

        elif [ele for ele in flourishedStringList if(ele in match.group(0))]: #Got this from https://www.geeksforgeeks.org/python-test-if-string-contains-element-from-list/
            flag = 'f.'

        if saveYear:
            year = saveYear
        tabs(-1)

        return year, month, day, context, flag, match, start, end, calType

    YMessage(f"Returning _, _, _, _, flag={flag}, {match}, {start}, {end}\n", logOption=LOG)
    # If no date is found, return empty values
    tabs(-1)

    return "", "", "", "", flag, match, start, end, calType


def ExtractContext(text, start_idx, end_idx, window=100): #function generated by chatGPT and edited by me
    f = inspect.stack()[0][3] + "():" #function name
    tabs(1)
    YMessage(f"STA ExtractContext(text={text[:100]}..., start_idx={start_idx}, end_idx={end_idx})\n", logOption=LOG)

    # Get the surrounding context for the extracted date
    '''start must begin after a new line or a ". " string and not exceed window'''

    start = start_idx - window

    for c in range(start_idx, start_idx - window, -1):

        if "\n" == text[c]:
            start = c + 1
            break

        elif "." == text[c] and " " == text[c+1]:
            start = c + 2
            break

        if c == 0:
            start = 0
            break

    end = min(len(text), end_idx)
    for c in range(start_idx, start_idx + window, 1):

        if c < end:
            noprint("", text[c] + " at c=" + str(c) ) #text[c] retrieves a UTF-8 character, not an ASCII 1 byte parts

        if "\n" == text[c]:
            end = c - 1
            break

        elif "." == text[c] and ( " " == text[c+1] or "<" == text[c+1] ):
            end = c - 1
            break

        if c + 1 >= end:
            end = c
            break

    context = text[start:end].strip()
    YMessage(f"returning {context}\n", logOption=LOG)
    tabs(-1)

    return context


def ExtractDateComponents(date_str): # function generated by chatGPT
    f = inspect.stack()[0][3] + f"(date_str={date_str}):" #function name
    tabs(1)
    YMessage(f"STA {f}\n", logOption=LOG)

    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    # Try to parse different date formats
    #if "|" in date_str:
     #   doprint( date_str, "count of | == "+ str(date_str.count("|")))

    for c in range(len(date_str), 0, -1): #clean up potential garbage at the end

        if date_str.endswith('|') or date_str.endswith('\n'):
            date_str = date_str[:-1]

        else:
            break

    YMessage(f"date_str{date_str}\n", logOption=LOG)

    if "|" in date_str: #could be YYYY|MM|DD or YYYY|MM|DD| or DD Month|YYYY|  or DD Month|YYYY
        parts = date_str.split("|") # splits by one or more | characters.

        if len(parts) == 2:

            if parts[0][:4].isnumeric(): #probably YYYY
                parts[0] = parts[0][:4]

                if not parts[1].isnumeric(): # because we probably got YYYY|DD Month but also we might had gotten some garbage, so be careful
                    YMessage("parts[1] = " + str(parts[1]), logOption=LOG)

                    if " " in parts[1]:
                        part1bits = parts[1].split()
                        parts.append(part1bits[1])
                        parts[1] = part1bits[0]

                    else: #we got garbage so we delete all the other parts in parts
                        parts.pop(1)

                else:
                    msg = f"1: parts[1] contains {str(parts[1])}. Don't know what to do with it. date_str == {date_str}. Person ID:{g.currTempSummaryRow}"
                    YMessage(f"{msg}\n", logOption=ERRORLOG)
                    tabs(-1)

                    return "", "", ""

            elif len(parts[0]) < 3: # assuming DD or some short numeric thing
                msg = f"2: Got this date: {str(date_str)}. Don't know what to do. Person ID:{g.currTempSummaryRow}."
                YMessage(f"{msg}\n", logOption=ERRORLOG)
                tabs(-1)

                return "", "", ""

            else: #parts[0] is not numeric

                if parts[1][:4].isnumeric(): #YYYY
                    parts[1] = parts[1][:4]

                    if not parts[0].isnumeric(): #the assumption is DD Month
                        parts.append(parts[1])
                        part0bits = parts[0].split()
                        parts[1] = part0bits[1]
                        parts[0] = part0bits[0]

                    else:
                        msg = f"3: Got this date: {str(date_str)}. Don't know what to do. Person ID:{g.currTempSummaryRow}."
                        YMessage(f"{msg}\n", logOption=ERRORLOG)
                        tabs(-1)

                        return "", "", ""

                else: #first four characters are not numeric
                    msg = f"4: Got this date: {str(date_str)}. Don't know what to do. Person ID:{g.currTempSummaryRow}."
                    YMessage(f"{msg}\n", logOption=ERRORLOG)
                    tabs(-1)

                    return "", "", ""

        elif len(parts) == 3:

            for part in parts:

                if not part.isnumeric():
                    msg = f"5: Got this date: {str(date_str)}. Don't know what to do. Person ID:{g.currTempSummaryRow}."
                    YMessage(f"{msg}\n", logOption=ERRORLOG)
                    tabs(-1)

                    return "", "", ""

        else:
            msg = f"6: Got this date: {str(date_str)}. Don't know what to do. Person ID:{g.currTempSummaryRow}."
            YMessage(f"{msg}\n", logOption=ERRORLOG)
            tabs(-1)

            return "", "", ""

    else:
        parts = date_str.split() # splits by one or more space characters.

    yearIsFirst = False
    year, month, day = "", "", ""
    YMessage(f"parts={str(parts)} len(parts)={str(len(parts))}", logOption=LOG)
    unwantedCharList = [",", "-", "–", ")", "}", "{", "("]

    for c in range (0, len(parts)):

        if len(parts[c]) == 1 and not parts[c].isnumeric(): # dealing with an occasional "-"(or similar) character or a 1 digit date
            parts[c] = ""

        else:  # otherwise dealing with all the usual cases

            if [ele for ele in unwantedCharList if(ele in parts[c][-1])]: #sometimes we'll have a character we want to get rid of
                parts[c] = parts[c][:-1]

            if parts[c].isnumeric():  # e.g., could be 10 or 1970 from "10 March 1970" or "1970 March 10"

                if len(parts[c]) <= 2: # a month or a date

                    if c == 0:
                        day = int(parts[c])

                    elif c == 1: # currently I am duplicating the block you see in the case when there is only one character above - need to refactor this somehow

                        if yearIsFirst:
                            month = int(parts[c])

                        else:
                            day = int(parts[c])

                    elif c ==2:

                        if yearIsFirst:
                            day = int(parts[c])

                        else:
                            month = int(parts[c])

                elif len(parts[c]) == 4:
                    year = int(parts[c])

                    if c == 0:
                        yearIsFirst = True

                else:
                    msg = f"encountered a seemingly date-related number in->{str(date_str)}<-that I don't understand. ID:{g.currTempSummaryRow}"
                    YMessage(f"{msg}\n", logOption=ERRORLOG)
                    tabs(-1)

                    return "", "", ""

            else: # assuming it's a month string or a fancy year string like '94 (TODO)

                if parts[c][:3] in months.keys():
                    month = months[parts[c][:3]]

                #else: we just ignore and month remains unset

        if c == 2:
            break

    YMessage(f"RETURNING year={year}, month={month}, day={day}. Person ID:{g.currTempSummaryRow}\n", logOption=LOG)
    tabs(-1)

    return year, month, day # If we were successful that is! (and if the page actually had the data, which some pages do not)


def ExtractFstLstNames(personName): # how hard can it be to get the first and the last name from a full name string....:)

    if "," in personName:
        personNameParts = personName.split(",")
        personName = personNameParts[0]

    personNames = SplitString(personName) #this split string has smarts to make sure that anything inside ( ) is extracted as a unit
    personFstName = personNames[0]

    #personLstName = personNames[-1] # but not always, because sometimes there is a specifier in parenthesis e.g. "(composer)"
    for c in range(-1, -6, -1):
        personLstName = personNames[c]

        if not "(" in personNames[c]:
            break

    return personFstName, personLstName


def ExtractPageNameFromWikiRow(row, log=True):
    f = f"{inspect.stack()[0][3]}(row={str(row)}):" #function name
    tabs(1)
    YMessage(f"STA {f}\n", logOption=LOG)

    # Typical situation is I get rows like this:
    # #REDIRECT [[wikipage Name]]

    # locate where "[[" is
    regexPattern = re.compile(r'\[\[([^|\]]+)\|?.*?\]\]')

    if "*[[" in row or "REDIRECT" in row: #assuming all the composer pages on the summary page begin with a bullet point
        '''extract page name'''
        match = re.search(regexPattern, row)
        YMessage(f"match={str(match)}", logOption=LOG)

        if match:
            YMessage(f"match.groups(1)={str(match.groups(1))}", logOption=LOG)
            YMessage(f"Returning match.group(1)=={str(match.group(1))}, logOption=LOG)
            tabs(-1)

            return str(match.group(1))

    YMessage(f"END {f} RETURNING nothing", logOption=LOG)
    tabs(-1)

    return ""


def ExtractShortenedVersionOfContent(content):
    f = f"{inspect.stack()[0][3]}(content={str(content)}):" #function name
    tabs(1)
    YMessage(f"STA {f}\n", logOption=LOG)

    returnValue = ""
    firstEqualsSignsEncountered = False
    pattern = r'==.*==\s*'

    for row in content.splitlines():
        returnValue = returnValue + row + "\n"
        match = re.findall(pattern, row)
        print("match=" + str(match))

        if match:

            if not firstEqualsSignsEncountered:
                print("Found == == match=" + str(match))
                firstEqualsSignsEncountered = True

            else:
                break

    YMessage(f"END {f}", logOption=LOG)
    tabs(-1)

    return returnValue


def ExtractSubStringBetweenStrings(source, bef, aft):
    f = f"{inspect.stack()[0][3]}(source={str(source)}, bef={bef}, aft={aft}):" #function name
    tabs(1)
    YMessage(f"STA {f}", logOption=LOG)

    idx1 = source.index(bef)
    idx2 = source.index(aft)

    # length of substring 1 is added to
    # get string from next character
    res = ''
    # getting elements in between

    for idx in range(idx1 + len(bef), idx2):
        res = res + source[idx]

    YMessage(f"END {f}\n", logOption=LOG)
    tabs(-1)

    return res


# Function to fetch page content from Wikipedia
def FetchWikipediaPage(wikipediaPageName):
    f = f"{inspect.stack()[0][3]}(wikipediaPageName=={wikipediaPageName}):" #function name
    tabs(1)
    YMessage(f"STA {f}", logOption=LOG)

    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': wikipediaPageName,
        'rvprop': 'content'
    }
    YMessage(f"CALLING requests.get(WIKIPEDIA_API_URL, headers, params)", logOption=LOG)

    response = requests.get(WIKIPEDIA_API_URL, headers=headers, params=params)

    if not response:
        YMessage(f"FAILED to get a response from requests.get(WIKIPEDIA_API_URL=={WIKIPEDIA_API_URL}.....)...Returning ''.", logOption=ERRORLOG)
        YMessage(f"END {f}", logOption=ERRORLOG)
        tabs(-1)

        return ""

    data = response.json()

    if ", 'missing': ''" in str(data): # couldn't get the page with such name
        msg = (f"It looks like the page '{wikipediaPageName}' doesn't exist. Got this response from requests.get's response:\n{str(data)}\n"
              f"Consider fixing list of wikipages. PersonID:{g.currTempSummaryRow}.")

        YMessage(f"{msg}", logOption=ERRORLOG)
        YMessage(f"END {f}", logOption=ERRORLOG)
        tabs(-1)

        return ""

    page_id = next(iter(data['query']['pages']))
    content = data['query']['pages'][page_id]['revisions'][0]['*']

    YMessage(f"END {f} RETURNING the following (starting next line): \n{content[:100]}.... \n(longer content is not shown)", logOption=LOG)
    tabs(-1)

    return content


def FetchWikipediaPermUrl(wikipediaPageName):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': wikipediaPageName,
        'rvprop': 'ids'  # Get the revision ID
    }

    response = requests.get(WIKIPEDIA_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        page_id = next(iter(data['query']['pages']))
        latest_revision_id = data['query']['pages'][page_id]['revisions'][0]['revid']

        # Construct the permanent URL
        permanent_url = f"https://en.wikipedia.org/w/index.php?title={wikipediaPageName}&oldid={latest_revision_id}"

        return permanent_url

    else:
        print(f"Error retrieving data from Wikipedia API: {wikipediaPageName}")
        exit()


def JulianToGregorian(year, month, day): # chatGPT failed to make it correctly, but it did suggest to use jdcal module which I then figured out
    # Calculate Gregorian Day from Julian calendar date
    j1 = jdcal.jcal2jd(year, month, day)
    #print(j1)
    j2 = jdcal.jd2gcal(*j1)
    #print(j2)
    '''

    '''
    return j2


def OpenUniqueFileForOutput(fname, openType="w"):
    file = None
    index = 1
    maxFileNum = 10
    newName= ""

    # first check that the file already exists,
    if os.path.isfile(fname):
        # fname exists

        for c in range(index, maxFileNum + 1):
            lastDotPos = fname.rfind(".")
            fnameName = fname[:lastDotPos]
            fnameExt = fname[lastDotPos:]

            newName = f'{fnameName}{str(c)}{fnameExt}'

            if not os.path.isfile(newName):
                print(f"Will try to open {newName}")

                try:

                    return open(newName, openType)

                except:
                    YMessage(f"couldn't open {newName} for writing", logOption=ERRORLOG)

                    exit()

    if not file:
        YMessage(f"couldn't find a unique file name to use. Last tried - {newName}", logOption=ERRORLOG)

        exit()

    return file


def SplitString(inputString): #generated by chatGPT
    # Define the regular expression to match words or phrases within parentheses
    pattern = re.compile(r'\([^()]*\)|\S+')

    # Find all matches in the input string
    matches = pattern.findall(inputString)
    '''
    # Examples
    string1 = "asdf sdfg dfgh"
    string2 = "qwer wert (erty rtyu tyui)"
    print(split_string(string1))  # Output: ['asdf', 'sdfg', 'dfgh']
    print(split_string(string2))  # Output: ['qwer', 'wert', '(erty rtyu tyui)']
    '''

    return matches


def Testing(test_strings): # a function that helps to verify that all my test cases still work after any code changes (Just need to set TESTING at the top to True)
    # testIdIdx, testSummaryIdx, testNameIdx, testCorrectDateIdx, testBiotextIds = 0, 1, 2, 3, 4

    if g.TESTING:
        testChecks = ['ID   |EXPECTED  |RESULT    |CHECK|group 0                   =>group 1                   ==>group 2'] # a list of lists
        totalOKResults = 0

        for test in test_strings:
            result = "OK   "
            match0, match1, match2 = " ", " ", " "

            if int(test[g.testIdIdx]) >= g.testIDStart:
                year, month, day, context, flag, match = ExtractBirthDateFromBioText( test[g.testBiotextIds], test[g.testNameIdx] )
                doprint("match=", str(match))

                if match:
                    match0 = match.group(0)
                    if not match0:
                        match0 = " "
                    match1 = match.group(1)
                    if not match1:
                        match1 = " "
                    match2 = match.group(2)
                    if not match2:
                        match2 = " "

                resultStr = str(year).rjust(4, " ")+" "+str(month).rjust(2, " ")+" "+str(day).rjust(2, " ")

                if resultStr != test[g.testCorrectDateIdx]:
                    result = "XXXXX"

                else:
                    totalOKResults = totalOKResults + 1

                testChecks.append(test[g.testIdIdx].rjust(5, " ") + "|" + test[g.testCorrectDateIdx]+"|"+resultStr+"|"+result+"|"+match0+"=>"+match1+"==>"+match2)

            if int(test[g.testIdIdx]) >= int(g.testIDEnd):
                break

        count = -1

        for n in testChecks:
            count = count + 1
            print(n)

        print("OK", totalOKResults, "out of", count)

    return


def WriteStringToFile(file, mystring):
    strlen = len(mystring)
    response = 0

    if strlen == 0:
        return 0

    response = file.write(mystring)

    if response != strlen:
        print("For some reason, I wasn't able to write to {file.name} all the characters of the following string ({strlen}):\n ({mystring})")

        exit()

    return 0
