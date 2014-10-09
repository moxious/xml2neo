## Synopsis

A set of tools for processing XML documents into formats that can be loaded
into Neo4J.  In general, we want to take the tree structure that the XML
presents, and load it into neo4j as-is, permitting analysts to then use
Cypher queries to massage/reformat that data from the XML structure into
whatever is needed.

## Quick Start

Get the source:

```$ git clone https://github.com/moxious/xml2neo.git```

Run a sample:

```
$ cd xml2neo
$ ./xml2neo.py test/sample.xml
```

The result will be a long series of cypher queries, which when executed, will create a graph model of that XML
tree.  This output can then be piped to ```neo4j-shell``` or to other scripts which can run the cypher
against the REST API on another machine.

## Graph Model

Because the tool does not necessarily know anything about the XML before it begins, it creates a fairly 
general tree that mimicks the XML's structure.  In particular, it creates many nodes with ```contains``` and
```namespace``` relationships between them.   Nodes are variously labeled as follows:
* ```XmlElement``` label is applied to *all* elements in the document;
* ```RootElement``` label will be applied to the root of the document; 
* ```LeafElement``` to all those nodes without children; 
* The tag name will also be applied as a label, so that you can find all "Foo" XML elements by querying for
```MATCH (element:XmlElement:Foo) RETURN element```.
* All nodes are assigned a generated ```_uuid``` property, and a ```_label``` property that corresponds to 
the XML element's tag name.
* XML attributes become node properties, so ```<foo bar='baz'/>``` will become ```(n:XmlElement:foo {bar: 'baz'})```.

## Limitations

Currently, the XML processing uses python's ```etree.ElementTree``` - as such the XML document you are
processing must be able to fit into memory.   Very large documents are not yet supported.
