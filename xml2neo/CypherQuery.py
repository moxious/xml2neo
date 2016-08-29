'''
Created on Oct 9, 2014

@author: moxious
'''
from xml2neo.Statement import Statement

class CypherQuery:
    def __init__(self, statements):
        self.statementMap = {}
        
        if statements is not None:
            for s in statements:
                self.addStatement(s)
            
    def addStatement(self, s):
        if not isinstance(s, Statement):
            raise Exception("Statement object %s is of wrong type" % s)
            
        # Sort statements into a map by type
        try:
            arr = self.statementMap[s.stmtType]
            arr.append(s)
        except KeyError:
            self.statementMap[s.stmtType] = [s]
            
        return s    
    
    def __str__(self):
        queryOrder = ['MATCH', 'MERGE', 'CREATE']
                
        if len(self.statementMap.keys()) == 0:
            raise Exception("Cannot turn an empty cypher query into a string")
                
        strbuf = ""
        
        for stmtType in queryOrder:
            try:
                stmts = self.statementMap[stmtType]
                strbuf = strbuf + "\n".join(map(lambda e: str(e), stmts)) + "\n"
            except KeyError:
                # None of those statements in this query.  No big deal.
                pass
        
        return strbuf + ";"
            
