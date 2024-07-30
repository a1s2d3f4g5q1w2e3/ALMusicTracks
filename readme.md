#  AL MusicTracks
#### Video Demo: https://youtu.be/rI64rVufr6k
#### Description:
If you feel you are qualified, post your suggestions on this forum: https://github.com/a1s2d3f4g5q1w2e3/ALMusicTracks/discussions/

Copyright(c) 2024, Anatoly Larkin. All rights reserved. 
https://www.anatolylarkin.com

This file is part of the AL MusicTracks project, which is free software. You may redistribute and/or modify it under the terms of the GNU General Public License, version 3 or later, as published by the Free Software Foundation.




Introduction
------------


### Problem ###

As a classical musician, I occasionally have very specific questions regarding my field: 

- Which composers lived in Vienna in 1801?
- Who were the students of Saint-Saens?
- What pieces for violin and flute were composed by any composer living in Italy between 1610 and 1620?
- etc.

I imagine, if I were a student of literature, visual arts, sciences or other areas of study, I would have similar questions about people, or their works, in those fields.

As of today (July 2024), ChatGPT-4 is unable to provide truthful answers to such questions as it is not trained in providing truthful answers. Plus, even if an AI model becomes reliably truthful, it certainly takes a lot of CPU cycles to retrieve answers from it.

Instead, I think we need to systematize the knowledge we already share in the public domain and make it easily retrievable so that these types of questions are instantly - and correctly - answered.



### Solution ###

My solution was to start building and refining algorithms that "scrape" the freely available knowledge on Wikipedia and other online repositories for _specific data items_ and then loading those items into a database, which can then be queried the way all other existing databases are.

In other words, I want to gather a lot of facts online and I write programming code to do it automatically. I then want to ask my questions about these facts via a "query". For example, "Which composers lived in Vienna in 1801?" is asked by setting the following input boxes in a "search parameters" table thus:

- person occupation: "composer"
- person location: "Vienna"
- person location time Y: "1801"


## Initial project steps overview ##

I began by looking at a kind of "summary page" on [Wikipedia][] - a list of thousands of wiki links to individual composer pages - and writing a Python module (~/Webscraping/) that retrieves data items like names, birthdays, etc. for each listed composer. 

[Wikipedia]: https://en.wikipedia.org/wiki/List_of_composers_by_name


The retrieved data is temporarily stored in a CSV file, which is used by another module I coded (~/dbManagement/), to populate an SQlite3 database.

Finally, I put together a web app powered by Flask (~/app.py) that uses the populated database to allow the end-user to browse the information in the database based on specific search parameters and, potentially, edit it, too.

I will now describe these steps in greater detail, showing what the current capabilities of the system are. After that I will follow up with the discussion of where the project is heading and the steps required to achieve its goals. Any developments and follow-on notes added after the initial publication of this document are to be preceded by a time stamp and a colon.




What has been done
------------------



### Figuring out the coding environment ###

This project also serves the purpose of satisfying the "Final Project" requirement of the CS50x course from Harvard University that I am completing online. Through this course I have learned about SQlite, Flask and Jinja, as well as deepened my understanding of Python - tools that I found well-suited for attempting to solve the above problem, one that has occupied my mind for a number of years.

CS50x provides a coding environment to its students through GitHub's Codespaces platform. This means that I learned to use VS Code to code programs and run processes without the need of setting up a local environment on my Windows computer.

However, one major drawback of coding online is that there is a time limit for how long the system allows the user to use its resources uninterrupted. If you don't interact with the platform for more than 30 minutes, the system "logs you out" and you need to wait at least 30 seconds to log back in before you are able to code again. That, naturally, wastes precious time.

So, to have easier times when working on this project, I figured out a way to replicate the VS Code-based coding environment of CS50x locally on my Windows machine (partly by asking chatGPT how to do it, partly by reading StackOverflow posts on this topic). 

Later still, I had to learn how to "push" my local edits back to my GitHub "repository" (where you are, presumably, accessing this file) and see those edits appear in the CS50x codespace.

Within the CS50x codespace (online or locally) I have a folder called "project". (NB: Later, I created a separate repository called “ALMusicTracks” on GitHub to which I copied all the “project” files). Within this folder are various files and subfolders that I will explain in the paragraphs below.

As I developed my code, to help with debugging, I found it useful to output the details of the algorithm flow to the terminal window. You can see YMessage and NMessage functions in utils.py. During the “production run”, when not debugging code, outputting all the text messages to the console slows down the execution of the code. To solve this problem, I can set the global DEBUG variable to False, which is used as YMessage’s “logOption” parameter to not output anything to the console.

Also, a number of generic “utility” functions were introduced and saved inside ~/utils/utils.py which was then imported inside each “subproject” .py file thus:
```
sys.path.append(os.path.abspath(os.path.join(g.pathToUtils, '')))
from utils.utils import *
```



### Scraping the web (webScraping) ###

As explained in the introduction, the basis of the project is a well-populated database of facts about, in this case, (classical) music (but it can certainly be expanded to encompass any field). Though it is possible to achieve as a crowdsourced effort, still, to populate a large database manually takes a long time (and I currently do not have a “crowd”). Therefore, my first step involved learning how to programmatically retrieve wiki text of a Wikipedia page using the so-called Wikipedia API (wikipediaapi) module in Python, so that I could "mine" Wikipedia for data items. (Here chatGPT provided me with excellent starter code, which I then adapted as necessary).

I started by creating a subproject folder (~/webScraping/) and some Python files (webScraping.py, webScraper.py, wikihelpers.py, globalVars.py). It was important to learn how to properly “import” each .py file inside the other, so that, for instance, all “globalVars.py” variables were available as g.[variable name] to webScraping.py and others:
```
import globalVars as g
``` 

For the algorithm to know where to go to start the web-scraping process - i.e., the process of gathering and parsing text from thousands of webpages - I created a [CSV file][] containing the description of the resources to be scraped. (At the moment, July 2024, the CSV file has a single CSV row, where the important element is the URL of the "list of composers" summary page I mentioned in the introduction).

[CSV file]: https://github.com/a1s2d3f4g5q1w2e3/ALMusicTracks/blob/main/static/listOfResources.csv


Once my algorithm parses this row (~/webScraping/webScraping.py) and notices that it is a Wikipedia summary page, it engages the Wikipedia-API module to send in a properly formatted "json" request to receive the summary page's wiki text (wikihelper.py/FetchWikipediaPage(...)).

json request params:
```json
  params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': wikipediaPageName, # has been set to “List_of_composers_by_name”
        'rvprop': 'content'
    }
```

