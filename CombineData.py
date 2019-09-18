import pandas as pd
import sys
import configparser


def home_vs_away(row):
    """
    return 0 for away and 1 for home
    """
    if row['OPP'][0] == '@' :
        return 0
    else:
        return 1

def get_defense(key):
    """
    look up defense based on name
    ex. Bears -> CHI
    """
    config = configparser.ConfigParser()
    config.read('defense.ini')
    return config['DEFENSE'][key['TeamName']]

# get parameters
fanduel_or_draftkings = sys.argv[1]
week = sys.argv[2]
week = 'Week' + week

player_list_path = ''
proj_ownership_path = ''
if(fanduel_or_draftkings == 'f'):
    player_list_path = 'FanduelPlayersList'
    proj_ownership_path = 'FanduelProjOwnership'
elif(fanduel_or_draftkings == 'd'):
    player_list_path = 'DraftKingsPlayersList\\early-only-players-list.csv'
    proj_ownership_path = 'DraftKingsProjOwnership'

player_list_path = ".\\" + week + "\\" + player_list_path
#print(player_list_path)
player_list_path = r'/Users/dominicdigiovanni/Documents/PythonApps/DFSFantasy2019/thu-mon-players-list.csv'
#print(player_list_path)

# draftkings data
draftkings_players_list = pd.read_csv(player_list_path)
draftkings_players_list = draftkings_players_list[['Position','Name','Salary','AvgPointsPerGame']]

# rotowire data
rotowire_stats = pd.read_csv('thu-mon-proj-own.csv')
#rotowire_stats_2 = pd.read_csv('afternoon-only.csv')
#roto_frames = [rotowire_stats, rotowire_stats_2]
#rotowire_stats = pd.concat(roto_frames, sort=False)
rotowire_stats = rotowire_stats[['PLAYER','TEAM','OPP','OWN%']]
rotowire_stats['HOME'] = rotowire_stats.apply(lambda row: home_vs_away(row), axis=1)
rotowire_stats['OPP'] = rotowire_stats['OPP'].map(lambda x: x.lstrip('@'))

print('merging draftkings player list and rotowire data')
#print(len(draftkings_players_list.index))
# join draftkings player list with stats from Rotowire
dataframe_merged = pd.merge(draftkings_players_list,rotowire_stats, left_on='Name',right_on='PLAYER',how='left')

print(dataframe_merged[dataframe_merged["PLAYER"].isnull()])
# TODO Find values that didn't join
for index, row in dataframe_merged.iterrows():
    if pd.isnull(row['PLAYER']):
        # display Player that could not be found
        print('Could not find player: ' + row['Name'])
        search_name = row['Name'].split()
        print("Search on: ")
        print(search_name)
        #rotowire_stats.filter(like=search_on, axis=0)
        x = input()
        if x == 'Done':
            break
        else:
            #print(rotowire_stats.filter(like=x, axis=0))
            # get players to potentially switch name for
            search_results = rotowire_stats[rotowire_stats['PLAYER'].str.contains(x)]
            if len(search_results) > 0:
                print(search_results)
                for index_search, row_search in search_results.iterrows():
                    print("Do you want to switch name of " + row_search['PLAYER'] + " to " + row['Name'] + "? (y/n)")
                    use_name = input()
                    if(use_name == 'y'):
                        rotowire_stats[rotowire_stats['PLAYER'].str == row_search['PLAYER']] = row['Name']
                        rotowire_stats.to_csv("thu-mon-proj-own.csv")
                        break
            else:
                print("No player was found for the given search criteria.")
        print('\n')

# QB Projections
qb_player_projections = pd.read_csv('FantasyPros_Fantasy_Football_Projections_QB.csv')
qb_player_projections = qb_player_projections[['Player','FPTS']]

# RB Projections
rb_player_projections = pd.read_csv('FantasyPros_Fantasy_Football_Projections_RB.csv')
rb_player_projections = rb_player_projections[['Player','FPTS']]

