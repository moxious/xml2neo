'''
Created on Oct 9, 2014

@author: moxious
'''
from xml2neo.CypherNode import CypherNode
from xml2neo.Statement import Statement

class CypherRelationship:
    def __init__(self, head, tail, relType, props):
        self.head = head
        self.tail = tail
        self.relType = relType
        self.props = props
        
        if not isinstance(self.head, CypherNode):
            raise Exception("Head must be a CypherNode")
    
        if not isinstance(self.tail, CypherNode):
            raise Exception("Tail must be a CypherNode")
        
    def toRelCypherSyntax(self):
        return "(%s)-[r:`%s`]->(%s)" % (self.head.getNodeID(), self.relType, self.tail.getNodeID())
        
    def mkStatement(self, st): return Statement(self.toRelCypherSyntax(), st)        
    def matchStatement(self): return self.mkStatement("MATCH")
    def mergeStatement(self): return self.mkStatement("MERGE")
    def createStatement(self): return self.mkStatement("CREATE")