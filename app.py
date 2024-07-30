import os, sys
import datetime
import pytz
import appGVars as g
import dbManagement.gVars as mgv
import dbManagement.dbMgmtHelpers as mg

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from utils.utils import *

from helpers import *
from cashSharesManagement import *
LOG = mgv.LOG

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd # I am not using it for now, but I might

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#print("loading!!!!")
g.db = SQL("sqlite:///musictracks.db")

response = g.db.execute(
            "CREATE TABLE IF NOT EXISTS ? ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, \
                username TEXT NOT NULL, \
                hash TEXT NOT NULL, \
                cash NUMERIC NOT NULL DEFAULT 10000.00 \
                )",
            g.usersTableName
            )

#print(response)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    return response


@app.route("/")
@login_required
def index():
    # transactionsTableName = g.transactionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user
    """Show portfolio of stocks"""

    """retrieve data for the table from the g.db table (if exists) AND"""
    """iterate over all rows in the list and add two more dictionary entries: price and total"""

    # using g.searchRow
    YMessage("___________________________________________________", logOption=LOG)
    if len(g.allSearchRows) != g.initNumSearchRows:
        for c in range(1, g.initNumSearchRows + 1):
            g.allSearchRows.append(list()) # Had some trouble creating a true copy of searchFields inside "allSearchRows" list
            YMessage(g.allSearchRows, logOption=LOG)
            for dict in g.searchFields:
                g.allSearchRows[c-1].append(dict.copy())

    ##g.allSearchRows[0][0]['val'] = "asdf"
    #print(g.allSearchRows)
    #print()
    #g.allSearchRows[1][0]['val'] = "asdfasdfasdf"
    #print(g.allSearchRows)
    #print(f"g.allSearchRows={g.allSearchRows}")

    return render_template(
        "index.html", allSearchRows=g.allSearchRows, headings=g.searchFields, afterResults=False, results=None
    )


@app.route("/addCash", methods=["GET", "POST"])
@login_required
def addCash():
    """Add Cash from a financial Institution"""

    # institutionsTableName = g.institutionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user
    userHasInstitutions = CheckInstitutions(
        session["institutionsTableName"]
    )  # this also sets g.userInstitutions
    # print( "back to addCash()" )
    # print( "userHasInstitutions is " + str( userHasInstitutions ) )

    """*****************************GET METHOD HERE*************************"""
    if request.method == "GET":
        """Build a list of Financial Institutions to pick from in HTML"""
        # print( "GET" )
        if not userHasInstitutions:
            flash(g.addFinancialInstitutionsMsg)
            return render_template("addCash.html")

        if not g.userInstitutions:  # this global variable is set by CheckInstitutions()
            flash(g.addFinancialInstitutionsMsg)
            return render_template("addCash.html")

        return render_template("addCash.html", userInstitutions=g.userInstitutions)

    """*****************************POST METHOD HERE*************************"""
    if request.method == "POST":
        """0. Verify that correct data has been submitted."""
        # print( "POST" )
        if not userHasInstitutions:
            flash(g.addFinancialInstitutionsMsg)
            return render_template(
                "addInstitution.html", listOfInstitutions=GetListOfInstitutions()
            )

        chosenInstitutionAccount = request.form.get("institutionAccount")
        if chosenInstitutionAccount is None:
            return apology("MISSING SOURCE ACCOUNT", 400)

        cashAmount = request.form.get("cashAmount")
        if not cashAmount:
            return apology("CASH MUST BE POSITIVE", 400)

        if int(cashAmount) < 1:
            return apology("CASH MUST BE POSITIVE", 400)

        """Check if user has enough cash in the source account"""
        isEnoughCashInSourceAccount, error = DoesUserHaveEnoughCash(
            chosenInstitutionAccount, cashAmount, session["institutionsTableName"]
        )

        if error != 0:
            return apology(isEnoughCashInSourceAccount, error)

        if not isEnoughCashInSourceAccount:
            return apology("Not enough cash in user's account", 400)

        """Initiate transfer of cashAmount from user's account to CS50 cash"""
        response = TransferCashFromInstitution(
            g.handshakeInstructions
        )  # This is fake at the moment
        # print( "back to addCash()" )
        if not response:
            return apology(
                "Failed to transfer cash from " + chosenInstitutionAccount, 400
            )
        # print( "response from TransferCashFromInstitution() " + str( response ) )

        """Transfer was successful, so update users table"""
        print(f"cashAmount={str(cashAmount)}")
        cash, error = UpdateCashValueInUsersTable(g.usersTableName, session["user_id"], cashAmount)
        if error != 0:
            return apology(cash, error)

        return redirect("/")

    return apology("A method other than GET or POST was used to reach this route", 400)


