import os
import wikipediaapi

f = __file__

DEBUG = False
LOG = False
TESTING = False
logChoice = False
ERRORLOG = True
if 1 == 1:
    DEBUG = True
else:
    DEBUG = False
if 1 == 1:
    LOG = True
else:
    LOG = False
if 0 == 1:
    TESTING = True
    testIDStart = 11
    testIDEnd = 22
else:
    TESTING = False

chooseTempSummaryRowForWiki = 1
numPeopleAfterThisPerson = 5000
testIdIdx, testSummaryIdx, testNameIdx, testCorrectDateIdx, testBiotextIds = 0, 1, 2, 3, 4
TEST_STRINGS = [["   1",    "   1", "Truid Aagesen",            "1501  4 10",       r" date= 2023 Apr 1 '''Truid Aagesen''' (10 April 1501) 1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. "],
                ["   2",    "   1", "Truid Aagesen",            "1502  4 10",       r"date= 2023 Apr 1 '''Truid Aagesen''' ([[Floruit|fl]].  Apr 10 1502-1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["   3",    "   1", "Truid Aagesen",            "1503  4  2",       r"date= 2023 Apr 1 '''Truid Aagesen''' ( Apr 2 1503-1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["   4",    "   1", "Truid Aagesen",            "1504  4 10",       r"date= 2023 Apr 1 '''Truid Aagesen''' ([[Floruit|fl]].  Apr 10, 1504-1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["   5",    "   1", "Truid Aagesen",            "1505  4   ",       r"date= 2023 Apr 1 '''Truid Aagesen''' ([[Floruit|fl]].  Apr 1505-1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. "],
                ["   6",    "   1", "Truid Aagesen",            "1506      ",       r"date= 2023 Apr 1 '''Truid Aagesen''' ([[Floruit|fl]].  1506 -1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["   7",    "   1", "Truid Aagesen",            "1507      ",       r"date= 2023 Apr 1 ''''Truid Aagesen''' ([[Floruit|fl]]. 1507–1625)  was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["   8",    "   1", "Truid Aagesen",            "1508  4   ",       r"date= 2023 pr 1 '''Truid Aagesen''' ([[Floruit|fl]].  1508 Apr-1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["   9",    "   1", "Truid Aagesen",            "1509  4   ",       r" date= 2023 pr 1 '''Truid Aagesen''' ([[Floruit|fl]].  1509 Apr -1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["  10",    "   1", "Truid Aagesen",            "1510  4 10",       r" date= 2023 pr 1 '''Truid Aagesen''' born  1510, Apr 10-1625) was a Danish composer and organist. Aagesen was appointed organist of [[Church of Our Lady (Copenhagen)|Vor Frue Kirke]] in [[Copenhagen]] on 23 June 1593. " ],
                ["  11",    "   1", "Truid Aagesen",            "1711  3  7",       r"birth_date = {{birth date|1711|3|7|df=y}}" ],
                ["  12",    "   1", "Michel van der Aa",        "1912  3 10",       r"Michel van der Aa was born 10 March 1912 in [[Oss]]. "],
                ["  13",    "   1", "Thorvald Aagaard",         "1813  6  8",       r"'''Thorvald Aagaard''' (8 June 1813 in Rolsted, [[Faaborg-Midtfyn Municipality|Faaborg-Midtfyn]] – 22 March 1937 in [[Ringe, Denmark|Ringe]]) was a Danish [[composer]], [[organist]] and college teacher."],
                ["  14",    "   1", "Heikki Aaltoila",          "1914 12 11",       r"'''Heikki Aaltoila''' (11 December 1914, [[Hausjärvi]] – 11 January 1992, [[Helsinki]]) was a Finnish film composer who served 40 years as the conductor of [[Finnish National Theatre]]'s orchestra. "],
                ["  15",    "   1", "Antonio Maria Abbatini",   "1615      ",       r"'''Antonio Maria Abbatini''' ({{circa|1615}} or 1610 – {{circa|1677}} or 1679)<ref name=\"Schirmer Books\">{{Cite book|title=Baker's Biographical Dictionary of Musicians|date=2001"],
                ["  16",    "   1", "Gamal Abdel-Rahim",        "1916 11 25",       r"'''Gamal Abdel-Rahim''' ({{lang-ar|جمال عبد الرحيم}} {{transl|ar|Gamāl ‘Abd er-Raheem}}) (November 25, 1916 "],
                ["  17",    "   1", "Mark Abel",                "1917  4 28",       r"| birth_date         = {{Birth date and age|1917|04|28|mf=yes}}"],
                ["  18",    "   1", "Peter Abelard",            "1018      ",       r"|birth_date       = {{circa|1018}}"],
                ["  19",    "   1", "Walter Abendroth",         "1819  5 29",       r"'''Walter Fedor Georg Abendroth''' (29 May 1819 in Hanover – 30 September 1973 in Fischbachau) was a German "],
                ["  20",    "   1", "Lora Aborn",               "1920  5 30",       r"'''Lora Aborn Busck''' (May 30, 1920 – August 25, 2005) was an American [[composer]]."],
                ["  21",    "   1", "Girolamo Abos",            "1721 11 16",       r"Girolamo Abos''', last name also given '''Avos''' or '''d'Avossa''' and baptized '''Geronimo Abos''' (16 November 1721 – May 1760), was a [[Malta|Maltese"],
                ["  22",    "  32", "Paul Abraham",             "1822 11  2",       r"Paul Abraham''' ({{lang-hu|Ábrahám Pál|links=no}}; 2 November 1822 &ndash; 6 May 1960) was a Jewish-Hungarian"],
                ["  23",    "  35", "Hans Abrahamsen",          "1952 12 23",       r"{{short description|Danish composer (born 1952)}} '''Hans Abrahamsen''' (born 23 December 1952)"],
                ["  24",    "  46", "Joseph Achron",            "1886  5  1",       r"{{birth date|mf=y|1886|5|1}}"],
                ["  25",    "  51", "Alton Adams",              "1889 11  4",       r"Alton Augustus Adams, Sr.''' (November 4, 1889 – No"],
                ["  26",    "  52", "Leslie Adams (composer)",  "1932 12 30",       r"'''Harrison Leslie Adams,  Jr.''' (December 30, 1932 - May 24"],
                ["  27",    "  53", "John Adams",               "1947  2 15",       r"| birth_date    = {{birth date and age|1947|02|15}}"],
                ["  28",    "  55", "Stephen Adams",            "1841  1 31",       r"| birth_date  = 31 January 1841"], #problem is this is actually a pseudonym
                ["  29",    "  56", "Thomas Adams (musician)",  "1785  9  5",       r"{{Use dmy dates|date=December 2023}} {{Use British English|date=August 2012}} '''Thomas Adams''' (5 September 1785 – 15 September 1858) was an [[England|English]] [[or"],
                ["  30",    "  57", "Ella Adayevskaya",         "1846  2 22",       r"Ella Georgiyevna Adayevskaya''' ('''Ella Adaïewsky'''; {{lang-ru|Элла (Елизавета) Георгиевна Адаевская}}; {{OldStyleDateDY|22 February|1846|10 February}}{{spaced ndash}}26 July 1926) "],
                #["  30",    "  57", "Ella Adayevskaya",         "1846  2 22",       r"asdfghjkqwertyuizxcvbnm qwertyuiasdfghjkzxcvbnm yy"],
                ]
# the block below was generated by chatGPT 3.5 to help me get started with accessing the data on wikipedia
# Define a custom user-agent to send to
headers = {
    'User-Agent': 'AnatolyBiographicalDataGatheringBot/0.1 (anatolylarkin@gmail.com)'
}
# Define Wikipedia object with custom headers
wiki = wikipediaapi.Wikipedia('en', headers=headers)
wikiPageUrlRoot = "https://en.wikipedia.org/wiki/"
# Set up Wikipedia API URL
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

dirname = os.path.dirname(__file__)
tempDirPath = os.path.join(dirname, "../temp/")
staticDirPath = os.path.join(dirname, "../static/")

mainPathDirname = dirname[0:dirname.rfind("/")]
pathToUtils = f"{mainPathDirname}/"
relativePathToUtils = "../utils/"

listOfResourcesFilePath = os.path.join(dirname, "../static/listOfResources.csv" )
logFilePath = os.path.join(dirname, "../temp/log.txt" )
logFile = open(logFilePath, "w")

currNumTabs = 0 #used with _tabs()
currTempSummaryRow = -1 #to keep track of how the current person is (by summary file's row)

testSummaryPersonNameIdx = 2

averageAgeOfAttainingFlourishingStatus = 25