# WR Projections
wr_player_projections = pd.read_csv('FantasyPros_Fantasy_Football_Projections_WR.csv')
wr_player_projections = wr_player_projections[['Player','FPTS']]

# TE Projections
te_player_projections = pd.read_csv('FantasyPros_Fantasy_Football_Projections_TE.csv')
te_player_projections = te_player_projections[['Player','FPTS']]

# Defense Projections
dst_player_projections = pd.read_csv('FantasyPros_Fantasy_Football_Projections_DST.csv')
dst_player_projections = dst_player_projections[['Player','FPTS']]

# K Projections
k_player_projections = pd.read_csv('FantasyPros_Fantasy_Football_Projections_K.csv')
k_player_projections = k_player_projections[['Player','FPTS']]


print(len(dataframe_merged.index))
print('merging with projected points')
# union all the projection data into one dataframe
proj_frames = [qb_player_projections, rb_player_projections, wr_player_projections, te_player_projections, dst_player_projections, k_player_projections]
proj_result = pd.concat(proj_frames, sort=False)
proj_result.to_csv("player_projections_combined.csv")

# join to get projected points
dataframe_merged = pd.merge(dataframe_merged,proj_result, left_on='Name',right_on='Player',how='left')

# Defense Against QB
def_against_qb = pd.read_csv('Team-vs-QB.csv')
def_against_qb = def_against_qb.rename(columns={'Name':'TeamName',r'Pts/G':'OppPointsAllowed'})
def_against_qb = def_against_qb[['TeamName','OppPointsAllowed']]
def_against_qb['OPP-2'] = def_against_qb.apply(lambda row: get_defense(row), axis=1)
def_against_qb['Position'] = 'QB'

# Defense Against RB
def_against_rb = pd.read_csv('Team-vs-RB.csv')
def_against_rb = def_against_qb.rename(columns={'Name':'TeamName',r'Pts/G':'OppPointsAllowed'})
def_against_rb = def_against_rb[['TeamName','OppPointsAllowed']]
def_against_rb['OPP-2'] = def_against_rb.apply(lambda row: get_defense(row), axis=1)
def_against_rb['Position'] = 'RB'

# Defense Against WR
def_against_wr = pd.read_csv('Team-vs-WR.csv')
def_against_wr = def_against_qb.rename(columns={'Name':'TeamName',r'Pts/G':'OppPointsAllowed'})
def_against_wr = def_against_wr[['TeamName','OppPointsAllowed']]
def_against_wr['OPP-2'] = def_against_wr.apply(lambda row: get_defense(row), axis=1)
def_against_wr['Position'] = 'WR'

# Defense Against TE
def_against_te = pd.read_csv('Team-vs-TE.csv')
def_against_te = def_against_qb.rename(columns={'Name':'TeamName',r'Pts/G':'OppPointsAllowed'})
def_against_te = def_against_te[['TeamName','OppPointsAllowed']]
def_against_te['OPP-2'] = def_against_te.apply(lambda row: get_defense(row), axis=1)
def_against_te['Position'] = 'TE'

#TODO Look up position

# union all the projection data into one dataframe
def_against_frames = [def_against_qb, def_against_rb, def_against_wr, def_against_te]
def_against_result = pd.concat(def_against_frames, sort=False)
def_against_result.to_csv('def_against_frames.csv')

print('merging with defense points allowed')
# join to get points against defense by position
dataframe_merged = pd.merge(dataframe_merged,def_against_result, left_on=['OPP','Position'],right_on=['OPP-2','Position'],how='left')
print(len(dataframe_merged.index))

# get rid of duplicate name columns
dataframe_merged = dataframe_merged.drop('PLAYER', 1)
dataframe_merged = dataframe_merged.drop('Player', 1)
dataframe_merged = dataframe_merged.drop('OPP-2', 1)

#change column names
dataframe_merged = dataframe_merged.rename(columns={'FPTS':'ProjectedPoints',r'Pts/G':'OppPointsAllowed'})

dataframe_merged = dataframe_merged.sort_values(by=['Salary'], ascending=False)
# final csv output
dataframe_merged.to_csv("merged.csv")
