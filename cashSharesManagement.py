"""Helpers"""
import appGVars as g    
from helpers import *

def BuyShares(currSymbol, numShares):
    # print( "BuyShares()" )
    # transactionsTableName = g.transactionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user
    totalPurchasePrice = 0
    """ Error Checking """
    if int(numShares) < 1:
        return (
            f"BuyShares() must be called with a positive number of share, not {numShares}",
            400,
        )

    """1. Make sure currSymbol exists and get its share price """

    returnval = lookup(currSymbol)  # lookup can return None

    if returnval is None:
        return f"SYMBOL {currSymbol} doesn't exist in the market", 400

    pricePerShare = returnval["price"]
    totalPurchasePrice = float(numShares) * float(pricePerShare)

    """2. Get How Much Cash the user has"""
    cash, error = GetUserCashAmount(g.usersTableName)

    if error != 0:
        return apology(cash, error)
    
    """3. Compare total cost to cash and produce the right reaction"""
    if cash < totalPurchasePrice:
        return "CAN'T AFFORD", 400

    # print( f"Here presumably, the handshake with the stockmarket takes place where the user's cash is sent there, and {numShares} of {currSymbol} are sent back to CS50's server" )
    """4. Update the transactions database"""
    """Create table if table doesn't exist"""
    response = g.db.execute(
        "CREATE TABLE IF NOT EXISTS ? ( \
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, \
            symbol TEXT NOT NULL, \
            numShares INTEGER NOT NULL, \
            priceAtTransaction NUMERIC NOT NULL, \
            transactionTimeMs INTEGER NOT NULL \
            )",
        session["transactionsTableName"]
    )  # g.db.execute can return an empty list, but not None

    if not response:
        return "Couldn't create transactions database for this user", 400

    timeNowInMs = int((datetime.datetime.now(pytz.timezone("US/Eastern"))).timestamp())

    # print( f"{session["transactionsTableName"]}, {totalPurchasePrice}" )
    msg, error = UpdateTransactionTable(
        session["transactionsTableName"],
        currSymbol,
        sharesDelta=numShares,
        totalPurchasePrice=totalPurchasePrice,
        timeNowInMs=timeNowInMs,
    )

    if error != 0:
        return apology(msg, error)
    
    """5. Update the users database cash value"""
    # print( f"totalPurchasePrice={totalPurchasePrice}" )
    cash, error = UpdateCashValueInUsersTable(
        g.usersTableName, session["user_id"], cashAmountDelta=-totalPurchasePrice
    )

    if error != 0:
        return apology(cash, error)
    
    return totalPurchasePrice, 0  # 0 is "no error"


# Fake function for now
def DoesUserHaveEnoughCash(institutionAccount, cashAmount, institutionsTableName):
    
    # print( "DoesUserHaveEnoughCash()" )
    institutionAccount = institutionAccount[:-1]
    accInfo = institutionAccount.split(" (")
    # print( accInfo )
    # print( accInfo[0] + " " + accInfo[1] )
    g.handshakeInstructions = g.db.execute(
        "SELECT handshakeInstructions \
        FROM ?",
        institutionsTableName,
    )

    if not g.handshakeInstructions:
        return "Could not access user's institutions information", 400

    # print( "Making an API call with " + str( g.handshakeInstructions ) +  " to retrieve the amount of cash the user has. TBD")
    retrievedCash = 1000000  # for now just a simple constant
    if int(cashAmount) > retrievedCash:
        return False, 0

    return True, 0



def GetListOfInstitutions():
    # later this function would make actual API calls to databases provided by whatever services keep track of all the financial institutions
    # Right now, hardcoded
    
    return g.listOfInstitutions


def GetNumSharesForSymbol(currSymbol):
    # print( "GetNumSharesForSymbol()" )
    # transactionsTableName = g.transactionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user

    response = g.db.execute(
        "SELECT sum( numShares ) numShares \
        FROM ? \
        WHERE symbol = ? \
        GROUP BY symbol",
        session["transactionsTableName"],
        currSymbol.upper(),
    )  # g.db.execute never responds with None, but an empty List (check for with if not list:)

    if not response:
        return g.errorSelectFromTransactionTable + session["transactionsTableName"], 400

    userCurrSharesOwned = response[0]["numShares"]
    # print( "userCurrSharesOwned=" + str( userCurrSharesOwned ) )

    return userCurrSharesOwned, 0


def GetUserCashAmount(usersTableName):
    cashResponse = g.db.execute(
        "SELECT cash \
        FROM ? \
        WHERE id =?",
        usersTableName,
        session["user_id"],
    )

    if not cashResponse:
        return "user was not found", 400

    cash = cashResponse[0]["cash"]

    return cash, 0


