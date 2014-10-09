#!/bin/bash
# 
# This is a sample script to find all POM XML files in your local
# maven repository, and convert them  into loadable cypher.
# This creates one ginormous cypher file called all-poms.cypher,
# which can then be loaded.
#
# For many maven repos, this is going to be a big file.

find ~/.m2 -name "*.pom" -exec ../xml2neo.py {} \; > all-poms.cypher