@app.route("/addInstitution", methods=["GET", "POST"])
@login_required
def addInstitution():
    # print( "addInstitution()" )


    # institutionsTableName = g.institutionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user
    userHasInstitutions = CheckInstitutions(
        session["institutionsTableName"]
    )  # this also sets userInsitutions variable
    # print( "back from CheckInstitutions()" )
    if request.method == "GET":
        # print( "GET" )
        return render_template(
            "addInstitution.html", listOfInstitutions=GetListOfInstitutions()
        )

    if request.method == "POST":
        """Add institution and account number to institution table for this user"""
        duplicateAccount = (
            False  # We do not want to allow the user to add the same exact account
        )

        """Check for form input correctness"""
        institutionName = request.form.get("institutionName")

        if not institutionName:
            return apology(g.errorProvideInstitutionName, 400)

        accountNumber = request.form.get("accountNumber")
        if not accountNumber:
            return apology(g.errorAccountNumberMissing, 400)

        """Verify that this institution with the exact same accountNumber doesn't already exist"""
        if userHasInstitutions:
            # it means g.userInstitutions is already set by CheckInstitutions()
            # print( g.userInstitutions )

            """We want to check the current g.userInstitutions list for the presence of a dictionary element that matches institutionName and accountNumber"""
            # print( "iterating over the g.userInstitutions" )
            for e in g.userInstitutions:
                # print( str( e ) + "\te's institutionName key=" + str( e["institutionName"] ) + "institutionName=" + str( institutionName ) + "\te's accountNumber=" + str( e["accountNumber"] ) + " accountNumber = " + accountNumber )
                if e["institutionName"] == institutionName and int(
                    e["accountNumber"]
                ) == int(
                    accountNumber
                ):  # had to make sure e["accountNumber"] was processed with str() or accountNumber as int()

                    duplicateAccount = True
                    break

        if duplicateAccount:
            return apology(g.errorDuplicateAccount, 400)

        g.handshakeInstructions = (
            "Special handshake instructions to connect to "
            + institutionName
            + f" acct: {accountNumber}"
        )  # eventually set this up correctly for it to work in the real world?
        response = g.db.execute(
            "CREATE TABLE IF NOT EXISTS ? ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                institutionName TEXT NOT NULL, \
                accountNumber INTEGER NOT NULL, \
                handshakeInstructions TEXT NOT NULL \
                )",
            session["institutionsTableName"]
        )  # g.db.execute can return an empty list, but not None

        if not response:
            return apology(g.errorCreatingInstitutionsTableMsg, 400)

        """Now add the new institution to the table"""
        id = g.db.execute(
            "INSERT INTO ? ( \
                institutionName, accountNumber, handshakeInstructions \
                ) \
            VALUES( ?, ?, ? )",
            session["institutionsTableName"],
            institutionName,
            accountNumber,
            g.handshakeInstructions,
        )

        if not id:
            return apology(g.errorInsertInstitutionMsg, 400)

        g.userInstitutions = g.db.execute(
            "SELECT institutionName, accountNumber \
            FROM ?",
            session["institutionsTableName"],
        )

        if not g.listOfInstitutions:
            return apology("couldn't retrieve list of institutions for this user", 400)
        # print( g.listOfInstitutions )

        flash(g.institutionAddedMsg)
        return render_template("addCash.html", userInstitutions=g.userInstitutions)


