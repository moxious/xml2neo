#!/usr/bin/python
'''
@author: moxious
'''

import sys
# import xml.etree.cElementTree as etree
import xml.etree.ElementTree as ET
from xml2neo.CypherNode import CypherNode
from xml2neo.CypherRelationship import CypherRelationship
from xml2neo.CypherQuery import CypherQuery
import re

class Xml2Cypher:
    def __init__(self):
        self.counter = 0
        self.queries = []

        self.STRIP_WHITESPACE = True

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
                print (str(self.queries[z]))

        except ET.ParseError as e:
            sys.stderr.write("Unable to parse XML stream: %s (skipped)" % e)
        return

    def getNamespaceCypherNodeByURI(self, uri):
        cnode = CypherNode(nodeID=self.getId(), labels=['Namespace'], props={"uri":uri}, matchBy="uri")
        return cnode

    def convertNamespaces(self, nsMap):
        """Looks at a namespace map, and adds queries to merge those namespaces in as new nodes"""
        for key in nsMap.keys():
            nid = self.getId()
            cnode = CypherNode(nid, labels=['Namespace'], props={"prefix" : nsMap[key], "uri" : key }, matchBy="uri")
                        
            self.queries.append(CypherQuery([cnode.mergeStatement()]))

        return True

    def tagNameParts(self, tok):
        """Given an element tree token such as '{http://foo.com/}bar' returns
        a tuple with the namespace and tag name ('http://foo.com/', 'bar')"""
        try:
            tok.index("{")
            m = re.search("\{(.+)\}(.+)", tok)
            return (m.group(1), m.group(2))
        except ValueError:
            return ("", tok)

    def elementToCypher(self, element, treeLabel=None):
        """Convert an XML element (recursively) into a set of Cypher queries, which are added
        to self.queries"""
        nodeId = self.getId()

        if treeLabel is None:
            raise Exception("Missing tree labels are not permitted.")

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
            if self.STRIP_WHITESPACE:
                t = t.strip()
            if t != "":
                props["_text"] = t

        labels = [tagName, "XmlElement"]
        if treeLabel == [0]: labels.append("RootElement")
        if len(element) == 0: labels.append("LeafElement")

        # Put the tag name in as the label.         
        if not "label" in props:
            props["label"] = tagName
        
        cnode = CypherNode(nodeId, labels=labels, props=props)
        
        # Create the element.
        self.queries.append(CypherQuery([cnode.createStatement()]))        

        if uri != "":
            nsNode = self.getNamespaceCypherNodeByURI(uri)
            
            # Add a query to assert a namespace relationship here.            
            self.queries.append(CypherQuery([nsNode.mergeStatement(), 
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
