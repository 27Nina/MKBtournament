from .table import Table

class Room:
    def __init__ (self, teams:list, roundNum:int, roomNum:int, size:int):
        self.teams = teams
        self.table = Table(teams, roundNum, roomNum, size)
        self.roundNum = roundNum
        self.roomNum = roomNum
        self.advanced = []
        self.tieTeams = []
        self.extraTeams = []

    def updateTable(self, tournament, players, scores):
        self.table.update(players, scores)
        self.table.finished = True
        self.calcAdvanced(tournament)
        
    def calcAdvanced(self, tournament):
        if self.table.finished is None:
            return None, None, None
        adv, tie, extra = self.table.getAdvanced(tournament)
        self.advanced = adv
        self.tieTeams = tie
        self.extraTeams = extra
        return adv, tie, extra

    def checkAdvanced(self, tournament, players, scores):
        playerScores = {}
        for i in range(len(players)):
            playerScores[players[i]] = scores[i]
        adv, tie, extra = self.table.getAdvanced(tournament, playerScores)
        return adv, tie, extra

    def sampleScoreboard(self, players, scores):
        playerScores = {}
        for i in range(len(players)):
            playerScores[players[i]] = scores[i]
        sb = self.table.scoreboard(playerScores)
        return sb
    
    def getPlayersFromMiiNames(self, names):
        players = []
        for name in names:
            players.append(self.table.getPlayerFromName(name))
        return players

    def getProgressStr(self):
        finished = False
        if self.table.finished is False:
            status = "✘"
        elif len(self.tieTeams) > 0:
            status = f"✘ ({len(self.tieTeams)} tied teams)"
        else:
            finished = True
            status = f"✓ Submitted"
        progressStr = f"`Room {self.roomNum} - {status}`\n"
        return finished, progressStr

    def reset(self):
        size = self.table.size
        self.table = Table(self.teams, self.roundNum, self.roomNum, size)
        self.advanced = []
        self.tieTeams = []
        self.extraTeams = []

    def __str__ (self):
        msg = f"`Room {self.roomNum}`\n"
        for i, team in enumerate(self.teams):
            msg += f"`{i+1}.` {str(team)}\n"
        return msg

    
