DIR=/root/oddsdata
POSTFIX=`date +%m%d%y`
mkdir -p ${DIR}
cd $DIR

#http://www.oddsmaker.ag/rss-feeds/
wget http://www.referincome.com/odds/rss2/basketball_nba.xml
wget http://www.referincome.com/odds/rss2/football_nfl.xml
wget http://www.referincome.com/odds/rss2/basketball_ncaa.xml
wget http://www.referincome.com/odds/rss2/hockey_nhl.xml
wget http://www.referincome.com/odds/rss2/baseball.xml

mv basketball_nba.xml basketball_nba.${POSTFIX}.xml
mv football_nfl.xml football_nfl.${POSTFIX}.xml
mv basketball_ncaa.xml basketball_ncaa.${POSTFIX}.xml
mv hockey_nhl.xml hockey_nhl.${POSTFIX}.xml
mv baseball.xml baseball.${POSTFIX}.xml

TG=`grep title * | grep -v OddsMaker | grep -v 'Click Here' | wc -l`
echo Total Games = $TG
grep title *.${POSTFIX}.xml | wc -l