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

"""Script to download builds for Firefox and Thunderbird from the Mozilla server."""

from optparse import OptionParser, OptionGroup
import os
import sys

from libs import scraper


APPLICATIONS = ['firefox', 'thunderbird']

BUILD_TYPES = {'release': scraper.ReleaseScraper,
               'candidate': scraper.ReleaseCandidateScraper,
               'daily': scraper.DailyScraper }


def main():
    """Main function for the downloader"""

    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('--application', '-a',
                      dest='application',
                      choices=APPLICATIONS,
                      default=APPLICATIONS[0],
                      metavar='APPLICATION',
                      help='The name of the application to download, '
                           'default: "%s"' % APPLICATIONS[0])
    parser.add_option('--directory', '-d',
                      dest='directory',
                      default=os.getcwd(),
                      metavar='DIRECTORY',
                      help='Target directory for the download, default: '
                           'current working directory')
    parser.add_option('--build-number',
                      dest='build_number',
                      default=None,
                      type="int",
                      metavar='BUILD_NUMBER',
                      help='Number of the build (for candidate and daily builds)')
    parser.add_option('--locale', '-l',
                      dest='locale',
                      default='en-US',
                      metavar='LOCALE',
                      help='Locale of the application, default: "en-US"')
    parser.add_option('--platform', '-p',
                      dest='platform',
                      choices=scraper.PLATFORM_FRAGMENTS.keys(),
                      metavar='PLATFORM',
                      help='Platform of the application')
    parser.add_option('--type', '-t',
                      dest='type',
                      choices=BUILD_TYPES.keys(),
                      default=BUILD_TYPES.keys()[0],
                      metavar='BUILD_TYPE',
                      help='Type of build to download, default: "%s"' %
                           BUILD_TYPES.keys()[0])
    parser.add_option('--version', '-v',
                      dest='version',
                      metavar='VERSION',
                      help='Version of the application to be used by release and\
                            candidate builds, i.e. "3.6"')

    # Option group for candidate builds
    group = OptionGroup(parser, "Candidate builds",
                        "Extra options for candidate builds.")
    group.add_option('--no-unsigned',
                     dest='no_unsigned',
                     action="store_true",
                     help="Don't allow to download unsigned builds if signed\
                           builds are not available")
    parser.add_option_group(group)

    # Option group for daily builds
    group = OptionGroup(parser, "Daily builds",
                        "Extra options for daily builds.")
    group.add_option('--branch',
                     dest='branch',
                     default='mozilla-central',
                     metavar='BRANCH',
                     help='Name of the branch, default: "mozilla-central"')
    parser.add_option('--build-id',
                      dest='build_id',
                      default=None,
                      metavar='BUILD_ID',
                      help='ID of the build to download')
    group.add_option('--date',
                     dest='date',
                     default=None,
                     metavar='DATE',
                     help='Date of the build, default: latest build')
    parser.add_option_group(group)

    # TODO: option group for nightly builds
    (options, args) = parser.parse_args()

    # Check for required options and arguments
    # Note: Will be optional when ini file support has been landed
    if not options.type == "daily" and not options.version:
        parser.error("The version of the application to download has not been specified.")
    if not options.platform:
        parser.error("The platform of the application to download has not been specified.")

    # Instantiate scraper and download the build
    scraper_keywords = {'application': options.application,
                        'locale': options.locale,
                        'platform': options.platform,
                        'version': options.version,
                        'directory': options.directory}
    scraper_options = {'candidate': {
                           'build_number': options.build_number,
                           'no_unsigned': options.no_unsigned},
                       'daily': {
                           'branch': options.branch,
                           'build_number': options.build_number,
                           'build_id': options.build_id,
                           'date': options.date }}

    kwargs = scraper_keywords.copy()
    kwargs.update(scraper_options.get(options.type, {}))
    build = BUILD_TYPES[options.type](**kwargs)

    build.download()

if __name__ == "__main__":
    main()
