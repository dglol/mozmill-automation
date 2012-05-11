#!/usr/bin/env python

# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is MozMill automation code.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Henrik Skupin <hskupin@mozilla.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

import ConfigParser
import copy
import optparse
import os
import sys

from libs.testrun import *


def main():
    general_args = []

    usage = "usage: %prog [options] config_file"
    parser = optparse.OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option("--logfile",
                      default=None,
                      dest="logfile",
                      metavar="PATH",
                      help="Path to the log file")
    (options, args) = parser.parse_args()

    if not args:
        parser.error("A configuration file has to be specified as argument.")

    if options.logfile:
        general_args.append('--logfile=%s' % options.logfile)

    # Read all data from the config file
    try:
        filename = os.path.abspath(args[0])
        config = ConfigParser.RawConfigParser()
        config.read(filename)

        # Check the URL for sending reports
        url = config.get('reports', 'url')
        if url:
            general_args.append('--report=%s' % url)

        # Get the list of binaries for the current platform
        general_args.extend([binary for name, binary in config.items(sys.platform)])
    except Exception, e:
        print str(e)
        sys.exit(1)


    testruns = [UpdateTestRun,
                FunctionalTestRun,
                RemoteTestRun,
                EnduranceTestRun,
                AddonsTestRun,
                L10nTestRun ]
    testrun_options = {EnduranceTestRun: [
                            '--iterations=%s' % 50,
                            '--entities=%s' % 10 ],
                       AddonsTestRun: [
                            '--with-untrusted' ]
                      }

    # To exit with another exit code we have to store the latest exception
    tests_failed_exception = None

    for testrun in testruns:
        try:
            args = copy.copy(general_args)
            args.extend(testrun_options.get(testrun, [ ]))
            testrun(args).run()

        except TestFailedException, e:
            tests_failed_exception = e

        except Exception, e:
            print str(e)

    if tests_failed_exception:
        sys.exit(2)


if __name__ == '__main__':
    main()
