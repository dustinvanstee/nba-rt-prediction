import glob
import pdb
import sys
import csv

base_dir = "/data/work/git-repos/nba-rt-prediction/scoredata/"
base_file = base_dir + "scores_nba.2015.test.dat"
norm_file = base_dir + "nrm_scores_nba.2015.test.dat"

#CONSTANTS for CSV file
DT=0 # date
TS=1 # timestamp
AT=2 # away team
AS=3 # away score
HT=4 # homte team
HS=5 # home score
CT=6 # current time in game
TL=7 # time left (added by my mm.py script but somewhat error prone)

#LEAGE STRINGS
NCAA_FB = 'ncf'
NFL = 'nfl'
MLB = 'mlb'
NBA = 'nba'
NHL = 'nhl'
NCAA_BB = 'mens-college-basketball'


def parse(base_file, within_spark=0) : 
    
    # example line --> #2016-04-05,15:07:51,Charlotte,0,Toronto,0,(7:30 PM ET),48.0,400829043

    game_data = {}

    f = open(base_file, 'r')
    i = 0
    for line in f:
        lineary = []
        if(within_spark == 0) :
            lineary = line.split(",")
        else :
            base_file_ary = base_file.split('=')
            date_str  = base_file_ary[1].split('/')[0]
            away_team = base_file_ary[2].split('/')[0]
            home_team = base_file_ary[3].split('/')[0]

            tmp = line.split(",")
            lineary = list([date_str,tmp[0],away_team,tmp[1],home_team,tmp[2],tmp[3],tmp[4]])


        gameid = ""
        
        # This if statement below, could be replaced by a nice checker function someday
        if(len(lineary) == 8 or len(lineary) == 9) :
            #not all games have a gameid, so concat date/teamaway/teamhome
            gameid = lineary[0]+lineary[2]+lineary[4]

            #if(lineary[CT] == "(HALFTIME)") :
            #    pdb.set_trace()

            lineary[TL] = convert_time(lineary[CT], NBA)

            if gameid in game_data :
                game_data[gameid].append(lineary[0:8])
            else :
                game_data[gameid] = list([lineary[0:8]])
    
            print "adding " + str(lineary[0:8]) + " to  " + gameid + " game"
            i += 1
        # Bad line format .. dont process
        else :
            print "Error =>" + str(lineary)

        #if(i > 30) :
        #    break
    return game_data

def convert( line ) : 
    line[3] = float(line[3])
    line[5] = float(line[5])
    line[7] = float(line[7])
    return line

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
        mm_ss = ""
        in_indicator = ""
        periods = ""

        if(len(time_string.split(' ')) == 3) :
            (mm_ss,in_indicator,periods) = time_string.split(' ')


        # Sport Specific Parsing
        if(sport == MLB) :
            print "Passed a sport that isnt coded for"

        # Hockey
        elif(sport == NHL) :
            print "Passed a sport that isnt coded for"

        # Game not started case handled with defaults
        # Game Finished handled with try / except

        # Basketball
        elif(sport == NBA) :
            # END OF [1234] Quarter
            if(in_indicator == "OF") :
                in_indicator = "IN"
                mm_ss = '0:00'
            
            if(in_indicator == "IN") :
               #pdb.set_trace()
               mm_ss = mm_ss.replace('(','')
               (mins,secs) = mm_ss.split(':')
               periods = float(periods[0])
               time_left = float((tperiods - periods) * tpper)+ float(mins) + float(secs)/60
            elif(time_string == "(HALFTIME)") :
                time_left = 24.0
            else :
                print "ERROR, time not properly converted !"

        else : 
            print "Passed a sport that isnt coded for"
            exit(1)

    except ValueError :
        time_left = 0.0

    return str(time_left)

# --> 2016-04-22,23:25:27
#2016-04-22,23:29:28,San Antonio,70,Memphis,71,(END OF 3RD),0.0,400874378


# cur_game is an array of lists
#  each row is a list of a single data point from a game


def normalize(cur_game) :

    time_step = 0.5
    start_time = 0.0

    first_row = cur_game[0]

    first_row[AS] = 0
    first_row[HS] = 0
    first_row[TL] = 48.0

    nrm_game_data = list([first_row])
    last_assigned_time = start_time

    prev_line = first_row
    num_samples = len(cur_game)

    for i in range(0,num_samples) :
        line = convert(cur_game[i])

        #if((cur_game[i][AT] == "Orlando" or cur_game[i][HT] == "Milwaukee") and cur_game[i][CT] == "(HALFTIME)") :
        #    pdb.set_trace()
        
        #print line
        cur_time = 48.0 - line[TL]


        # this determines if I need to make a new row ....
        loop_cnt = 0
        while(cur_time > last_assigned_time+time_step) :
            # Perform Linear Interpolation for scores
            if(loop_cnt == 0) :
                nrm_line = list(line)
            else :
                nrm_line = list(prev_nrm_line)

            nrm_line_te  = last_assigned_time+time_step
            numerator = nrm_line_te - (48.0 - prev_line[TL])
            nrm_line[AS] = prev_line[AS] + (line[AS]-prev_line[AS]) * ( numerator / ( prev_line[TL] - line[TL]))
            nrm_line[HS] = prev_line[HS] + (line[HS]-prev_line[HS]) * ( numerator / ( prev_line[TL] - line[TL]))
            nrm_line[TL] = 48.0 - nrm_line_te

            nrm_game_data.append(nrm_line)
            last_assigned_time += time_step
            prev_nrm_line = list(nrm_line)
            loop_cnt += 1

        prev_line = line

        if(cur_time == 48) :
            #pdb.set_trace()
            nrm_game_data.append(list(line))
    
    return nrm_game_data

    
def normalize_all_games(game_data) :
    keys = game_data.keys()
    print "keys = " + str(keys)
    #mykey = "400829041\n"
    
    nrm_game_data = {}
    for mykey in keys :
        print "Normalizing game " + mykey
        nrm_game_data[mykey] = normalize(game_data[mykey])
        #debug_game(game_data[mykey],nrm_game_data[mykey])
        #pdb.set_trace()


    return nrm_game_data


def debug_game(game_data,nrm_game_data) :

    print "#" * 20
    print "Debugging Game :"
    for g in (game_data,nrm_game_data) :
        for line in g :
            print line


def write_game_data(outfile, nrm_data) :
    #pdb.set_trace()
    with open(outfile, 'w') as csvfile :
        spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='\'', quoting=csv.QUOTE_MINIMAL)

        for keys in nrm_data.keys() :
            for line in nrm_data[keys] :
                spamwriter.writerow(line)


# Only run parser code if directly called
if __name__ == "__main__":
    game_data = parse(base_file)
    nrm_game_data = normalize_all_games(game_data)
    write_game_data(norm_file,nrm_game_data)







    #rv.append(lineary)
    #rv = tdf.count()
    #return rv    
    #return "Here it is " + key_in + " "+ str(rv)