def SellShares(symbol, sharesToSell):
    # print( f"SellShares( {symbol}, {sharesToSell} ) - start" )
    totalPurchasePrice = 0
    # transactionsTableName = g.transactionsTableNameRoot + str( session["user_id"] ) #The name of the table for this user
    """ First Make sure the user actually owns this symbol """
    checkShare = g.db.execute(
        "SELECT symbol \
            FROM ? \
            WHERE symbol = ? \
            GROUP BY symbol",
        session["transactionsTableName"],
        symbol.upper(),
    )  # must use symbol.upper() to make sure it's the same case, even though supposedly sql is case insensitive
    # If symbol not in list, checkShare is [] but for some reason checkShare is None doesn't work - probably if doesn't exist period

    if not checkShare:
        return "SYMBOL NOT OWNED", 400  # copied from finance.cs50.net

    userCurrSharesOwned, error = GetNumSharesForSymbol(symbol)

    if error != 0:
        return apology(userCurrSharesOwned, error)
    
    if 0 == userCurrSharesOwned:
        return (
            "SYMBOL NOT OWNED",
            400,
        )  # very important that this works for a huge number of transactions

    if int(userCurrSharesOwned) < int(sharesToSell):
        """ It was here that I found out that doing "return apology(msg, errorcode )" from within
            this function (SellShares) wouldn't render apology.html in the browser
            but instead return the html code + error code tuple back to the caller ( sell() )
        """
        return "TOOO MANY SHARES", 400
        

    """Update the transactions database"""
    returnval = lookup(symbol)  # lookup can literally return None
    if returnval is None:
        return "INVALID SYMBOL", 400

    price = returnval["price"]

    totalPurchasePrice = float(sharesToSell) * float(price)
    timeNowInMs = int((datetime.datetime.now(pytz.timezone("US/Eastern"))).timestamp())
    msg, error = UpdateTransactionTable(
        session["transactionsTableName"],
        symbol,
        sharesDelta=-sharesToSell,
        totalPurchasePrice=totalPurchasePrice,
        timeNowInMs=timeNowInMs,
    )
    if error != 0:
        return apology(msg, error)
    
    """Update users database - cash field"""
    cash, error = UpdateCashValueInUsersTable(
        g.usersTableName, session["user_id"], cashAmountDelta=totalPurchasePrice
    )

    if error != 0:
        return apology(cash, error)
    
    return totalPurchasePrice, 0


def TransferCashFromInstitution(handshakeInstructions):
    # fake function for now
    print("TransferCashFromInstitution()")
    print(
        "Sending handshake instructions "
        + str(handshakeInstructions)
        + " to the financial institution, waiting for response...."
    )

    return True


def UpdateCashValueInUsersTable(usersTableName, userId, cashAmountDelta):
    cashValue = 0
    
    oldCash, error = GetUserCashAmount(usersTableName)
    
    if error != 0:
        return oldCash, error
    newCash = float(oldCash) + float(cashAmountDelta)

    response = g.db.execute(
        "UPDATE ? \
        SET cash = ? \
        WHERE id = ?",
        g.usersTableName,
        newCash,
        userId,
    )
    # print( response )
    if not response:
        return "USER CASH UPDATE FAILED IN LOCAL DATABASE. CONTACT ADMINISTRATOR.", 400

    response = g.db.execute(
        "SELECT cash \
        FROM ? \
        WHERE id = ?",
        g.usersTableName,
        userId,
    )

    if not response:
        return "FAILED TO ACCESS THE USERS DATABASE. CONTACT ADMINISTRATOR", 400

    cashValue = response[0]["cash"]
    if float(cashValue) != float(newCash):
        return (
            "FAILED TO SET THE NEW CASH VALUES IN THE USERS DATABASE. CONTACT ADMINISTRATOR",
            400,
        )

    return cashValue, 0


def UpdateTransactionTable(
    transactionsTableName, symbol, sharesDelta, totalPurchasePrice, timeNowInMs
):

    response = g.db.execute(
        "INSERT INTO ? ( \
            symbol, numShares, priceAtTransaction, transactionTimeMs \
            ) \
        VALUES( ?, ?, ?, ? )",
        transactionsTableName,
        symbol.upper(),
        sharesDelta,
        totalPurchasePrice,
        timeNowInMs,
    )

    # print( response ) #should return newly minted id
    if not response:
        return apology(
            "FAILED TO INSERT LAST TRANSACTION INTO INTERNAL TABLE. CONTACT ADMINISTRATOR.",
            400,
        )

    id = response
    response = g.db.execute(
        "SELECT priceAtTransaction \
        FROM ? \
        WHERE id = ?",
        transactionsTableName,
        id,
    )

    if not response:
        return "Failed to verify if the transaction table was updated correctly.", 400

    return "all good", 0


"""I made a mistake and returned a "dictionary-formatted" string from an HTML form.
        i.e. A string that looks like a dictionary, not the actual dictionary
        Just in case, here is how you turn the newstring (that has single quotes in it)
        into a regular dictionary (and then retrieve a "symbol" key from it )
        newString = symbolResponse.replace("'", '"')
        dict = ast.literal_eval( newString ) #this actually works, but I should review what the lecture said about json
        symbol = dict["symbol"] #this gets us a symbol
"""
