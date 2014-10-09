'''
@author: moxious
'''

class Statement:
    def __init__(self, stmt, stmtType="MERGE"):
        self.stmt = stmt
        self.stmtType = stmtType.upper()
        
        if self.stmtType not in ["MERGE", "MATCH", "CREATE"]:
            raise Exception("stmtType must be one of ['MERGE', 'MATCH', 'CREATE']")

    def __str__(self):
        return "%s %s" % (self.stmtType, self.stmt)

if __name__ == '__main__':
    pass