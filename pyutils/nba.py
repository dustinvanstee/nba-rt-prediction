import math

# Add Lookup tables
monthMap = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}

teamMap = {
  "Atlanta" : "atl",
  "Boston"  : "bos",
  "Brooklyn"  : "bkn",
  "Charlotte"  : "cha",
  "Chicago"  : "chi",
  "Cleveland"  : "cle",
  "Dallas"  : "dal",
  "Denver"  : "den",
  "Detroit"  : "det",
  "Golden State"  : "gst",
  "Houston"  : "hou",
  "Indiana"  : "ind",
  "LA Clippers"  : "lac",
  "LA Lakers"  : "lal",
  "Memphis"  : "mem",
  "Miami"  : "mia",
  "Milwaukee"  : "mil",
  "Minnesota"  : "min",
  "New Orleans"  : "nor",
  "New York"  : "nyk",
  "Oklahoma City"  : "okc",
  "Orlando"  : "orl",
  "Philadelphia"  : "phi",
  "Phila."  : "phi",
  "Phoenix"  : "pho",
  "Portland"  : "por",
  "Sacramento" : "sac",
  "San Antonio"  : "san",
  "Toronto"  : "tor",
  "Utah"  : "uta",
  "Washington"  : "wsh",
   None : "none"
   }


# Create new team name column.. do simple lookup conversion with a UDF
def mapper(teamin) :
    return teamMap[teamin]

mapperudf = udf(mapper)
# Date Logic to adjust for games that finish on the day after .... 
# This is so that I can join them against the spread which was dated the day prior...
# This is due to not having a great key to join my tables ...

datecrossregex = re.compile("^0[0-3]") # midnight to 3am
def dateadjust(datein, tsin ) : 
    #dateary = datein.split("-")
    tsary   = tsin.split(":")
    sub_one_day = datetime.timedelta(days=1)
    newdate = datein
    if datecrossregex.match(tsary[0]) :
        #day = "%02d".format(int(dateary[2]) -1)
        #newdate = dateary(0) + "-" + dateary(1) + "-" + day   
        newdate = datein - sub_one_day
    return str(newdate)

dateadjustudf = udf(dateadjust)


# UDFs to create some extra features ... this one is for an experiemental combination of Time left and Score difference.  
# Made this via intuition.  This can be extended to add other custom features
#val crossover = 8
#val exp = 0.5
def scoredivtimeXform(score_diff,time_left, crossover, exp):
    rv = score_diff/(math.pow((time_left/crossover) + 0.01, exp))
    return rv

scoredivtimeUdf = udf(scoredivtimeXform)


