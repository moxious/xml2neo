'''
Created on Oct 9, 2014

@author: moxious
'''
from numbers import Number
from xml2neo.Statement import Statement
import uuid

"""A simple class that contains information about what can be created/matched as a node in Cypher"""
class CypherNode:
    def __init__(self, nodeID, labels, props={}, matchBy="_uuid"):
        if nodeID is None or labels is None or len(labels) == 0:
            raise Exception, "CypherNodes must have a valid nodeID and more than zero labels"
                
        self.nid = nodeID
        self.labels = labels
        self.props = props
        self.matchBy = matchBy
        
        if matchBy != "_uuid" and not self.props.has_key(self.matchBy):
            raise Exception, "CypherNode matchBy field '%s' cannot be used because properties do not include that" % self.matchBy
                
        if matchBy == "_uuid":
            self.props["_uuid"] = str(uuid.uuid4())
        else:
            # generate a UUID based on the match field.   
            # This guarantees the same UUID for a given match field value.
            self.props["_uuid"] = str(uuid.uuid5(uuid.NAMESPACE_X500, str(self.props[self.matchBy])))                    
        
    def getNodeID(self): return self.nid
        
    def matchStatement(self):
        """Return a MATCH statement for this node"""
        return Statement(self.toSimpleMatchSyntax(), "MATCH")

    def mergeStatement(self):
        """Return a MATCH statement for this node"""
        return Statement(self.toNodeCypherSyntax(), "MERGE")
        
    def createStatement(self):
        """Return a MATCH statement for this node"""
        return Statement(self.toNodeCypherSyntax(), "CREATE")        
        
    def toSimpleMatchSyntax(self):
        """Matching a node only requires matching on the UUID, not everything"""
        labelStr = ":".join(map(lambda e: "`%s`" % e, self.labels))        
        return "(%s:%s {`%s`:%s})" % (self.getNodeID(), labelStr, self.matchBy, self.formatValue(self.props[self.matchBy]))
        
    def toNodeCypherSyntax(self):
        # Labels should look like:  `foo`:`bar`:`baz`
        labelStr = ":".join(map(lambda e: "`%s`" % e, self.labels))
        propsStr = self.formatProperties(self.props)
        
        return "(%s:%s {%s})" % (self.getNodeID(), labelStr, propsStr)        
    
    def formatValue(self, val):
        def translate(s):
            return s.replace("\\", "\\\\").replace("'", "\\'")
        
        if isinstance(val, list):
            return "[%s]" % ", ".join(map(lambda e: self.formatValue(e), val))
        elif isinstance(val, bool):            
            return unicode(str(val), "utf-8").lower()
        elif isinstance(val, Number):        
            v = "%s" % str(val)            
            return unicode(v, "utf-8")
        else: 
            v = "'%s'" % translate(val)
            if isinstance(v, unicode): return v
            else: return unicode(v, "utf-8")

    def formatProperties(self, props):
        s = []
        for key in props.keys():
            s.append("`%s`: %s" % (unicode(key,"utf-8"), 
                                   self.formatValue(props[key])))

        return ", ".join(s).encode("utf-8")    