retrieved text snippet:
```
  {{Short description|none}}
{{Dynamic list}}
This is a '''list of composers by name''', alphabetically sorted by surname, then by other names. The list of [[composer]]s is by no means complete. It is not limited by classifications such as [[Genre (music)|genre]] or time period; however, it includes only music composers of significant fame, notability or importance who also have current Wikipedia articles. For lists of music composers by other classifications, see [[lists of composers]].

This list is not for arrangers or lyricists (see [[list of music arrangers]] and [[lyricist]]s), unless they are also composers.  Likewise, [[songwriter]]s are listed separately, for example in a [[list of singer-songwriters]] and [[list of Songwriters Hall of Fame inductees]].

{{Compact ToC|name=Directory|side=yes|center=yes|nobreak=yes|refs=yes|seealso=yes|extlinks=yes}}<!--first name then last-->

==A==
{{columns-list|colwidth=22em| 
*[[Michel van der Aa]] (born 1970)
*[[Thorvald Aagaard]] (1877–1937)
*[[Truid Aagesen]] (fl. 1593–1625)
... etc.
```

The summary page’s wiki text is parsed further to isolate only those lines of text that contain the Wikipedia page links of "[[Name of the page|optional, display name]]" format, ignoring other text.

This parsing is saved to another temporary CSV file, which is what I feed into my main scraping function, ~/wikiScraper.py=>ExtractDataFromWikiPersonPage(...). The wiki text of every person's individual Wikipedia page is retrieved and parsed as per below.


## How the "person's page" wiki text is parsed ##

The specific text of Wikipedia pages about composers differs from person to person but there are structural features that they all tend to share (as they do with Wikipedia articles about all people), thanks to Wikipedia community's push towards standardization.

A more famous person would usually have an "infobox" section near the beginning of the wiki text, introduced by the string "{{Infobox person". This is great for retrieving data, because it already has parsed information, like in this example:

```
{{Infobox ...
|birth_name  = Louis Moreau Gottschalk
|birth_date  = {{birth date|1829|5|8}}
|birth_place = [[New Orleans, Louisiana]], US
|death_date  = {{death date and age|1869|12|18|1829|5|8}}
|death_place = [[Rio de Janeiro]], Brazil
|occupation  = {{hlist|Composer|pianist}}
...
```

Here, every pipe character at the beginning of the line is followed by a term describing the data unit (name, birthday etc.) followed by its value. In the case of life dates, the format is consistent but requires further parsing logic to extract the data. For example, other people's Infoboxes could also look like this: 

```
| birth_date    = 22 October 1811
```
or
```
| birth_date         = {{start date|1939|06|06|df=y}}
```
or
```
| birth_date         = {{Birth date|1710|03|12|df=y}}
```
etc.

In other words, text strings following "birth_date = " or "death_date = " can be of different formats. My solution here (and for all other data units scraping tasks) was to learn to use "regular expressions", which have more flexibility than merely asking Python code 

```
   if '|birth_date" in textrow or '| birth_date" in textrow::
       if '{{birth date|' in textrow:
            # extract dob from the remaining part of the textrow
 elif '{{start date|' in textrow:
            # extract dob from the remaining part of the textrow
	...
```

Regex commands can achieve all the same results but with fewer lines of code, because regex has the inherent ability to check for multiple possibilities in one command, e.g. "| birth_date =", or "|birth_date=", or "|Birth_date      =" are all found by with this regex string: 

```
    '\|\s*[Bb]irth_date\s*='
```


Typically, however, the wiki text lacks the Infobox section and immediately gets into prose, like so:

Ex. 1