@app.route("/addInstitutionFromCash", methods=["GET", "POST"])
@login_required
def addInstitutionFromCash():
    # print( "addInstitutionsFromCash()" )

    """Got here because the user pressed Add Insitution button on addCash.html"""

    return render_template(
        "addInstitution.html", listOfInstitutions=GetListOfInstitutions()
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # print( "buy()" )
    # transactionsTableName not needed as we have a helper function called BuyShares() now
    """Buy shares of stock"""
    """&&&&&&&&&&&&&&&&&&&&&&&& GET METHOD &&&&&&&&&&&&&&&&&&&&&&&&&&"""
    if request.method == "GET":
        return render_template("buy.html")

    """&&&&&&&&&&&&&&&&&&&&&&&& POST METHOD &&&&&&&&&&&&&&&&&&&&&&&&&&"""
    if request.method == "POST":
        """0. Verify that correct data has been submitted."""
        currSymbol = request.form.get("symbol")

        if currSymbol is None:
            return apology("MISSING SYMBOL, 400")

        numShares = request.form.get("shares")

        if numShares == "" or numShares == 0:
            return apology("TOO FEW SHARES", 400)

        if "-" in numShares or "." in numShares or not numShares.isnumeric():
            return apology("SHARES MUST BE A POSITIVE INTEGER", 400)

        purchaseTotal, error = BuyShares(currSymbol, numShares)

        if 0 != error:
            return apology(purchaseTotal, error)

        flash(f"Bought {numShares} of {currSymbol} for {usd( purchaseTotal )} !")
        return redirect("/")

    return apology("A method other than GET or POST was used to reach this route", 400)


@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():

    if request.method == "POST":
        oldPasswordAttempt = request.form.get("oldPassword")

        if not oldPasswordAttempt:
            return apology(
                "MISSING OLD PASSWORD", 400
            )

        oldPasswordHash = g.db.execute(
            "SELECT hash \
            FROM ? \
            WHERE id =?",
            g.usersTableName,
            session["user_id"],
        )

        if not check_password_hash(oldPasswordHash[0]["hash"], oldPasswordAttempt):
            return apology("OLD PASSWORD INCORRECT", 400)

        newPassword = request.form.get("newPassword")
        if not newPassword:
            return apology("MISSING NEW PASSWORD", 400)

        confirmation = request.form.get("confirmation")
        if not confirmation or confirmation != newPassword:
            return apology("PASSWORDS DON'T MATCH", 400)

        if newPassword == oldPasswordAttempt:
            return apology("NEW PASSWORDS MATCHES OLD PASSWORD", 400)

        hash = generate_password_hash(newPassword, method="scrypt", salt_length=16)
        response = g.db.execute(
            "UPDATE ? \
            SET hash = ? \
            WHERE id = ?",
            g.usersTableName,
            hash,
            session["user_id"],
        )

        if not response:
            return apology("SERVER ERROR. COULD NOT UPDATE NEW PASSWORD", 400)

        flash("Password Changed!")
        return redirect("/")

    """ GET Method assumed """
    return render_template("changePassword.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # transactionsTableName = g.transactionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user

    if request.method == "GET":
        history = g.db.execute(
            "SELECT symbol, numShares AS shares, priceAtTransaction AS price, transactionTimeMs AS transactionDatetime \
            FROM ?",
            session["transactionsTableName"],
        )

        for row in history:  # will not iterate through an empty list

            row["symbol"] = row["symbol"].upper()  # just in case
            row["price"] = usd(row["price"])
            row["transactionDatetime"] = datetime.datetime.fromtimestamp(
                row["transactionDatetime"]
            )  # had to google about converting ms to time and found "fromtimestamp"
            # the amazing thing is that what gets sent into history.html is literally a function datetime.datetime(year,month,day,hours,minutes,seconds)

        return render_template("history.html", history=history)

    return apology(
        "The page was accessed with a method that's not supported (supported method: GET)",
        400
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    '''Log user in'''
    print( "hello1!!!!!" )

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        session["name"] = request.form.get("username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)


        response = g.db.execute(
            "CREATE TABLE IF NOT EXISTS ? ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, \
                username TEXT NOT NULL, \
                hash TEXT NOT NULL, \
                cash NUMERIC NOT NULL \
                )",
            g.usersTableName
            )

        print(response)
        # Query database for username
        rows = g.db.execute(
            "SELECT * \
            FROM ? \
            WHERE username = ?",
            g.usersTableName,
            request.form.get("username"),
        )  # g.db.execute does not return None, but an empty list

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["transactionsTableName"] = g.transactionsTableNameRoot + str(
            session["user_id"]
        )
        session["institutionsTableName"] = g.institutionsTableNameRoot + str(
            session["user_id"]
        )

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET or some other method (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        returnval = lookup(request.form.get("symbol"))  # lookup can return None

        if returnval is None:
            return apology("INVALID SYMBOL", 400)

        else:
            return render_template(
                "quoted.html", symbol=returnval["symbol"], price=usd(returnval["price"])
            )

    return apology("A method other than GET or POST was used to reach this route", 400)


@app.route("/register", methods=["GET", "POST"])
def register():

    id = -1  # make sure id is initialized to an impossible value
    """Register user"""
    """(register.html page is based on login.html)"""

    if request.method == "POST":
        username = request.form.get("username")

        if not username:
            return apology(
                "MISSING USERNAME", 400
            )  # 400: The server cannot or will not process the request due \
            # to something that is perceived to be a client error (e.g., \
            # malformed request syntax, invalid request message framing, or deceptive request routing).

        response = g.db.execute(
            "CREATE TABLE IF NOT EXISTS ? ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, \
                username TEXT NOT NULL, \
                hash TEXT NOT NULL, \
                cash NUMERIC NOT NULL \
                )",
            g.usersTableName
            )

        #print("response from g.db.execute()")
        #print(response)

        id = g.db.execute(
            "SELECT id \
            FROM ? \
            WHERE username = ?",
            g.usersTableName,
            username,
        )

        if id:
            return apology("USERNAME TAKEN", 400)

        password = request.form.get("password")

        if not password:
            return apology("MISSING PASSWORD", 400)

        confirmation = request.form.get("confirmation")

        if not confirmation or confirmation != password:
            return apology("PASSWORDS DON'T MATCH", 400)

        hash = generate_password_hash(password, method="scrypt", salt_length=16)
        id = g.db.execute(
            "INSERT INTO ? ( \
                username, hash \
                ) \
            VALUES( ?, ? )",
            g.usersTableName,
            username,
            hash
        )
        session["user_id"] = id  # log in the user right away
        session["name"] = username
        session["transactionsTableName"] = g.transactionsTableNameRoot + str(
            session["user_id"]
        )
        session["institutionsTableName"] = g.institutionsTableNameRoot + str(
            session["user_id"]
        )

        return redirect("/")

    return render_template("register.html")


@app.route("/searchPeople", methods=["GET", "POST"])
@login_required
def searchPeople():
    # print( "searchPeople()" )

    NMessage(f"{g.allSearchRows}")

    if request.method == "POST":

        for c in range(1, g.initNumSearchRows + 1):
            colDict = g.allSearchRows[c - 1]
            YMessage(f"colDict={colDict}", logFile=None, logOption=LOG)
            includeRefs = False

            if request.form.get('incl_refs') == "on":
                includeRefs = True

            for i in range(0, len(colDict)):
                #print(g.searchFields[i]['name'] + str(c))
                g.allSearchRows[c - 1][i]['valFrom'] = request.form.get(g.searchFields[i]['name'] + str(c))
                g.allSearchRows[c - 1][i]['ph1'] = g.allSearchRows[c - 1][i]['valFrom']
                #print(g.searchFields[i]['name'] + str(c))
                NMessage(f"g.allSearchRows[c - 1][i]['valFrom']={g.allSearchRows[c - 1][i]['valFrom']}", logFile=None, logOption=LOG)

        for dict in g.tempSearchFields: # let's make sure to reset every value here
            dict['valFrom'] = ''
            dict['valTo'] = ''

        NMessage(f"allSearchRows={g.allSearchRows}", logFile=None, logOption=LOG)

        # Now we call helper functions to retrieve data from the database based on the filled in search fields
        g.parsedSearchResults, g.chosenColsHeads, error = mg.GetDbDataFromSearch(g.db,
                                                                    mgv.t['peopleTableName'],
                                                                    g.allSearchRows,
                                                                    g.tempSearchFields, # .copy() doesn't appear to give me a blank slate!
                                                                    g.htmlSearchNamePrefixLen,
                                                                    g.htmlResultsNamePrefixLen,
                                                                    includeRefs
                                                                    )
        YMessage(f"g.parsedSearchResults={g.parsedSearchResults}", logFile=None, logOption=LOG)
        #parsedSearchResults = mg.ParseSearchResults(searchResults) # This might be important if I allow to reorder the columns later in the game


        if error:
            return apology(f"{g.parsedSearchResults}", error)

        else: # we seem to have real data we should try to display in the table
            return render_template(
               "index.html", allSearchRows=g.allSearchRows, headings=g.searchFields, afterResults=True, searchResults=g.parsedSearchResults, chosenColsHeads=g.chosenColsHeads
            )


    # End of request.method == POST
    return apology(f"CALLED searchPeople() - with a method other than POST")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # transactionsTableName = g.transactionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user

    """If DATA was COLLECTED from the SELL page"""
    if request.method == "POST":
        symbolResponse = request.form.get(
            "symbol"
        )  # request.form.get can return None or a string

        if symbolResponse is None:
            return apology("MISSING SYMBOL", 400)
        symbol = symbolResponse

        if request.form.get("shares") == "":
            return apology("MISSING SHARES", 400)

        sharesToSell = int(request.form.get("shares"))
        if sharesToSell < 1:
            return apology("SHARES MUST BE POSITIVE", 400)

        totalPurchasePrice, error = SellShares(symbol, sharesToSell)
        if error != 0:
            return apology(totalPurchasePrice, error)

        flash(
            f"Sold {sharesToSell} share(s) of {symbol} for {usd( totalPurchasePrice )}"
        )
        return redirect("/")

    """ If SELL page was simply requested """
    """ We need to populate the pull down menu with the """
    """ choice of all the symbols the user currently owns """
    """ that means that the total sum of numShares == 0 """
    if request.method == "GET":
        shares = g.db.execute(
            "SELECT UPPER( symbol ) symbol \
            FROM ? AS transactions \
            GROUP BY symbol \
            HAVING SUM( numShares ) <> 0",
            session["transactionsTableName"],
        )  # HAVING is important to avoid trying to sell non-existing shares

        return render_template("sell.html", shares=shares)


@app.route("/updateDatabase", methods=["GET", "POST"])
@login_required
def updateDatabase():
    """update the database if the user submitted new results"""

    if request.method == "POST":
        request_form = request.form
        YMessage("_________________________updatePeople__________________________", logOption=LOG)
        YMessage(f"request_form = {request_form}", logOption=LOG)
        YMessage("------------", logOption=LOG)
        YMessage(f"g.refreshFormCheck={g.refreshFormCheck}", logOption=LOG)

        if not g.refreshFormCheck:
            g.refreshFormCheck = request_form

        else:

            if g.refreshFormCheck == request_form:
                YMessage("------------*********REFRESH has been triggered or same form data submitted as already was*************************-----------------------", logOption=LOG)
                YMessage(f"request_form = {request_form}", logOption=LOG)
                YMessage("------------", logOption=LOG)
                YMessage(f"g.refreshFormCheck={g.refreshFormCheck}", logOption=LOG)
                flash("You refreshed this page and nothing changed!")
                return render_template(
                    "index.html", allSearchRows=g.allSearchRows, headings=g.searchFields, afterResults=True,
                    searchResults=g.parsedSearchResults, chosenColsHeads=g.chosenColsHeads
                    )

            else:
                g.refreshFormCheck = request_form

        YMessage(f"g.parsedSearchResults={g.parsedSearchResults}", logOption=LOG)
        i = 0 # index of parsedSearchResults rows
        for row in g.parsedSearchResults: # every row of search Reults
            for key in row: #going through each box of the results table in one row
                YMessage(f"key={key}", logOption=LOG)

                if key == 'personId': # We use this to set the names of the html input box of other values (we don't display this internal number)
                    continue
                # ex. currName = "xxxxpeopleNamesFmlEngT_lstName__personId619"

                if row[key] == None:
                    origval = ""

                else:
                    origval = str(row[key])

                currName = key + "__personId" + str(row['personId']) + "__origval" + origval #curr html table cell name

                if not "_url" in key:
                    currValue = request.form.get(currName)

                else: # we are dealing with the url column that isn't an input box so it doesn't have a "value"
                      # we set currValue to "origval" (MAGIC VALUE!!!) part of the name
                    origvalstr = '__origval'
                    currValue = currName[currName.find(origvalstr) + len(origvalstr):]

                YMessage(f"currName={currName} currValue={currValue}", logOption=LOG)

                if origval != currValue: # value was changed by the user, need to update the database
                    underscorePos = key.find("_") # this will be the first _ character in the long input box name
                    dbTableName = key[g.htmlResultsNamePrefixLen:underscorePos]
                    colName = key[underscorePos + 1:]

                    YMessage(f"origval={row[key]} currValue={currValue} key={key} currName={currName} dbTableName={dbTableName} colName={colName}", logOption=LOG)
                    dictOfDbValues = {'tableName': dbTableName, 'colName': colName, 'personId': row['personId'], 'newVal': str(currValue)}

                    if origval != "": # the user changed an existing value
                        g.updateTheseRows.append(dictOfDbValues) # the assumption is that everything went well

                    else:  #origval != currValue and origval == "": # the user input a value that didn't exist before
                        g.insertTheseRows.append(dictOfDbValues)

                    # and let's update the view of the results as well
                    g.parsedSearchResults[i][key] = currValue
                    # the actual update will happen when we have gathered everything in g.updateTheseRows

            i = i + 1
        YMessage(f"g.updateTheseRows={g.updateTheseRows}", logOption=LOG)
        YMessage(f"g.insertTheseRows={g.insertTheseRows}", logOption=LOG)

        if not 'name' in session:
            message = "Programming error, I don't know your username. Logout then log back in so that you can see 'Welcome, <your username>."
            error = 500
            return apology(message, error)

        message, error = mg.UpdateDbDataFromHtml(g.db, g.updateTheseRows, g.parsedSearchResults, g.htmlResultsNamePrefixLen, session['name'])
        if 0 != error:
            return apology(message, error)
        message, error = mg.InsertDbDataFromHtml(g.db, g.insertTheseRows, g.parsedSearchResults, g.htmlResultsNamePrefixLen, session['name'])

        if 0 != error:
            return apology(message, error)

        flash(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+":") # should display how many records were updated
        flash(mgv.recordsInsertedMessage ) # should display how many records were updated
        flash("\n") # It ignores new lines
        flash(mgv.recordsUpdatedMessage) # should display how many records were inserted
        g.updateTheseRows.clear()
        g.insertTheseRows.clear()
        mgv.numRecordsUpdated = 0
        mgv.numRecordsInserted = 0
        mgv.recordsUpdatedDetails = ""
        mgv.recordsUpdatedMessage = ""
        mgv.recordsInsertedDetails = ""
        mgv.recordsInsertedMessage = ""

        YMessage(f"g.parsedSearchResults={g.parsedSearchResults}", logFile=None, logOption=LOG)
        NMessage(f"allSearchRows={g.allSearchRows}", logFile=None, logOption=LOG)

        # Now we call helper functions to retrieve data from the database based on the filled in search fields


        return render_template(
           "index.html", allSearchRows=g.allSearchRows, headings=g.searchFields, afterResults=True, searchResults=g.parsedSearchResults, chosenColsHeads=g.chosenColsHeads
        )

    return apology("database update feature has not been implemented yet", 400)
