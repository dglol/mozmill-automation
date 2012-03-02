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

"""Module to handle downloads for different types of Firefox and Thunderbird builds."""


from datetime import datetime
from HTMLParser import HTMLParser
import os
import re
import sys
import urllib


# Base URL for the path to all builds
BASE_URL = 'http://stage.mozilla.org/pub/mozilla.org'

PLATFORM_FRAGMENTS = {'linux': 'linux-i686',
                      'linux64': 'linux-x86_64',
                      'mac': 'mac',
                      'mac64': 'mac64',
                      'win32': 'win32',
                      'win64': 'win64-x86_64'}


class NotFoundException(Exception):
    """Exception for a resource not being found (e.g. no logs)"""
    def __init__(self, message, location):
        self.location = location
        Exception.__init__(self, ': '.join([message, location]))


class DirectoryParser(HTMLParser):
    """Class to parse directory listings"""

    def __init__(self, url):
        HTMLParser.__init__(self)

        self.entries = [ ]
        self.active_url = None

        req = urllib.urlopen(url)
        self.feed(req.read())

    def filter(self, regex):
        pattern = re.compile(regex, re.IGNORECASE)
        return [entry for entry in self.entries if pattern.match(entry)]

    def handle_starttag(self, tag, attrs):
        if not tag == 'a':
            return

        for attr in attrs:
            if attr[0] == 'href':
                self.active_url = attr[1].strip('/')
                return


    def handle_endtag(self, tag):
        if tag == 'a':
            self.active_url = None

    def handle_data(self, data):
        # Only process the data when we are in an active a tag and have an URL
        if not self.active_url:
            return

        name = urllib.quote(data.strip('/'))
        if self.active_url == name:
            self.entries.append(self.active_url)


class MozillaScraper(object):
    """Generic class to download an application from the Mozilla server"""

    def __init__(self, directory, platform, version,
                 application='firefox', locale='en-US'):

        self.directory = directory
        self.locale = locale
        self.platform = platform
        self.version = version

        # build the base URL
        self.application = application
        self.base_url = '/'.join([BASE_URL, self.application])


    @property
    def binary(self):
        """Return the name of the build"""

        # Retrieve all entries from the remote virtual folder
        parser = DirectoryParser(self.path)
        if not parser.entries:
            raise NotFoundException('No entries found', self.path)

        # Download the first matched directory entry
        pattern = re.compile(self.binary_regex, re.IGNORECASE)
        for entry in parser.entries:
            try:
                binary = pattern.match(entry).group()
                return binary
            except:
                # No match, continue with next entry
                continue

        raise NotFoundException("Binary not found in folder", self.path)


    @property
    def binary_regex(self):
        """Return the regex for the binary filename"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)


    @property
    def extension(self):
        """Return the file extension"""

        regex = {'linux': '.tar.bz2',
                 'linux64': '.tar.bz2',
                 'mac': '.dmg',
                 'mac64': '.dmg',
                 'win32': '.exe',
                 'win64': '.exe'}
        return regex[self.platform]


    @property
    def final_url(self):
        """Return the final URL of the build"""

        return '/'.join([self.path, self.binary])


    @property
    def path(self):
        """Return the path to the build"""

        return '/'.join([self.base_url, self.path_regex])


    @property
    def path_regex(self):
        """Return the regex for the path to the build"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)


    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        return PLATFORM_FRAGMENTS[self.platform];


    @property
    def target(self):
        """Return the target file name of the build"""

        return os.path.join(self.directory, self.build_filename(self.binary))


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)


    def download(self):
        """Download the specified file"""

        tmp_file = None

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        try:
            # Don't re-download the build
            if os.path.isfile(os.path.abspath(self.target)):
                print "Build has already been downloaded: %s" % (self.target)
                return

            print 'Downloading build: %s' % (urllib.unquote(self.final_url))
            tmp_file = self.target + ".part"
            urllib.urlretrieve(self.final_url, tmp_file)
            os.rename(tmp_file, self.target)
        except:
            try:
                if tmp_file:
                    os.remove(tmp_file)
            except OSError:
                pass

            raise


