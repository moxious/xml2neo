#!/usr/bin/python
'''
@author: moxious
'''

import sys
# import xml.etree.cElementTree as etree
import xml.etree.ElementTree as ET
from xml2neo.Statement import Statement
from xml2neo.CypherNode import CypherNode
from xml2neo.CypherRelationship import CypherRelationship
from xml2neo.CypherQuery import CypherQuery
from numbers import Number
import re

class Xml2Cypher:
    def __init__(self):
        self.counter = 0
        # Map namespace URIs to cypher node IDs.
        self.nsMap = {}
        self.queries = []

    def getId(self):
        self.counter = self.counter + 1
        _id = "_%d" % self.counter
        return _id

    def convert(self, fileHandle):
        try:
            parser = ET.XMLParser(encoding="utf-8")
            # parser = etree.XMLParser(encoding="utf-8")                        
            tree = ET.parse(fileHandle, parser=parser)            
            root = tree.getroot()

            self.convertNamespaces(ET._namespace_map)
            
            # Tree label of [0] indicates that this is the root element.
            rootCypherNode = self.elementToCypher(root, [0])

            # After processing, all queries are accumulated here.
            for z in range(0, len(self.queries)):
                # print "/* QUERY %d */" % z
                print "%s" % str(self.queries[z])

        except ET.ParseError, e:
            sys.stderr.write("Unable to parse XML stream: %s (skipped)" % e)
        return

    def getNamespaceCypherNodeByURI(self, uri):
        cnode = CypherNode(nodeID=self.getId(), labels=['Namespace'], props={"uri":uri})
        return cnode

    def getNamespaceNodeIdByURI(self, uri):
        try:
            return self.nsMap[uri]
        except KeyError:
            nid = self.getId()
            self.nsMap[uri] = nid
            
            cnode = CypherNode(nid, labels=['Namespace'], props={ "uri" : uri })
            #self.statements.append(Statement("(%s:Namespace {uri: %s})" % 
            #                                 (nid, self.formatValue(uri)),
            #                                 stmtType="MERGE"))
            self.statements.append(cnode.mergeStatement())
            return nid

    def convertNamespaces(self, nsMap):
        for key in nsMap.keys():
            nid = self.getId()
            cnode = CypherNode(nid, labels=['Namespace'], props={"prefix" : nsMap[key], "uri" : key })
                        
            self.queries.append(CypherQuery([cnode.mergeStatement()]))

        return True

    def formatValue(self, val):
        def translate(s):
            return s.replace("\\", "\\\\").replace("'", "\\'");

        if isinstance(val, bool):
            return unicode(str(val), "utf-8").lower()
        elif isinstance(val, Number):
            v = "'%s'" % translate(val)
            if isinstance(v, unicode): return v
            else: return unicode(v, "utf-8")
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

    def tagNameParts(self, tok):
        try:
            tok.index("{")
            m = re.search("\{(.+)\}(.+)", tok)
            return (m.group(1), m.group(2))
        except ValueError:
            return ("", tok)

    def elementToCypher(self, element, treeLabel=None):
        nodeId = self.getId()

        if treeLabel is None:
            raise Exception, "Missing tree labels are not permitted."

        # Properties of the node to log, starting with root status.
        props = { "_path" : treeLabel }

        # Copy properties from the XML elements attributes.
        for key in element.attrib:
            props[key] = element.attrib[key]
        
        # Extract namespace URI and tag name
        (uri, tagName) = self.tagNameParts(element.tag)

        # Add the elements text as a property, if appropriate
        t = element.text
        if t is not None:
            props["_text"] = t.strip()

        # rootLabel = ""        
        # When the tree label is the 0th item, that's the root.
        # if treeLabel == [0]: rootLabel = ":RootElement"

        # Cypher; create an element labeled (tag name) and XMLElement,
        # with the specified properties.
        #s = "(%s:`%s`:XMLElement%s {%s})" % (nodeId, tagName, rootLabel,
        #                                     self.formatProperties(props))
        #statements.append(Statement(s, stmtType="CREATE"))
        labels = [tagName, "XmlElement"]
        if treeLabel == [0]: labels.append("RootElement")
        if len(element) == 0: labels.append("LeafElement")

        # Put the tag name in as the label.         
        if not props.has_key("label"):
            props["label"] = tagName
        
        cnode = CypherNode(nodeId, labels=labels, props=props)
        
        # Create the element.
        self.queries.append(CypherQuery([cnode.createStatement()]))        

        if uri != "":
            nsNode = self.getNamespaceCypherNodeByURI(uri)
            
            # Add a query to assert a namespace relationship here.            
            self.queries.append(CypherQuery([nsNode.matchStatement(), 
                                             cnode.matchStatement(),
                                             CypherRelationship(cnode, nsNode, "namespace", props={}).createStatement()]))

        childIdx = 0
        
        # Extend the tree label for first child.
        treeLabel.append(childIdx)
        
        for child in element:
            childCypherNode = self.elementToCypher(child, treeLabel)
            
            self.queries.append(CypherQuery([cnode.matchStatement(), childCypherNode.matchStatement(), 
                                             CypherRelationship(cnode, childCypherNode, "contains", props={"seq":childIdx}).createStatement()]))

            childIdx = childIdx + 1
            treeLabel[-1] = childIdx # Update tree label for next sequential child.

        treeLabel.pop()

        return cnode

def main(args):
    if len(args) > 0:
        for arg in args:
            #try:
            fp = open(arg, mode="rb")
            Xml2Cypher().convert(fp)
            fp.close()
            #except Exception as e:
            #    raise Exception("Error processing %s: %s" % (arg, e))
                # sys.stderr.write("Failed to process %s: %s" % (arg, e))
                # sys.stderr.flush()
    else:
        Xml2Cypher().convert(sys.stdin)

if  __name__ =='__main__': 
    main(sys.argv[1:])
