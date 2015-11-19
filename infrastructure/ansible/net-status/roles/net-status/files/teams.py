import requests
import json

USE_REAL_TEAMS = True

URL = "http://ructf.org/e/2015/teams/info"

teams_cache = {}

def get_teams():
    global teams_cache
    try:
        teams = {}
        if not USE_REAL_TEAMS:
            for i in range(490):
                teams[i] = "test_team%d" % i
        else:
                response = requests.get(URL)
                response.encoding = 'utf-8'
                teams_list = json.loads(response.text)
                for team_id, team_name in teams_list:
                    if type(team_id) is int:
                        teams[team_id] = team_name
    except Exception:
        return teams_cache

    teams_cache = teams
    return teams