class DailyScraper(MozillaScraper):
    """Class to download a daily build from the Mozilla server"""

    def __init__(self, branch='mozilla-central', build_id=None, date=None,
                 build_number=None, *args, **kwargs):

        MozillaScraper.__init__(self, *args, **kwargs)
        self.branch = branch

        # Internally we access builds via index
        if build_number is not None:
            self.build_index = int(build_number) - 1
        else:
            self.build_index = None

        if build_id:
            # A build id has been specified. Split up its components so the date
            # and time can be extracted: '20111212042025' -> '2011-12-12 04:20:25'
            self.date = datetime.strptime(build_id, '%Y%m%d%H%M%S')
            self.builds, self.build_index = self.get_build_info_for_date(self.date)

        elif date:
            # A date (without time) has been specified. Use its value and the
            # build index to find the requested build for that day.
            self.date = datetime.strptime(date, '%Y-%m-%d')
            self.builds, self.build_index = self.get_build_info_for_date(self.date, self.build_index)

        else:
            # If no build id nor date have been specified the lastest available
            # build of the given branch has to be identified. We also have to
            # retrieve the date of the build via its build id.
            url = '%s/nightly/latest-%s/' % (self.base_url, self.branch)

            print 'Retrieving the build status file from %s' % url
            parser = DirectoryParser(url)
            parser.entries = parser.filter(r'.*%s\.txt' % self.platform_regex)
            if not parser.entries:
                message = 'Status file for %s build cannot be found' % self.platform_regex
                raise NotFoundException(message, url)

            # Read status file for the platform, retrieve build id, and convert to a date
            status_file = url + parser.entries[0]
            f = urllib.urlopen(status_file)
            self.date = datetime.strptime(f.readline().strip(), '%Y%m%d%H%M%S')
            self.builds, self.build_index = self.get_build_info_for_date(self.date)


    def get_build_info_for_date(self, date, build_index=None):
        url = '/'.join([self.base_url, self.monthly_build_list_regex])

        print 'Retrieving list of builds from %s' % url
        parser = DirectoryParser(url)
        regex = r'%(DATE)s-(\d+-)+%(BRANCH)s%(L10N)s$' % {
                    'DATE': date.strftime('%Y-%m-%d'),
                    'BRANCH': self.branch,
                    'L10N': '' if self.locale == 'en-US' else '-l10n'}
        parser.entries = parser.filter(regex)
        if not parser.entries:
            message = 'Folder for builds on %s has not been found' % self.date.strftime('%Y-%m-%d')
            raise NotFoundException(message, url)

        if date.hour and date.minute and date.second:
            # If a time is included in the date, use it to determine the build's index
            regex = r'.*%s.*' % date.strftime('%H-%M-%S')
            build_index = parser.entries.index(parser.filter(regex)[0])
        else:
            # If no index has been given, set it to the last build of the day.
            if build_index is None:
                build_index = len(parser.entries) - 1

        return (parser.entries, build_index)


    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex_base_name = r'^%(APP)s-.*\.%(LOCALE)s\.%(PLATFORM)s'
        regex_suffix = {'linux': r'\.tar\.bz2$',
                        'linux64': r'\.tar\.bz2$',
                        'mac': r'\.dmg$',
                        'mac64': r'\.dmg$',
                        'win32': r'.*\.exe$',
                        'win64': r'.*\.exe$'}
        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'APP': self.application,
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        try:
            # Get exact timestamp of the build to build the local file name
            folder = self.builds[self.build_index]
            timestamp = re.search('([\d\-]+)-\D.*', folder).group(1)
        except:
            # If it's not available use the build's date
            timestamp = self.date.strftime('%Y-%m-%d')

        return '%(TIMESTAMP)s-%(BRANCH)s-%(NAME)s' % {
                   'TIMESTAMP': timestamp,
                   'BRANCH': self.branch,
                   'NAME': binary}


    @property
    def monthly_build_list_regex(self):
        """Return the regex for the folder which contains the builds of a month."""

        # Regex for possible builds for the given date
        return r'nightly/%(YEAR)s/%(MONTH)s/' % {
                  'YEAR': self.date.year,
                  'MONTH': str(self.date.month).zfill(2) }


    @property
    def path_regex(self):
        """Return the regex for the path"""

        try:
            return self.monthly_build_list_regex + self.builds[self.build_index]
        except:
            raise NotFoundException("Specified sub folder cannot be found",
                                    self.base_url + self.monthly_build_list_regex)


