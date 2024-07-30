import csv
import datetime
import pytz
import requests
import urllib
import uuid
import appGVars as g
from flask import Flask, flash, redirect, render_template, request, session # This gives us access to session here, it seems

from functools import wraps



def apology( message, code=400 ):
    """Render message as an apology to user."""
    #print( "inside apology()" )
    def escape( s ):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ( "-", "--" ),
            ( " ", "-" ),
            ( "_", "__" ),
            ( "?", "~q" ),
            ( "%", "~p" ),
            ( "#", "~h" ),
            ( "/", "~s" ),
            ( '"', "''" ),
        ]:
            s = s.replace( old, new )
        return s

    #bottom = escape( message )
    #print( "bottom =")
    #print( bottom )
    return render_template( "apology.html", top=code, bottom=escape( message ) ), code


def login_required( f ):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps( f )
    def decorated_function( *args, **kwargs ):
        if session.get( "user_id" ) is None:
            return redirect( "/login" )
        return f( *args, **kwargs )

    return decorated_function


def lookup( symbol ):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now( pytz.timezone( "US/Eastern" ) )
    #print( "inside lookup" )
    #print( end )
    #print( int( end.timestamp() ) )

    start = end - datetime.timedelta( days=7 )

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus( symbol )}"
        f"?period1={int( start.timestamp() )}"
        f"&period2={int( end.timestamp() )}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str( uuid.uuid4() )},
            headers={"Accept": "*/*", "User-Agent": request.headers.get( "User-Agent" )},
        )
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list( csv.DictReader( response.content.decode( "utf-8" ).splitlines() ) )
        price = round( float( quotes[-1]["Adj Close"] ), 2 )
        return {"price": price, "symbol": symbol}
    except ( KeyError, IndexError, requests.RequestException, ValueError ):
        return None


def usd( value ):
    """Format value as USD."""
    return f"${value:,.2f}"


def CheckInstitutions(institutionsTableName):
    
    # print( "CheckInstitutions()" )
    # print( "institutionsTableName=" + institutionsTableName )
    userHasInstitutions = g.db.execute(
        "SELECT name \
        FROM sqlite_master \
        WHERE type='table' AND name = ?",
        institutionsTableName,
    )  # This checks if the table exists
    # print( "userHasInstitutions = " + str( userHasInstitutions ) )
    if not userHasInstitutions:
        return False

    g.userInstitutions = g.db.execute(
        "SELECT institutionName, accountNumber \
        FROM ? \
        GROUP BY institutionName",
        institutionsTableName,
    )
    # print( "g.userInstitutions = " + str( g.userInstitutions ) )
    if not g.userInstitutions:
        return False

    return True

