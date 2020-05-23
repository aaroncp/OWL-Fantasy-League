# OWL-Fantasy-League
This is a script that pulls csv files weekly from the official Overwatch League website containing player and match stats.  It then uses that data to generate a fantasy score for each player, along with recording map score, and inserting all that data into the following spreadsheet: https://docs.google.com/spreadsheets/d/1LsuN_2Oo4wHV9kMEAulGZEnT1W8B8--A89XMZI8r5LE/edit?usp=sharing

The spreadsheet itself does a number of useful things for the league.  Each person participating in the league can create a team for each week.  Once the script is run in a given week, it will automatically calculate each person's team fantasy score.  Participants can also predict who is going to win each match for any given weekend, and a score will automatically tally for correct guesses.  A fantasy cost is also generated that incorporates both a player's average score and how likely they are to play.

Both weekly sheets and Player Info can be sorted by a variety of columns using the 'Sort Data' menu I added to the sheet.  I have included the google sheets script that adds that menu item and sorts the information as 'Sort Sheet Script'.