class ReleaseScraper(MozillaScraper):
    """Class to download a release build from the Mozilla server"""

    def __init__(self, *args, **kwargs):
        MozillaScraper.__init__(self, *args, **kwargs)

    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex = {'linux': r'^%s-.*.tar.bz2$',
                 'linux64': r'^%s-.*.tar.bz2$',
                 'mac': r'^%s.*.dmg$',
                 'mac64': r'^%s.*.dmg$',
                 'win32': r'^%s.*.exe$',
                 'win64': r'^%s.*.exe$'}
        return regex[self.platform] % self.application


    @property
    def path_regex(self):
        """Return the regex for the path"""

        regex = r'releases/%(VERSION)s/%(PLATFORM)s/%(LOCALE)s'
        return regex % {'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'VERSION': self.version}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        template = '%(APP)s-%(VERSION)s.%(LOCALE)s.%(PLATFORM)s%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'EXT': self.extension}


class ReleaseCandidateScraper(ReleaseScraper):
    """Class to download a release candidate build from the Mozilla server"""

    def __init__(self, build_number=None, no_unsigned=False, *args, **kwargs):
        MozillaScraper.__init__(self, *args, **kwargs)

        # Internally we access builds via index
        if build_number is not None:
            self.build_index = int(build_number) - 1
        else:
            self.build_index = None

        self.builds, self.build_index = self.get_build_info_for_version(self.version, self.build_index)

        self.no_unsigned = no_unsigned
        self.unsigned = False


    def get_build_info_for_version(self, version, build_index=None):
        url = '/'.join([self.base_url, self.candidate_build_list_regex])

        print 'Retrieving list of candidate builds from %s' % url
        parser = DirectoryParser(url)
        if not parser.entries:
            message = 'Folder for specific candidate builds at has not been found'
            raise NotFoundException(message, url)

        # If no index has been given, set it to the last build of the given version.
        if build_index is None:
            build_index = len(parser.entries) - 1

        return (parser.entries, build_index)


    @property
    def candidate_build_list_regex(self):
        """Return the regex for the folder which contains the builds of
           a candidate build."""

        # Regex for possible builds for the given date
        return r'nightly/%(VERSION)s-candidates/' % {
                 'VERSION': self.version }


    @property
    def path_regex(self):
        """Return the regex for the path"""

        regex = r'%(PREFIX)s%(BUILD)s/%(UNSIGNED)s%(PLATFORM)s/%(LOCALE)s'
        return regex % {'PREFIX': self.candidate_build_list_regex,
                        'BUILD': self.builds[self.build_index],
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'UNSIGNED': "unsigned/" if self.unsigned else ""}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        template = '%(APP)s-%(VERSION)s-build%(BUILD)s.%(LOCALE)s.%(PLATFORM)s%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'BUILD': self.builds[self.build_index],
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'EXT': self.extension}


    def download(self):
        """Download the specified file"""

        try:
            # Try to download the signed candidate build
            MozillaScraper.download(self)
        except NotFoundException, e:
            print str(e)

            # If the signed build cannot be downloaded and unsigned builds are
            # allowed, try to download the unsigned build instead
            if self.no_unsigned:
                raise
            else:
                print "Signed build has not been found. Falling back to unsigned build."
                self.unsigned = True
                MozillaScraper.download(self)
