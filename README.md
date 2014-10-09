## Synopsis

A set of tools for processing XML documents into formats that can be loaded
into Neo4J.  In general, we want to take the tree structure that the XML
presents, and load it into neo4j as-is, permitting analysts to then use
Cypher queries to massage/reformat that data from the XML structure into
whatever is needed.

This tool represents only a quick way to get XML data into neo4j; the graph
structure it creates will usually not be the one that is best for your application,
but it provides a starting point to get the work into graph land, where it can continue
with other tools.

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
```namespace``` relationships between them.   

Nodes are structured using the following rules:

* ```XmlElement``` label is applied to *all* elements in the document;
* ```RootElement``` label will be applied to the root of the document; 
* ```LeafElement``` to all those nodes without children; 
* The tag name will also be applied as a label, so that you can find all "Foo" XML elements by querying for
```MATCH (element:XmlElement:Foo) RETURN element```.
* All nodes are assigned a generated ```_uuid``` property, and a ```_label``` property that corresponds to 
the XML element's tag name.
* XML element content and/or text is held in the ```_text``` property, as applicable.
* XML attributes become node properties, so ```<foo bar='baz'/>``` will become ```(n:XmlElement:foo {bar: 'baz'})```.
* Elements are given a ```_path``` property, which is an array of integers indicating the element's depth and
location in a document.  So for example ```_path: [0, 0, 1]``` indicates that the particular node is the second grandchild
of the root.   The root element is always assigned path ```[0]```.

Relationships use the following rules:
* ```contains``` relationships exist between nodes; parents contain children. 
* ```contains``` relationships have a ```seq``` property that is an integer starting at 0.  This
indicates ordering of child elements; the first is seq 0, and so on.
* ```namespace``` relationships link ```XmlElement``` nodes to ```Namespace``` elements, (which contain a 
```prefix``` and a ```uri```)

## Querying XML with Neo4J: Examples

Using the [sample book file](test/sample.xml) as an example, after processing through this script, we can 
query for the description of a book like this:

```
match (t:title:XmlElement { _text: "XML Developer's Guide" })<-[:contains]-
(b:book:XmlElement)-[:contains]->(d:description:XmlElement)
return t._text as title, d._text as description, b.id as bookID;

+--------------------------------------------------------------------------------------------------+
| title                   | description                                                  | bookID  |
+--------------------------------------------------------------------------------------------------+
| "XML Developer's Guide" | "An in-depth look at creating applications     with XML."    | "bk101" |
+--------------------------------------------------------------------------------------------------+
```

We first match on the title, then use relationships to find the ```book``` element, and its other
```description``` child.  The text in that node gives us a description of this book. 

We can also use XPath like expressions by using the ```path``` attribute:

```
neo4j-sh (?)$ match (n:XmlElement { _path: [0, 1, 2] }) return n.label, n._text;
+---------------------+
| n.label | n._text   |
+---------------------+
| "genre" | "Fantasy" |
+---------------------+
```

This query yields the tag name of the third grandchild of the second item under the root, which is a 
"genre" tag.

## Limitations

Currently, the XML processing uses python's ```etree.ElementTree``` - as such the XML document you are
processing must be able to fit into memory.   Very large documents are not yet supported.
