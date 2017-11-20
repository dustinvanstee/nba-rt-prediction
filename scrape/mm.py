#!/usr/bin/python2.7
#Created by Josh Fuerst
#!/usr/bin/env python
#Modified  by Dustin VanStee

# for question/bug reports please visit http://www.fuerstjh.com and submit through contact page.

#only been tested on python 2.7
#Currently if an error is encountered the API does not handle the exception it raises it to the caller.


#******************* USAGE *******************

#import espn_api
#espn_api.get_scores(espn_api.NCAA_FB, 'Cincinnati, Ohio State')


#****************** ABOUT ****************************

#This API connects to ESPN bottomline and parses the page to get current game scores.
#Just call the get_scores function passing in a league string (defined below)

#The return value will be a dictionary of games. Each entry will have the following structure:
        # {espn_game_id:[team1_name,team1_score,team2_name,team2_score,game_time]}

#You can also pass in team_filter. This should be a comma separated string of the team names you wish to
#get scores for
#NOTE: the team names must appear as listed on espn bottomline. To see list run once with no filter


import urllib2
import pdb
import json

import time
import datetime
import argparse
import sys
import re

globalArgs = ''


#LEAGE STRINGS
NCAA_FB = 'ncf'
NFL = 'nfl'
MLB = 'mlb'
NBA = 'nba'
NHL = 'nhl'
NCAA_BB = 'mens-college-basketball'
outfilebase="scores_REPLACE.test.dat"
sample_rate = 30


def parseCliArgs():
  fn = sys._getframe().f_code.co_name
  parser = argparse.ArgumentParser(description='CLI parser for score capture')
  parser.add_argument('-s','--sport',help='This is the server data',default='nba')
  global globalArgs  # need this to assign to global var namespace
  globalArgs= parser.parse_args()

  #print "#{0:<20s} Running on project {1}".format(fn, globalArgs.project)



def get_scores(league,team_filter=None):
        fn = sys._getframe().f_code.co_name

        scores = {}
        STRIP = "()1234567890 "
        if team_filter:
                team_filter=team_filter.lower().split(', ')

        try:
                #visit espn bottomline website to get scores as html page
                url = 'http://sports.espn.go.com/'+league+'/bottomline/scores'
    #url = "http://www.fuerstjh.com/test.html"
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                page = response.read()

                #url decode the page and split into list
                data = urllib2.unquote(str(page)).split('&'+league+'_s_left')
                #pdb.set_trace()
                for i in range(1,len(data)):
                    parse_data = 1
                    if(league == 'mlb' and not re.search("gameId", data[i])) :
                        parse_data = 0

                    if(parse_data == 1) :

                        #get rid of junk at beginning of line, remove ^ which marks team with ball
                        main_str = data[i][data[i].find('=')+1:].replace('^','')
                        #extract time, you can use the ( and ) to find time in string
                        # fixed rfind -> find ... this was confusing the nhl parser ...
                        time =  main_str[main_str.find('('):main_str.find(')')+1].strip()
                        #extract score, it should be at start of line and go to the first (
                        score =  main_str[0:main_str.find('(')].strip()
                        #extract espn gameID use the keyword gameId to find it
                        gameID = main_str[main_str.find('gameId')+7:].strip()
                        gameID = re.sub("&.*","",gameID)
                        if gameID == '':
                                #something wrong happened
                                continue
                        #split score string into each teams string
                        team1_name = ''
                        team1_score = '0'
                        team2_name = ''
                        team2_score = '0'
                        if (' at ' not in score):
                                teams = score.split('  ')
                                team1_name = teams[0][0:teams[0].rfind(' ')].lstrip(STRIP)
                                team2_name = teams[1][0:teams[1].rfind(' ')].lstrip(STRIP)
                                team1_score = teams[0][teams[0].rfind(' ')+1:].strip()
                                team2_score = teams[1][teams[1].rfind(' ')+1:].strip()
                        else:
                                teams = score.split(' at ')
                                team1_name = teams[0].lstrip(STRIP)
                                team2_name = teams[1].lstrip(STRIP)
                        #add to return dictionary
                        if not team_filter:
                                scores[gameID] = ['','','','','']
                                scores[gameID][0] = team1_name
                                scores[gameID][1] = team1_score
                                scores[gameID][2] = team2_name
                                scores[gameID][3] = team2_score
                                scores[gameID][4] = time
                        elif team1_name.lower() in team_filter or team2_name.lower() in team_filter:
                                scores[gameID] = ['','','','','']
                                scores[gameID][0] = team1_name
                                scores[gameID][1] = team1_score
                                scores[gameID][2] = team2_name
                                scores[gameID][3] = team2_score
                                scores[gameID][4] = time

        except Exception as e:
                #print(str(e))
                scores = {}
                return

        return scores

