#!/usr/bin/python
# encoding: utf-8
'''
xml2neo -- tools for converting XML into a format suitable for neo4j

xml2neo is a tool for converting XML into a format suitable for neo4j.

More documentation TBD....

@author:     moxious

@copyright:  2014 All rights reserved.

@license:    Apache 2.0

@contact:    moxious@oldhat.org
'''

import sys
import os
import xml2neo.Xml2Cypher

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-10-09'
__updated__ = '2014-10-09'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2014 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        # parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        # parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
        # parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='*')
                            #help="paths to file(s) [default: %(default)s]", metavar="path", nargs="+")

        # Process arguments        
        args = parser.parse_args()        

        paths = args.paths
        verbose = args.verbose
        # recurse = args.recurse
        # inpat = args.include
        # expat = args.exclude

        if verbose > 0:
            print("Verbose mode on")
            #if recurse:
            #    print("Recursive mode on")
            #else:
            #    print("Recursive mode off")

        # if inpat and expat and inpat == expat:
        #     raise CLIError("include and exclude pattern are equal! Nothing will be processed.")

        if len(paths) > 0:
            for inpath in paths:
                ### do something with inpath ###
                fp = open(inpath, mode="rb")
                xml2neo.Xml2Cypher.Xml2Cypher().convert(fp)
                fp.close()
        else:
            xml2neo.Xml2Cypher.Xml2Cypher().convert(sys.stdin)            
            
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    #except Exception, e:
    #    if DEBUG or TESTRUN:
    #        raise(e)
    #    indent = len(program_name) * " "
    #    sys.stderr.write(program_name + ": " + repr(e) + "\n")
    #    sys.stderr.write(indent + "  for help use --help")
    #    return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'xml2neo_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())