[Some initial Wikipedia-specific commands that we ignore because they don't have a group of three apostrophe characters]

```
'''Florian Leopold Gassmann''' (3 May 1729 &ndash; 21 January 1774<ref>Michael Lorenz: [http://michaelorenz.blogspot.co.at/2013/03/antonio-salieris-early-years-in-vienna.html "Antonio Salieri's Early Years in Vienna"]</ref>) was a [[German language|German-speaking]] [[Bohemia]]n [[opera]] [[musical composition|composer]] of the transitional period between the [[baroque music|baroque]] and [[classical music era|classical]] eras.
```

Ex. 2

```
...

'''Johann Joseph Fux''' ({{IPA-de|ˈjoːhan ˈjoːzɛf ˈfʊks|lang}}; {{circa|1660}} – 13 February 1741) was an Austrian composer, [[music theory|music theorist]] and [[pedagogy|pedagogue]] of the late [[Baroque music|Baroque]] era.
```

This data is far harder to parse out.

The essential consistent feature across all wikipedia articles about people is the three apostrophes (''') group that surrounds the person's name on both sides near the beginning of the article, immediately following some new line character, in most cases. This consistency allows me to both get the person's full name and expect to see date of birth values following close after (unless they were omitted in the article).

To see my current regex solution for trying to get at the birthdate data, see my code in ~/webScraping/wikihelpers.py => ExtractBirthDateFromBioText(bio_text, personName). It combines possible “prefixes” like r'b\.\s*' or r'born\s+' or r'born\s+on\s+' etc. with possible “date_formats” like fr'(\b\d{{1,2}},?\s+{regexMonths}[a-z]*,?\s+\d{{4}}\s*\b[{charsThatCouldFollow}])' or fr'(\b{regexMonths}[a-z]*\s+\d{{0,2}},?\s+\d{{4}}\s*[{charsThatCouldFollow}])', where “regexMonths” are pipe-separated 3 character month strings. Using the re.search(...) call, I see if my code was successful in retrieving any data, and if not, I move on to another possible combination of “prefix”+”date_format”.

Unfortunately, I still have some work left to do to refine this code because in roughly 5-10 percent of the cases, the birth date is either not retrieved at all, or worse, a wrong date is assumed to represent the birth date. For example:

```
| caption         = Portrait of Balakirev, c. 1900
| birth_name      = Mily Alexeyevich Balakirev
| birth_date      = {{Old Style Date|2 January 1837||21 December 1836}}
```

In this case, my stupidity in checking first for “prefix”+”date_format” pair, where the prefix is “c.”, instead of “birth_date”, resulted in “1900” being retrieved as the “birth year” for the composer with this wiki text.

Because of this, and because of the necessity of data quality assurance (see "Future" section below) I have to rely on human verification for every piece of data.


## Birth date flags ##

As you can see in the above examples, some Wikipedia person pages contain a precise birth date, but some refer to the person's moment of birth in an oblique way. For example, "circa 1660" doesn't guarantee that the person was born in 1660 but "around that time". Since we want to clearly differentiate this information from one that's known more precisely, I include "birthday flags" as a data item accompanying the birthday dates, if any.

In addition to the "circa" flag, there is also the -

- "f.[years]->b." flag which stands for "birth year is guessed to be 25 years before the flourishing years mentioned in the reference source.
- "bapt.->b." flag, which stands for "birthdate is guessed to be 1 day before the baptism date".
- some other flags are set manually (see updateDatabase section below)



At the end of this "webScraping" step of the project, I end up with a large set of parsed data, saved to a temporary “people data” CSV file (https://github.com/a1s2d3f4g5q1w2e3/ALMusicTracks/blob/main/temp/peopleFromWebScraping.csv) that I can use to move forward.



### Populating the SQL database (dbManagement) ###

With the people data CSV from the previous step prepared, the next step in my process chain is to populate a dedicated SQlite3 (July 2024) database with this CSV data.
``` 
    ~/dbManagement/ $ python dbManagement.py
```

Looping over the CSV lines, dbManagement.py calls helper functions to further parse the data and add it to the correct database tables. 

I made the decision to keep track of the project's data sources, so that every piece of information gathered into MusicTracks can be accounted for. I refer to these sources as reference sources, or simply references (ref, refs). For example, 

```        
https://en.wikipedia.org/w/index.php?title=Claude_Debussy&oldid=1236945152
```
is a URL-based ref, proving the existence of composer Claude Debussy, and, as you saw above in "webScraping", it is also a likely ref for biographical information such as the full birth name and the DOB values. As a first step, a ref is entered into a "references table" (refsT) of the database file (musictracks.db) and assigned a unique id.

All table names and the associated column names and types are defined in https://github.com/a1s2d3f4g5q1w2e3/ALMusicTracks/blob/main/dbManagement/gVars.py. The dbManagement module makes sure to create any missing tables at the beginning of its run.


## Approach to knowledge referencing ##

This project _uses_ publicly available knowledge and avoids containing any unique knowledge items of its own. Thus it _refers to_ the data in Wikipedia or IMSLP or other shared refs and it simply _copies_ data items from those refs for use in musictracks.db.

A real ref is a permanent ref. The usual Wikipedia URL points to the latest version of its page. Instead, the MusicTracks project uses _permanent_ URLs for Wikipedia articles. Those can be found if you click on a Wikipedia page's "page history". This assures that a ref can always be trusted to contain the same, unchanging data.

NB: permanent URLs are not necessarily used for GitHub file references in this document as the whole point of this project’s code is to be changing and dynamic!

What about other, non-wikipedia refs?

This is currently not supported in the project and is addressed in the “Future” section, but briefly:

For printed books, the ref would need to include an ISBN or some other pieces of data to uniquely identify a publicly available (at least, at one point in time) printed source, as well as a page number (see the discussion about Books in the "Future" section).

For other webpages that do not have a system of permanently preserving a ref under the same, unchanging URL, an Internet Archive repository URL would need to be used. If a webpage the user wants to use as a ref is not already available on Internet Archive, it cannot be used until Internet Archive accepts it for [archiving][] and provides the permanent URL.

[archiving]:https://help.archive.org/help/save-pages-in-the-wayback-machine/


What about something someone told you, maybe even the very person referenced in the database?

Hearsay is not a legitimate ref. To use a personal conversation as a ref, it must first be written about and made publicly available. For example, you can write about it in a blog, a personal website, a forum, or, perhaps, record a YouTube video (though, this is a dangerous ref as the channel or the video can be removed from YouTube, so it is safer to use text-based data, unless the YouTube video is somehow included in the Internet Archive repository). Then the published data's permanent URL can be used. If a private conversation cannot be published, it cannot be used in this project.


## refsT ##

Besides the unique id column, refsT table contains columns for encoding the URL of a ref (if it's an online resource) more efficiently than simply copying the URL string in its entirety. 

Because the design of the project began around the processing of Wikipedia data, it was convenient to split Wikipedia's permanent URL into four parts: URL root (urlRoot), URL main value (urlMain), URL suffix (urlSuffix) and URL suffix value (urlSuffixVal). For example,

```
https://en.wikipedia.org/w/index.php?title=Thorvald_Aagaard&oldid=1212139107
```
In this URL:
- urlRoot is "https://en.wikipedia.org/w/index.php?title="
- urlMain is the name of the Wikipedia page: "Thorvald_Aagard"
- urlSuffix is the part that follows urlMain: "&oldid" 
- urlSuffixVal is the remaining part of the URL string: "1212139107"

urlMain and urlSuffixVal values are unique, but urlRoot and urlSuffix values contain strings that are continuously reused by the Wikipedia URL structure. 

To this end, I created two helper tables called urlRootsT and urlSuffixesT and, to begin with, populated them with the values you see in the example URL above. Because of this, I can reference the urlRootsT's and urlSuffixesT's unique ids for all the Wikipedia refs in refsT, instead of constantly taking up space by copying the same strings over and over in urlRoot and urlSuffix columns.

As the project grows beyond Wikipedia to incorporate other ref sources, I intend to use the same approach.

Additionally, this table has a column called refType to allow for future expansion of this table's functionality and it is currently (July 2024) set with "1", identifying the ref as a URL-based ref, see discussion in the "Future" section.

There is also a voteVal column reserved for so-called "vote values" and this is discussed in the "Future" section as well.


## peopleT ##

And so, we continue on with the processing of the “people data” CSV row. With the refsT table ref record set, the corresponding refsT unique id integer is inserted into a new record in the peopleT table along with:

- addedByUserId: set to my (admin) user id
- wikiPageNameOrLike: which duplicates refsT’s urlMain value and so I now think it’s no longer a necessary value to have in peopleT (TODO)
- voteVal: set to 0 (see “Future” section)
- useThis: set to 1 for any new people (discussed in more detail in “Future” section)

This database table doesn't have any interesting data of its own but it does create a unique listing for a single person, thus providing us with a unique person id integer (personId) that can be referenced by other "people" tables. 


## peopleNamesFmlEngT ##

This is likely the most important table for referring to a person, as it contains the data columns lstName, midNames and fstName. At the moment, lstName and fstName columns are set by using the name strings from the "temp summary" CSV (i.e., the names used in the List_of_composers_by_name Wikipedia page - see urlMain in refsT above). midNames column is not currently set automatically but can be set manually later (see updateDatabase below).

Down the road, this should be changed to where these data items are retrieved from the three-tick-group-enclosed full name in the article about the person. (See “Future” section.)

The "Eng" part in the table name refers to the fact that the names are the English versions. See "Future" section for the discussion of support of languages besides English. 

The "administrative" columns such as addedByUserId, refId, personId (referencing the unique entry in peopleT table) keep the data organized. These columns are present in all other "people...." tables.


## peopleNamesFullNameEngT ##

This one is similar to peopleNamesFmlEngT, but the only data column is fullNameEng and it is supposed to feature the correct full name (in English) assigned to this person. For example, the famous Mozart is generally known as fstName: "Mozart", midNames: "Amadeus", lstName: "Mozart" and his full name is all three put together: "Wolfgang Amadeus Mozart".

*NB: You might naturally wonder whether there is any reason to have a separate “full name” table, if it appears to be a concatenation of first, middle and last names. It turns out that, in a number of cases, the name mapping is not straight forward. For example, “Felix Mendelssohn”, whose “full name” is “Jakob Ludwig Felix Mendelssohn Bartholdy”.

In most cases, the full name of the person is encapsulated by the three-apostrophe character groups mentioned above, but, in my haste to get this project working, I instead used the Wikipedia's page name to set the full name of each composer. This created many incorrect entries in this table and will be something to address in the future (see "Future" section).


## peopleDobT ##

Currently (July 2024), this is the only other data table, besides peopleNamesFmlEngT and peopleNamesFullEngT, that is largely filled for the current set of composers. It keeps track of composers' dates of birth.

The important data columns are:
- dobFlag
- evtTimeYgr
- evtTimeMgr
- evtTimeDgr

"gr" refers to the date values being in the Gregorian calendar mode. So far, all Wikipedia dates are presented as Gregorian calendar dates and are, therefore, easy to add to the database. Just in case, I did figure out a way (~/webScraping.py => JulianToGregorian(year, month, day)) to convert dates from Julian to Gregorian calendar formats correctly.

As mentioned above, the webScraping algorithm is slightly imperfect, meaning that the automatic loading of data into this table results in some data errors (as of July 2024), which need to be corrected, whether manually (see updateDatabase below), or by improving the ExtractBirthDateFromBioText(...) function.



### Database viewing tools ###

Being able to easily view and possibly edit the database data is important for this project. I found a VS Code “extension” for manipulating SQlite databases (the name is on my other computer at the moment) and installed it. I found it quite useful in my work using the local install of the VS Code environment.

With coding online, using CS50x’s GitHub Codespace, another built-in SQL viewer/editor is automatically provided for working with SQlite databases: phpAdminLite.



### Web-app (Flask) ###

Finally, with the musictracks.db loaded with data, I can proceed building a web browser-based interface that gives the user a way to browse the database contents by applying all kinds of search queries (i.e., questions you saw at the very top of this document) and allows changing the database values, too.

 
## File/folder structure ##

Because I decided to use Flask to implement a dynamic, database-supported website, I created a file/folder structure typical for [Flask applications][]:

[Flask applications]: https://web.archive.org/web/20240620165144/https://cdn.cs50.net/2017/fall/shorts/flask/flask.pdf


- ~/app.py (an entry point for Flask) when it processes interactions of the user with the website.
- ~/appGVars.py
- ~/templates/ folder, containing HTML files with Jinja code, allowing the display of all necessary project content.
- ~/static/ folder, containing a style.css CSS file to help with graphical rendering of the text content of the HTML pages; also, a script.js JavaScript code to allow to sort the HTML table content, but I am dismayed by its lack of responsiveness, so I plan on discovering alternative solutions.


## Starting the web app ##

Here is the command line that can be sent in from the server's (VS Code's) command line terminal to load Flask and create a way for a user on the web to interact with my app:

```
    flask run
```

It must be executed from the same path as app.py, i.e., ~/. 

During CS50x, I wasn't taught how Flask works "under the hood", but, rather, how to use it so that I can generate a dynamic, Python-powered web application. So, keep that in mind as you are reading my discussion of Flask.

Once it's loaded, Flask allows a specific URL to be used to execute the code in app.py under 
```
@app.route("/")
@login_required
def index():
```, 

which ends up serving index.html to the user.

In other words, if I, right now, take advantage of my project’s “free host”, CS50’s GitHub Codespace, navigate to my projects folder, and execute "flask run", you would be able to go to [this url][] and see what my app looks like.

[this url]: https://animated-trout-x5qr6gjx69cp96g-5000.app.github.dev/


Unless I am busy refining the app and breaking my code in the process (see this problem discussed in the "Future" section), the index.html would show (in July 2024 - I'll likely be moving this search page away from the home page in the future) a three-row table with the following headings:

- Last/First Names-Last
- First
- Ref.
- Full Name (Eng.)
- Pseudon.
- DOB Flag*
- DOB-Y
- M
- D
- DOD Flag*
- DOD Y
- M
- D


You'll also notice the "Include refs" checkbox and some text explaining what you are seeing and what to do.

The reason you are viewing this "search parameters" table is because of the code under the "/" route of app.py, combined with the HTML/Jinja code inside layout.html and index.html files. appGVars.py defines a global dictionary list (```searchFields```) for every column of the search table, referencing the global vars from ~/dbManagement/gVars.py. This dictionary list is then copy-appended three times to a global list called ```allSearchRows``` to then allow the index.html Jinja code to display the search table as shown. Most importantly, I am able to give a unique, structurally coherent _html element name_ to each input box of this table.


## Browsing the database ##

While looking at the described HTML page, type in "Beethoven" in the last name column in the second row of the "search parameters" table. Now, either hit enter or click the Search button.

You'll observe a few things:

1) There is now a new "search results" table shown below the "search parameters" table. In it, you should see two rows listing two Beethovens (the famous one and his brother), listing their names and other data, like their (guestimated) dates of birth.

2) You will also notice that the URL address changed slightly. Now "searchPeople" is added to the end of the "home" URL address. 

The reason for the appearance of "seachPeople" is because the "search parameters" table in the HTML is actually a so-called "HTML form", whose “action” attribute is set to “searchPeople”. Triggering the "Search" button, or pressing enter, sends this form's values into the Flask process, which then executes the commands in the searchPeople function underneath a searchPeople "route" "decorator" (I am still to figure out exactly how it all works behind the covers - but it does) in app.py. This “searchPeople” route string is thus added to the end of the website's URL.

Reading through the searchPeople function code, you'll notice that, pretty soon, searchPeople asks ~/dbManagement/dbMgmtHelpers.py => GetDbDataFromSearch(...) function for help, and this massive function works hard to parse out what the query is and build the SQlite “SELECT...LEFT JOIN ...WHERE …” command so as to retrieve the requested data from musictracks.db.

I won't go through the details of the algorithm's logic here (after all, the goal is to make the code itself easy to follow through structure and comments), but I will mention that the structure of the input box' names allows it to retrieve the query terms and pair them with the relevant database table data.

# Searching options #

Besides entering a specific name into the second row's "last name" cell, you can also type in "aa" into the second row and, say, "ae" into the third row, resulting in a search results table that displays all records where the last name begins with "aa" (not including names like "van Aa", which begins with "van") and stops as soon as it reaches "ae", searching through the last name column values alphabetically.
 
You can, of course, use any other search parameters, like the birth date values, to search for people born in a specific year, on a specific date, or in a specific date range.

Additionally, you can select the "Include refs" check box and have the ref links show up in the results table as well. 

Finally, putting "1" in select boxes of the top row allows the user to only display the specified columns in the results table.


## Updating the database ##

The results table is actually another HTML form with “action” attribute called “updateDatabase” and, similarly to "searchPeople" it causes Flask to execute all the code under the updateDatabase function name, should the user trigger a "submission" of this form through the pressing of the "update" button at the bottom, or hitting enter, while editing a "search results" form's cell.

Looking through updateDatabase code, you can see that it uses two helper functions, UpdateDbDataFromHtml or InsertDbDataFromHtmland; the algorithm has to decide how to handle any data submitted that differs from the data currently in the database, whether to insert a new record into a database table, or instead to update the existing values.

Below I will go through a number of examples of how updateDatabase affects the various database tables. It is important to note that I am currently only allowing myself and other trusted users to be able to update the database because I do not yet have a mechanism to recover from database damage, whether intentional or accidental.

In the "Future" section, you can read about how I want to move away from simply editing the database values directly and, instead, have a "community dispute process" take place to allow for transparency and accuracy.

# Full Names #

As mentioned in the Webscraping section, this table is currently full of incorrect data. As you will read in the "Future" section, this should be fixed programmatically, but at the moment it can also be fixed with a manual update by going to the provided ref link, for example, and copy-pasting the correct full name from there.

# peopleNamesFullBirthDocT #

This is another person's name-related table, which seeks to contain the exact name from the person's birth record document, in whichever language. Birth record document name is sometimes mentioned in the same Wikipedia article as every other detail, and sometimes not. For example, in the case of Wolfgang Amadeus Mozart, his birth record document name is mentioned in a separate Wikipedia article discussing the complicated sutuation with his [full name][].

[full name]: https://en.wikipedia.org/wiki/Mozart%27s_name


At present (July 2024), as with all other table edits, I have implemented the ability to manually enter and update the database record related to a person's birth record document name. I have not, however, provided the ability to set a ref value for this specific data item and so the algorithm forces the use of the current refId used in peopleT for that person. This means I cannot currently properly add Mozart's birth record's name, for example, through updateDatabase HTML interface, given that his birth record name is not discussed in the main (Wikipedia) ref for Mozart.

In general, once the ability to properly pair refs with new data items is implemented, I can foresee that the data items like "birth record document name" would be, more likely, added by community memebers manually, as opposed to being added through some clever algorithm that knows how to scour the internet for such esoteric data.



All other available columns can currently be edited in a similar way, with the refId never changing. The edits are currently assumed to be needed to correct either missing or incorrectly scraped data in the Wikipedia-pages refs. 



### Helper tools ###

While working on the project code, I invariably ran into situations where creating a helper function to solve a temporary problem helped to move forward. Below I list the various command line arguments that give me the extra abilities to manipulate the database data.


## colsonly ## 

~/dbManagement/gVars.py contains global variables that describe the structure of the musictracks.db tables. If I want to create any missing columns for any of my tables, I first make sure to add the data to gVars.py and then run the command below:

```
python dbManagement.py setvalue peopleDobT
```

This command makes sure that the description of peopleDobT table in gVars.py (in the ```tcols['peopleDobT_...``` block is represented in musictracks.db by inserting any missing columns and then quitting.


## copyonly ##

SQlite has limited abilities when it comes to altering the structure of a table. Sometimes I found it necessary to create a new table structure and copy one table to another. To show the mapping of the columns between the source and target tables, I created a global dictionary called tableCopyMap. 

```
python dbManagement.py copyonly dobT peopleDobT
```
In the above example, the contents of dobT table are copied to peopleDobT table using the above map.


## createonly ##

```
python dbManagement.py createonly
```

Because all my table creation commands are executed prior to the running of all the other commands, if I only want the program to create any new tables before quitting, I call it with the above argument, which forces the program to quit.


## test1 ##

```
python dbManagement.py test1
```

This, and potentially more tests, are created to help me with some debugging problems I ran into. For example, while struggling to understand the bug that would prevent me from retrieving the records from the database based on a seemingly correct db.execute call, I found it useful to be able to “play around” with the SELECT ... LEFT JOIN ... WHERE command to figure out what the issue was.


## setvalue ##

At one point I decided to add the useThis (see summary of database column names below, at the bottom of this document) column to most of my data containing tables that I need to set with value "1". The solution was to have a function that did just that (```SetTableColumnToValue(db, args[2], args[3], args[4])```) and it was executed with 

```
python dbManagement.py setvalue peopleDobT useThis 1
```


## skip1 ##

```
python dbManagement.py skip1
```

This kind of command allows me to “skip over” some parts of the dbManagement code at the beginning which I found useful during development.





Future
------



This being a very early (as of July 2024) stage of this project, there are a lot of steps left to do (TODO). Right now, I leave TODO notes for myself in a Google document, which are partly replicated in this section, but there is a better, collaborative way to create "issues" or "bug reports", and it needs to be set up.

At the moment, the following incomplete list of issues can give a sense of the direction(s) in which the development will unfold.

As these issues are addressed and resolved, I plan to add notes below each resolved item.



### A permanent home for this project ###

It's a less than ideal situation that I can currently allow others to interact with this web app only when I am actively using the CS50x GitHub-based codespace with the 30-minutee time out. It also has a cryptic, unwieldy URL. 

I don't yet know of the best, most cost effective way to serve this project to the world, but hope to get good advice from the community.



### Data security ###

Having created a dedicated repository (a1s2d3f4g5q1w2e3/ALMusicTracks) for this project on GitHub (one separate from CS50 Codespace and the one to which I connected the above-mentioned discussion forum), and having copied all the project’s files to it, I then removed musictracks.db - the sqlite database file - because I got concerned about having this file in a public repository. After all, it contains usernames and (hashed) passwords. That doesn’t seem like a safe thing to do. 

So, I hope someone points me in the right direction on how to handle this security issue properly.


### Improving the code without breaking the web app ###

At the moment, if I am working on improving the web app while Flask is live, actively serving the project on the web, any code changes that break the app are immediately reflected for everyone else. 

Ideally, I want the public repository I created to only contain tested, working code for the “live” version of the app, to which I would "push" my code changes from the "development repository" (be it the CS50 Codespace, or my local Windows machine), whenever they are ready to be pushed.

Given that there must exist (I assume) a standard way to deal with this issue, I need to learn about it to further this project and be able to collaborate with other coders.



### Algorithm efficiency ###

If this project becomes popular, the computer(s) serving it will be working harder to serve more people. I would love for the code to be streamlined so that it uses the server's CPU and RAM in the most efficient manner.

I can foresee many of my design choices undergoing revisions in the future. For example, I heard that SQlite3 doesn't support large databases as well as other “database management systems”. I don't know if it's true, but if so, and the database grows significantly, it would need to be “re-housed”.



### Data fill percentages ###

Some refs provide data for all data items for the associated entity (e.g., a person's first, middle, last names, year, month, day birth date values etc., but others only provide the name and nothing else, resulting in a database record that has many blank or “null” data items.

When users browse the database, they benefit from knowing how “filled” the database is. If they see a value of “88%” above “DOB-M” search column heading, it communicates that, if they try searching for all composers born in April, some of the 12% who were born in April, but do not have a filled date of birth month value, cannot possibly show up in the search results.



### Data quality assurance ###

The data items I have collected and will continue to collect programmatically during the webScraping stage need to be verified by other humans. My regex data extraction commands being imperfect means that unless someone manually clicks on a ref link and confirms that the data in the database matches what's written in the ref, we cannot be 100% certain that the database represents true values. The more people click and verify, the better. But how do we capture this manual verification process?


## Votes to support the data ## 

Almost every table in musictracks.db has the column "voteVal" (vote values). When the user entrusted with the right to vote assesses that the values in the associated ref match with the values in the database, they can click on an upvote button for this data item (the design of the button tbd) and then they must submit a "voting ballot" (see below) to show why they believe the values to be correct. In other words, I don't think it is a good idea to allow people to simply "vote unchecked", as with the "like" button of the YouTube videos or Facebook comments.

We want to be confident that the person who "upvoted" a data item did so consciously and provided a reason.

Submitting of such voting ballots by multiple users and engaging a module that automatically verifies the veracity of those voting reasons will serve to increase the item's vote value in the database (in the relevant table as well as in the refsT table). A value above 0 is already a good first step. Higher values would increase the user community's confidence even further. I can imagine using brighter shades of green for the backgrounds of the "quality assured" cells as more and more users verify the data, but that might possibly come in conflict with the users' browser display preferences (although, see "user preferences/color schemes" below).

Naturally, voteVal can also be decreased and you can read about it in the "Disputes" section below.


## Voting ballots and ballot verification ##

A "voting ballot" consists of yet another HTML form and contains a number of text input and check boxes/radio buttons. It can pop up, for example, as soon as the user tries to edit a value in the "search results" table. When the user fills out a voting ballot to support the correctness of the data, they select the "correct ref capture" radio button choice. I propose that they have the ability to copy and paste - into some “voting ballot” box - the corresponding text snippet from the reference source's text. This snippet can be later used by a "ballot verification" module to retrieve start and end character indices from the (permanent) ref's text to store them in the database as well. This would allow for a quicker assessment of all follow up ballots.

The "ballot verification" module needs to have the necessary logic to be able to assess the veracity of the ballot before the corresponding voteVal value is increased. If the verification module is unable to definitively say if the reasons on the ballot are valid for confirming the accuracy of the database data being voted on, then an entry in a "ballot validation required" (balValReqT) database table would be made. A dedicated HTML table would then allow other - and only other - community members to manually confirm or disconfirm the ballot.*

It's important to realize that this step is just to confirm that the user is submitting a valid ref, and not to argue about whether the ref itself is saying true things. This issue is dealt with in "Disputes" as described below.


*How can we prevent the situation of a malicious user setting up multiple accounts and confirming bad data by acting as if other users are confirming the ballot in balValReqT?



### Disputes ###

As soon as someone sees some piece of data that appears to contradict (according to this user) "the truth", they can submit alternative data values (supported by some ref) and thus start a "dispute". The mechanism of triggering a dispute can start as mentioned above: the user begins to edit a value in the "search results" table and is then forced into the completion of a "voting ballot" form. 

Also, the algorithm checks to make sure an active dispute for this record doesn't already exist in the "disputesT" table (see below). If it does, the user is sent to the “disputes” HTML page (also see below) to vote on this dispute.

Different dispute situations are discussed below.


## Data of a ref was incorrectly transcribed into the database ##

When the data in the ref source is not captured correctly (for example, by my imperfect webscraping algorithm), the database needs to be updated, of course. This updating involves the "voting ballot" process from above, where I described the "upvoting" situation. The only difference here is that the reporting user selects "incorrect ref capture" radio button choice, instead of "correct ref capture".

If the "ballot verification" process (i.e., the coded module, which is optionally followed by the human verification) confirms the "voting ballot" data, then the "history of database revisions" (hisDbRevT) table would store the user id of the helpful user, along with the id (tableNamesT) of the relevant table  and the id of the record in that table. 

The voteVal for the data item would also be increased by the above process.


## Data from a ref misstates facts and shouldn't be used in the search results ##

It is also possible that whoever created the original ref (e.g., a particular version of a Wikipedia article for some person) was wrong and a different ref should be used in our database (e.g., a different version of a Wikipedia article about the same person). 

For example, though it is commonly believed that Beethoven was born on December 16th, 1770, new hypothetical evidence might come to light showing that he was, instead, born on December 15th. Here the "voting ballot" would accept another ref source, but, otherwise, the user would provide all the other data in the same manner as described in the previous section.

At this point the new ref, along with the data it describes, is added as a new record to the corresponding table in the database, but "useThis" value is set to 0.

Subsequently, an entry made in the "disputes" table (disputesT), which gets shown on a dedicated "dispute resolution" HTML page, allows the user community to vote on the two options. disputesT table contains the id of the involved data table (tableNamesT) and the two unique ids from that table for which the dispute has been generated. In addition to using this entry to know what to display on the “dispute resolution” HTML page, this will also allow blocking of any new refs for this data item from being added until after the dispute has been resolved.

The exact manner in which the dispute is resolved is open for debate - perhaps, in this project's forum - but suffice it to say, the members of the community will be either voting in support of one data value or the other, or against one, the other, or both. It's possible that, if after a certain number of votes (exactly how many, tbd) it becomes obvious that one choice is the clear winner, the dispute is resolved in favor of the winner immediately. On the other hand, if the new ref creates a ca. 50/50 split in the user base's idea of where the truth lies, something clever would need to be done to resolve such a dispute.

Either way, when the dispute is resolved in favor of the new ref's data, then the useThis values of the two records are exchanged and voteVals for each data item updated. voteVal of the winner is incremented and voteVal of the loser is decremented.

hisDbRevT also gets an entry to honor the user who brought in the correct data.


## The user thinks some data is incorrect but it is actually correct ##

This situation is identical to the above two dispute situations, but in this case the dispute will be (presumably) resolved in favor of the old data.
In this case, the old data will end up with an increased voteVal. Also, the disputed data remains in the table with the reduced voteVal and useThis set to 0. This is important so that any future attempts to add the same (bad) data are rejected right away.



### Languages support ###

At the moment, besides the peopleNamesFullBirthDocT table, all names are set using the English language versions (i.e., how they appear in the English language Wikipedia). This situation needs to be improved so that all languages are supported. 

Composers whose names are not English often suffer from multiple accepted spellings of their names in English. To deal with this problem, multiple versions could be listed in this table, all referencing the same personId (and yet only one is marked as the "commonly accepted" spelling). It's not yet clear to me what the correct solution to this should be. 

These types of problems are somehow addressed by Wikipedia, where multiple accepted spellings of a composer's name point to the same page with the "most accepted" spelling (e.g., try searching for "rakhmaninov" and see what happens). I am guessing that there is a mapping table that collects all accepted spellings/misspellings of a name in some table and maps them to the "commonly accepted" one.

Whatever the Wikipedia solution is, it's either possible to find out what it is and borrow it or we can try to come up with our own.



### Expanding the database ###


## More ref sources ##

refs coming outside of Wikipedia articles currently (July 2024) cannot be stored in the database. What's the best way to store other refs in refsT? My thoughts are below.

I would mention that because Wikipedia already has a lot of information that is correct in the majority of cases, I would suggest focusing on other TODO items first, so as to better extract the information in the existing Wikipedia articles, before working on how to provide the mechanisms for using other refs.

# Books #

Book descriptions have titles (a string of characters), authors (an id from peopleT), publishers (an id from publishersT table), year and city (an id from placesT) of publication. publishersT table consists of the publisher's name string and includes the id (placesT) of the publisher’s city. Then, booksT table can hold a unique ISBN-or-similar identifier string for the book, the title of the book and the year of publication (in most cases, the title and the year together would uniquely identify the book, but to be safe, a separate identifier seems important to have - there is likely a solution out there for this problem already) and an id from publishersT. A separate mapping table, authorsT, maps peopleT ids to booksT ids to allow locating of authors involved in the writing of the book.

refType column in refsT can then be set with "2" (i.e., "ref is a book") and urlRoot, doubling in its function, can hold the booksT id, while urlSuffix can hold the page of the book.

I am somewhat bothered that this solution is an inefficient use of refsT, where, for all printed sources, the urlMain and urlSuffixVal columns will be blank. To this end, I can see url-based columns migrating out of refsT into a separate urlRefsT table, with refsT referencing ids from that table, with refType set to "1", as I mentioned earlier in this document. TBD.

# Articles and other printed sources #

The situation here is similar to books, where the article or anything else that's publicly available needs to be uniquely identified in its own table and the id of that table needs to be used in conjunction with the correct refType identifier in refsT table.


## More people ##

There are many more composer pages on Wikipedia than what's listed on the List_of_composers_by_name summary page. Every composer page tends to be tagged with a particular "category" tag, but all those tags are more specific than simply "Composer". There are "19th Century male composers", "List of 20th-century American women composers", and similar tags. To retrieve the list of pages under such tags, there might exist a particular wikipedia-api request to do that.

If it is possible to get the people lists that way, it will greatly expand the reach of "Webscraper".


## More details about existing people ##

The currently shown data items related to the entity “person” (i.e. person’s names, date of birth) are a tip of a huge iceberg of person-related biographical data.

We want the database to hold as much biographical data items as possible.

# Integrating further scraping data #

As the scraping algorithm improves and extracts more and more data items out of Wikipedia and other web pages, it would be important to intelligently integrate this data with what's already in the database. 

Every data item from the incoming CSV needs to be checked against the database. 

(A) If the incoming ref value matches an existing ref in refsT table, it means we must first of all do the following:

- check if this ref's voteVal is not negative (meaning that during past disputes it hasn't been voted down and should not be deemed trustworthy).

  - If it is negative, warn the user that this ref has already been rejected and don't allow them to proceed, suggesting they go to a forum to discuss this issue.

- determine if this ref is being used to support the data for an existing person in the corresponding table. (TODO: what's a good way of doing that?)
 
  - If so, for every CSV value (besides the ref) that doesn't match the existing database value, create a disputeT entry, or maybe create a text report instead. I am not yet sure what the better approach would be. Perhaps, in the initial, debugging stages of the code it is better to avoid touching the database (or, perhaps, maintain a copy of the database that can be experimented upon with the ability of restoring to the previous state should something go wrong).

  - for every matching value, do nothing as we are clearly dealing with data that has already been scraped.

  - for every value that has a blank (or no) value in the corresponding table in the database, the new data is inserted as if we are populating it for the first time.

(B) If, on the other hand, the ref doesn't already exist in refsT, or, it does but isn't associated with any person in peopleT:

- determine whether the ref is dealing with a person that exists in the peopleT table. (Here, I can imagine using the incoming name as a way of figuring that out, but we have to be careful in cases where a non-English name might have multiple acceptable spellings (see name spelling discussion above), or worse, if it's some person who shares all their names with another person in peopleT. Yuck - might require another manual intervention).

  - if related to an existing person, proceed as above (A), i.e. as if we are dealing with the case when this ref is in the database and used for this person. Just make sure to add this new ref to refsT and use its id.

  - if not, assume it's indeed a new person and enter them into the database like for the first time.

# peopleNamesPseudonymsT #

As many composers used (and use) a pseudonym, similar to other peopleNames... tables, peopleNamesPseudonymsT table holds pseudonym strings associated with a particular personId. Extra optional columns include the evtTime… and firstUsed columns that can encode the time that this pseudonym was used by personId person for the first time.

It is possible to set the pseudonym value manually (see updateDatabase) but it would be a nice challenge for the algorithm to be able to find it by parsing the text in a URL-based ref.

For example, a number of “redirects” in Wikipedia are to do with pseudonyms. A certain person is generally known by their pseudonym (like “Lady Gaga”) but their actual name is different (like “Stefani Joanne Angelina Germanotta")

# Temporal relations # 

Historical research can sometimes only determine when an event took place in relation to another event, without knowing the exact date. For example, "Chopin composed Prelude in a, Op. 28, while on the boat to Majorca".*

Instantly this communicates two facts:

- Chopin was on a boat heading to Majorca when he was writing down this prelude

- When Chopin was composing this prelude, he was located on a boat heading to Majorca.


This means that if we find out the date of one event, we instantly know the date of the other. Thus, in my many data tables, I have columns labeled relEvtId, relEvtTableId, relEvtTimeRelation. These columns specify the other event that is bound in a temporal relationship to the current record. relEvtId and relEvtTableId specify how to locate the other event’s record in the database and relEvtTimeRelation can have either negative, 0 or positive values, corresponding to the _current event_ happening either before (optionally, interpreted as how many years*10000+months+100*days) during (0) or after the other event.

So, in the case of Chopin’s case above, relEvtTimeRelation would be set to 0 for either the record related to him moving on a ship to Majorca, or the record related to the composition of the Op. 28 Prelude.

This is, of course, a potentially problematic situation in case Chopin traveled to Majorca on multiple occasions (which he didn’t, but still). We can’t relate every different trip to Majorca as happening “in the same time as” the composition of the same piece. So, another TODO here.


*I slightly made up this "fact" about Chopin. He did compose Op. 28 pieces around that time, but I am not aware of the specific prelude I mentioned being composed “on a boat”.


## Locations, occupations and more ##

There are, of course, countless other pieces of data to add to the database to make it truly comprehensive. Essentially, the goal is to capture every piece of information contained in a ref, whatever it happens to be (for people: where the person was located during their lifetime, other people they knew, things they did etc., and when any of those things took place).

I have already created "placeholder" tables such as placesT, occupationsT etc. to allow this database to contain information about geographical places, people's occupations etc. in a manner similar to what I am doing for people "data" tables already. In other words, there is a "parent table" (peopleT, placesT, occupationsT, etc.) that contains refsT ids, pointing to an information about some entity, and there are all these "children data tables" that reference the "parent table" unique id in different contexts.

For example, a table like placesT would list cities, addresses, or other places on earth, and a table like peopleDobT would use the unique ids of placesT to store the person's place of birth in placesId column. But, at the same time, for places related to musical works (place composing started, place composition first performed etc.) I would be using the unique ids from placesT in musical works-related tables.


## Musical works ##

As I mentioned in the introduction, I want to eventually be able to make database queries related to musical compositions. For this I need to scrape data from a public source that holds details about compositions. One such source is, of course, Wikipedia. But over the past decade, a community-driven project called IMSLP has grown significantly to contain a huge repository of data about musical compositions. It is mostly focused on compositions that are now in public domain, but it is also growing to include information about more contemporary pieces.

I have already created an algorithm that scrapes and saves data in CSV format from IMSLP.org but haven't fully polished the code to include it in this project (as of July 2024).


## Music recordings ##

There are a lot of existing online databases that deal with music recordings. I'd be interested in integrating them into my database once the musical works tables have been created, e.g., AllMusic or MusicBrainz.



### Search results display ###

At the moment, July 2024, the search results table suffers from a number of problems. I will list a couple below.


## Column order ##

It would be great if the user could specify, using numbers, the order in which they would like the results table's columns to appear. For example, if they prefer the date of birth columns to appear in the "D, M, Y" order, followed by the first and last name, the user enters 1 into DOB's D column, 2 for M, 3 for Y, 4 for the first name and 5 for the last name columns in the top row of the search table.

Alternatively, the user can be given an option to drag the columns around with the finger (on a touchscreen) or the mouse.


## Column width ##

A way of displaying width such that the entire text string in the cell can be seen seems important. If the text box cannot be widened due to other concerns, it could be possible to either reduce the size of the “search results” text strings, or employ word-wrapping.


## Exporting as CSV ##

Seems like giving the user a way of exporting the search results as CSV is a good idea.



### Updating the database at admin level, bypassing the dispute route ###

Until the dispute process is refined, I, and other trusted administrators, will have the option of bypassing it and updating the database "silently", with the power of benevolent dictators. 

The issues related to this process are listed below.


## Losing the spot ##

At the moment, after updateDatabase is triggered, the HTML view jumps to the top of the page to "flash" a message explaining what was changed. This is frustrating, because the user loses their place in the search results table. Some other mechanism needs to be developed, so that the editor is made aware of the changes that were made in the database, but also does not suffer from having to relocate where they were editing in a potentially long "search results" table.


## Locking out other admin users ##

When the user begins to edit a cell in a row, there should be an instant check to see if the source database record is not already being edited by someone else by checking if useThis is set to "-1". If not "-1", then it means that no one else is currently touching this record and it is ok to change its values, at which point the useThis is set to "-1" until the current user completes the update edits, at which point it gets reset to what it was previously.

Otherwise, the user is blocked (with a tooltip message) from making any edits.


## Sorting HTML table data ##

JavaScript tends to work slowly when sorting the table data. I don't yet know what the bottleneck is, but I would like to be able to re-sort the data more quickly after I click the column heading. So, that's a TODO.



### User preferences ###

The only way users will be happy to interact with this project is if the interactions can be customized and saved. That, naturally, implies the use of more tables in the database. 


## Saving search queries ##

If a user enters some values into the "search parameters" table (whether for people search or any other entity search), we have to instantly (at least, as soon as the user "submits" them and triggers the associated Python function) save them into some database table where they are paired with the user's user id. After login, these parameters must be retrieved and shown in the "search parameters" table. An optional "reset search" button can set all parameters to blank.

Alternatively, another button could save these parameters to a separate "save slot", to be possibly retrieved in the future. Each person would be allowed a certain number of saved slots and they would be selectable through some menu.


## Color scheme ##

Another good idea might be to give the user control over the visual appearance of the web pages on the website, like background and foreground colors for the body and cells, disabling the ability to have bad combinations like "black on black" etc. Of course, these parameters would also be saved in some userVisualParamsT table and retrieved after login.

There might also be the "correct way" to integrate this customization with the "Dark" or "Light" browser modes.


## Research companion ##

An individual user might want to add personal notes regarding certain database records. For example, a musician might want to indicate the date they started studying this or that work or this or that person, or some other personal notes regarding the data retrieved. As a pianist, I often want to keep a log of my _sight-reading_ or musical composition performance activities. 

It is possible that the best way to do it is to give the user an ability to export and import the database data based on unique record identifiers, while they maintain their personal records through another platform.




Other related projects 
----------------------


With a comprehensive database of biographical details in place, I can also finally realize my other dream of creating an interactive, SVG-based "biographical chart" atlas, showing the inter-relationship of composers and other musicians as lines on a 2-d graph with x-axis showing time, and y-axis showing a "stringified" surface of the earth.



Summary of database table columns
---------------------------------

| colName | used in tables | comment |
| --- | --- | --- |
| useThis | all tables except < | allows to store all data in a table, but only use certain records as official representations of the community-accepted truth. If a certain record (based on a certain ref) is challenged and loses in a dispute, its useThis value becomes "0" and the other record is now used instead. However, any future attempt to submit data that matches that of a record whose useThis is set to "0", is rejected and would need to be discussed in a forum first. |
| voteVal | < ...

tbc.




Thanks for reading.
Please make improvement suggestions in the above-mentioned forum.






