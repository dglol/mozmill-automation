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
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Henrik Skupin <mail@hskupin.info> (Original Author)
#   Geo Mealer <gmealer@mozilla.com>
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

"""Script to download builds for Firefox and Thunderbird from the Mozilla server."""

import ConfigParser
from optparse import OptionParser, OptionGroup
import os
import re
import shutil
import sys
import urllib

from libs import scraper


APPLICATIONS = ['firefox', 'thunderbird']

BUILD_TYPES = {'release': scraper.ReleaseScraper,
               'candidate': scraper.ReleaseCandidateScraper,
               'daily': scraper.DailyScraper }


def clobber_directory(directory):
    """Remove the specified directory"""

    print 'Removing directory: %s' % os.path.abspath(directory)
    if os.path.exists(directory):
        shutil.rmtree(directory)


def initialize_directory(directory, clobber=False):
    """Create or initialize the specified directory and remove all existent
       files if wanted"""

    if clobber:
        clobber_directory(directory)

    print 'Initializing directory: %s' % os.path.abspath(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    """Main function for the downloader"""

    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('--clobber',
                      dest='clobber',
                      action="store_true",
                      metavar='CLOBBER',
                      help='Clean-up the target directory')
    parser.add_option('--config', '-c',
                      dest='config_file',
                      metavar='CONFIG_FILE',
                      help='Config file with a download specification, '
                           'see configs/release_general.cfg.example')
    parser.add_option('--os', '-o',
                      dest='os',
                      metavar='OS',
                      help='Operating system to work on')

    (options, args) = parser.parse_args()

    # For now require a configuration file to be set
    if not options.config_file:
        parser.error("No configuration file has been specified.")

    # Read-in configuration options
    config = ConfigParser.SafeConfigParser()
    config.read(options.config_file)

    # Check testrun entries
    testrun = { }
    for entry in config.options('testrun'):
        testrun.update({entry: config.get('testrun', entry)})
    options.testrun = testrun

    # Create logs directory
    directory = '%(ROOT)s/%(PREFIX)s_logs/' % {
                    'ROOT': options.testrun['directory'],
                    'PREFIX': options.testrun['script']}
    initialize_directory(directory, options.clobber)

    # Iterate through all OS
    for section in config.sections():
        # Retrieve the platform, i.e. win32 or linux64
        if not config.has_option(section, 'platform'):
            continue
        platform = config.get(section, 'platform')

        # Create the directory for the current OS, i.e. '5.0/update_win2000'
        directory = '%(ROOT)s/%(PREFIX)s_%(OS)s/' % {
                        'ROOT': options.testrun['directory'],
                        'PREFIX': options.testrun['script'],
                        'OS': section}
        initialize_directory(directory, options.clobber)

        # Iterate through all builds per platform
        for entry in config.options(section):
            locales = [ ]
            build_type = 'release'

            # Expression to parse versions like: '5.0', '5.0#3', '5.0b1', '5.0b2#1', '10.0esr#1'
            # Explicitly starts with a ##. portion to exclude other keys like platform=
            pattern = re.compile(r'(?P<version>(?:\d+\.)+[^#\s]+)(?:#(?P<build_number>\d+))?')
            try:
                (version, build_number) = pattern.match(entry).group('version', 'build_number')
                locales = config.get(section, entry).split(' ')

                # If a build number has been specified we have a candidate build
                build_type = 'candidate' if build_number else build_type
            except:
                continue

            # Download each listed locale
            for locale in locales:
                # Instantiate scraper and download the build
                scraper_keywords = {'application': options.testrun['application'],
                                    'locale': locale,
                                    'platform': platform,
                                    'version': version,
                                    'directory': directory}
                scraper_options = {'candidate': {'build_number': build_number}}

                kwargs = scraper_keywords.copy()
                kwargs.update(scraper_options.get(build_type, {}))
                build = BUILD_TYPES[build_type](**kwargs)

                build.download()

if __name__ == "__main__":
    main()