# Moving to norm.py, and upgrading capability there ...
# its best not to process streaming data, but rather just capture and post process offline

def convert_time(time_string, sport) :
    #(10:32 IN 3RD)
    fn = sys._getframe().f_code.co_name

    if(sport == NBA) :
        time_left = 48.0
        tperiods = 4
        tpper = 12.0
    elif(sport == NHL) :
        time_left = 60.0
        tperiods = 3
        tpper = 20.0
    elif(sport == NCAA_BB) :
        time_left = 40.0
        tperiods = 2
        tpper = 20.0
    elif(sport == MLB) :
        time_left = 9.0
        tperiods = 9
        tpper = 3.0

    #time_string = '(10:32 IN 3RD)'
    try :
        (mm_ss,in_indicator,periods) = time_string.split(' ')

        if(in_indicator == "OF") :
            in_indicator = "IN"
            mm_ss = '0.0'

        if(in_indicator == "IN") :
           #pdb.set_trace()
           mm_ss = mm_ss.replace('(','')
           (mins,secs) = mm_ss.split(':')
           periods = float(periods[0])
           time_left = float((tperiods - periods) * tpper)+ float(mins) + float(secs)/60
        # Game not started case handled with defaults
        # Game Finished handled with try / except

    except ValueError :
        time_left = 0.0

    return str(time_left)

def get_and_record_scores(sport) :
    fn = sys._getframe().f_code.co_name

    pscores = {}

    sleep_time = sample_rate  # global sleep timer that will throttle my pinging of the server
    while(1) :
        tstamp = time.time()
        ftstamp = datetime.datetime.fromtimestamp(tstamp).strftime('%Y-%m-%d,%H:%M:%S')

        scores = get_scores(sport)
        # I have been having this crash sometimes when sport is not a dict
        if(isinstance(scores,dict)) :


            outfile = re.sub('REPLACE',sport,outfilebase)
    
            #output format = date,t1,score,t2,score,time,timeleft
            f = open(outfile, 'a')
    
            ## Create a simple while loop here ... if all games final stop ....
            ## Only print if there is a change from previous
    
            any_updates = 0  # global sleep monitor that will throttle my pinging of the server
    
            for k,v in scores.iteritems():
                write_data = 0
                if(pscores.has_key(k)) :
                    if(scores[k] != pscores[k]) :
                        print "Score change detected"
                        print "Previous {0}".format(pscores[k])
                        print "Current  {0}".format(scores[k])
                        write_data = 1
                        any_updates = 1
    
                else :
                    write_data = 1
                    any_updates = 1
                    print "Initial write  {0}".format(scores[k])
    
                        #print "key = {0}".format(k)
                        #print "val = {0}".format(v)
                if(write_data == 1) :
                    f.write(ftstamp + ",")
                    for item in v :
                        #print item
                        f.write(item + ",")
                    # defer logic for mlb and just put it in the spark workbook for now
                    if(sport != 'mlb') :
                        f.write( convert_time(v[4],sport)+ "," )
                    else :
                        f.write('0'+ ",")
                    f.write(k)
                    f.write("\n")
                    f.flush()
            # save the structure for the next loop!
            pscores = scores

            # reset timer if updates occured ..
            if(any_updates == 1) :
                sleep_time = sample_rate
            # slow timer if no updates occured ..
            else :
                # limit throttle to max of 1820 seconds of sleep
                if(sleep_time < 961) :
                    sleep_time *= 2

            print "Updates detected = {0}".format(any_updates)
            print "Sleeping for {0}".format(sleep_time)

            time.sleep(sleep_time)
            #pdb.set_trace()

            f.close()


def main():
    fn = sys._getframe().f_code.co_name
    parseCliArgs()
    get_and_record_scores(globalArgs.sport)
    print "Data captured for sport:{0}".format(globalArgs.sport)

if __name__ == "__main__":
  main()


#get_and_record_scores(NBA)
#get_and_record_scores(NHL)
#get_and_record_scores(MLB)
#get_and_record_scores(NCAA_BB)
