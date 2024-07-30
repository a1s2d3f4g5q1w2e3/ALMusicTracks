// Just a test file to see if submit50 will actually include it this time
var yearsUpToNow = new Date().getFullYear();
//window.alert(yearsUpToNow)
//The script below is for sorting tables
function getElements( id ) { // borrowed from https://www.w3schools.com/lib/w3.js
    if ( typeof id == "object" ) {
        return [id];
    } else {
        return document.querySelectorAll( id );
    }
}

function sortHTML(id, sel, sortvalue, sortAlphaNum=0) { // borrowed from https://www.w3schools.com/lib/w3.js and expanded
    // window.alert("id=" + id + "\nsel=" + sel + "\nsortvalue=" + sortvalue + "\nsortAlphaNum=" + sortAlphaNum);
    //let startTime = new Date(); let startTimeMillis = startTime.getTime();
    saveSort = 0; // for cases where we set it to 1000 - you'll see
    // sortAlphaNum
    //  0=alpha,
    //  1=integer numeric incl negative
    //  2=month/date 3=month/date/year etc
    //  100=$ currency with commas and periods for cents
    // +1000 means value inside input

    var a, b, i, ii, y, bytt, v1, v2, cc, j;
    a = getElements(id);
    // window.alert("a=" + a + " a[0]=" + a[0]);
    //b = a[0].querySelectorAll(sel); // 20240708_1143: This is failing for the composers table...
    /*
    window.alert(">a=" + a + "\n>a.length = " + a.length + "\n" +
        ">b.length=" +
            b.length + "\n" +
            "> b[0].querySelector( sortvalue )=" +
            b[0].querySelector( sortvalue ) + "\n" +
        "> b[0].querySelector( sortvalue ).childElementCount=" +
            b[0].querySelector( sortvalue ).childElementCount + "\n" +
            "> b[0].querySelector( sortvalue ).children=" +
            b[0].querySelector( sortvalue ).children + "\n" +
            "> b[0].querySelector( sortvalue ).children.length=" +
            b[0].querySelector( sortvalue ).children.length + "\n" +
            "> b[0].querySelector( sortvalue ).children[0].value=" +
            b[0].querySelector( sortvalue ).children[0].value + "\n"
        );
    */
    oneBillion = 1000000000;
    for ( i = 0; i < a.length; i++ ) {
        for ( j = 0; j < 2; j++ ) {
            cc = 0;
            y = 1;
            while ( y == 1 ) {
                y = 0;
                b = a[i].querySelectorAll( sel );
                //window.alert( "b[0]=" + b[0] );
                for ( ii = 0; ii < ( b.length - 1 ); ii++ ) {
                    bytt = 0;
                    if ( sortvalue ) {
                        if ( sortAlphaNum >= 1000 ) {
                            saveSort = 1000;

                            v1 = b[ii].querySelector( sortvalue ).children[0].value;
                            v2 = b[ii + 1].querySelector( sortvalue ).children[0].value;
                            sortAlphaNum = sortAlphaNum - 1000;

                            // console.log( "1000-v1=" + v1 + "1000-v2=" + v2 )
                        }
                        else {
                            v1 = b[ii].querySelector( sortvalue ).innerText;
                            v2 = b[ii + 1].querySelector( sortvalue ).innerText;

                            // console.log( "000-v1=" + v1 + "000-v2=" + v2 )
                        }
                    } else {
                        v1 = b[ii].innerText;
                        v2 = b[ii + 1].innerText;
                    }
                    if ( sortAlphaNum == 0) {
                        sortAlphaNum = sortAlphaNum + saveSort;
                    }
                    if ( sortAlphaNum == 1 ) { // we need to temporarily remove the - (minus) sign and then padd the numbers
                        sortAlphaNum = sortAlphaNum + saveSort;
                        //console.log( 'v1 is ' + v1 );
                        v1 = parseInt( v1, 10 ) + oneBillion;
                        v2 = parseInt( v2, 10 ) + oneBillion;
                        //console.log( '1v1:' + v1 );
                        v1 = v1.toString().padStart( 15, "0" );
                        v2 = v2.toString().padStart( 15, "0" );
                        //window.alert( 'v1:' + v1 );
                        //console.log( '1-v1:' + v1 );
                    }
                    if ( sortAlphaNum == 2 ) { // we need to zero-pad the date values so they get sorted correctly
                        sortAlphaNum = sortAlphaNum + saveSort;
                        v1 = ExtractFromString( v1, -1, "/" ).padStart( 2, "0" ) + "/" + ExtractFromString( v1, "/", -1 ).padStart( 2, "0" )
                        v2 = ExtractFromString( v2, -1, "/" ).padStart( 2, "0" ) + "/" + ExtractFromString( v2, "/", -1 ).padStart( 2, "0" )
                    }
                    if ( sortAlphaNum == 100 ) { // we need to remove the symbol, all commas and then pad the float number with 8 zeros
                        sortAlphaNum = sortAlphaNum + saveSort;
                        v1 = v1.substring( 1 ).padStart( 13, "0" );
                        v2 = v2.substring( 1 ).padStart( 13, "0" );
                    }
                    v1 = v1.toLowerCase();
                    v2 = v2.toLowerCase();
                    //console.log( "2v1=" + v1 )
                    if ( ( j == 0 && ( v1 > v2 ) ) || ( j == 1 && ( v1 < v2 ) ) ) {
                        bytt = 1;
                        break;
                    }
                } // end of inner inner for loop
                if ( bytt == 1 ) {
                    b[ii].parentNode.insertBefore( b[ii + 1], b[ii] );
                    y = 1;
                    cc++;
                }
            } // end of inner while loop
            if ( cc > 0 ) { break; }
        } // end of inner for loop
    } // end of outer for loop
    //let endTime = new Date(); let endTimeMillis = endTime.getTime();
    //window.alert( endTimeMillis - startTimeMillis )
} // end of sortHTML function

function ExtractFromString( v1, fromString, toString ) {
    extractedString = "";
    let positionFrom;
    if ( -1 == fromString ) {
        positionFrom = 0;
    } else {
        positionFrom = v1.search( fromString );
        if ( -1 == positionFrom ) {
            return v1;
        }
        positionFrom = positionFrom + fromString.length;
    }
    let positionTo;
    if ( -1 == toString ) {
        positionTo = 999;
    } else {
        positionTo = v1.search( toString );
        if ( -1 == positionTo ) {
            return v1;
        }
        positionTo = positionTo + toString.length - 1;
    }
    extractedString = v1.substring( positionFrom, positionTo);
    return extractedString;
}


document.addEventListener('DOMContentLoaded', function() { 
    document.querySelectorAll('th[data-width]').forEach(function(th) { // this was suggested by ChatGPT when I was struggling to use variables from python through jinja to set the widths of the table columns in html
        th.style.width = th.getAttribute('data-width') + 'px';
    });
});

// This code will run after the page is fully loaded
window.onload = function() {
    document.getElementById('dobYearGr2').setAttribute('max', yearsUpToNow) // I wish there was some cleverer way to do this, 
    document.getElementById('dobYearGr2').setAttribute('max', yearsUpToNow) // but HTML complains about having the same id name for multiple input boxes
    document.getElementById('dodYearGr3').setAttribute('max', yearsUpToNow) // perhaps there is a way to getElementsBy something else that won't bother html validator?
    document.getElementById('dodYearGr3').setAttribute('max', yearsUpToNow)    
    // Your code here
    //window.alert("Welcome to Musictracks!")
    //console.log('The entire page is fully loaded');
};

