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
# Portions created by the Initial Developer are Copyright (C) 2010, 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
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
# ***** END LICENSE BLOCK ***** */


"""Pushes a request for an on-demand release test to the listener. Options will
be passed to the test script run by the listener. Only listeners for the
specified cluster will run tests. If platform is specified, only listeners
for that platform within the specified cluster will run tests."""

# System default packages
import sys
from optparse import OptionParser

# Pulse packages
from mozillapulse import publishers
from mozillapulse.messages import base


def main():
    # args/opts
    usage = """%prog [options] update cluster branch channel
       %prog [options] functional cluster branch"""

    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('-p', '--platform',
                      action='store', type='string', dest='platform',
                      help='platform to push to [default: all]')
    (options, args) = parser.parse_args()


    # quick precheck
    if len(args) == 0:
        parser.error('incorrect number of arguments');

    # per-type checks
    test_type = args[0].lower()
    if test_type == 'update':
        # update branch channel
        if len(args) != 4:
            parser.error('incorrect number of arguments');

        cluster = args[1]
        branch = args[2]
        channel = args[3]
    elif test_type == 'functional':
        # functional branch
        if len(args) != 3:
            parser.error('incorrect number of arguments');

        cluster = args[1]
        branch = args[2]
        channel = None
    else:
        parser.error('unknown test type: "%(type)s"' % {'type': test_type})

    # Message to send
    mymessage = base.GenericMessage()
    mymessage.routing_parts.append('mozmill.%(type)s' % {'type': test_type})
    mymessage.data['what'] = ('This is a mozmill on-demand %(type)s test '
                              'request') % {'type': test_type}

    # Add the cluster key
    mymessage.data['cluster'] = cluster
    cluster_string = 'cluster=%(cluster)s' % {'cluster': cluster}

    # Add the platform key
    if options.platform:
        mymessage.data['platform'] = options.platform
        platform_string = 'platform=%(platform)s' % {
            'platform': options.platform}
    else:
        mymessage.data['platform'] = None
        platform_string = 'all platforms'

    # This part differs per test type
    if test_type == 'update':
        mymessage.data['branch'] = branch
        mymessage.data['channel'] = channel
        option_string = 'branch=%(branch)s, channel=%(channel)s' % {
            'branch': branch, 'channel': channel}
    elif test_type == 'functional':
        mymessage.data['branch'] = branch
        option_string = 'branch=%(branch)s' % {'branch': branch}
    else:
        raise Error('Unknown test type: %(type)s' % {'type': test_type})

    # Let the user know what we're running
    print ('Requesting %(type)s tests for %(platform)s (%(cluster)s), '
           '%(opts)s') % {'type': test_type, 'platform': platform_string,
                          'cluster': cluster_string, 'opts': option_string}

    # Make a publisher
    pulse = publishers.PulseTestPublisher()

    try:
        # Send the message to the broker through the proper exchange with the
        # correct routing key and payload
        pulse.publish(mymessage)
    finally:
        # Disconnect to be nice to the server
        pulse.disconnect()


if __name__ == "__main__":
    main()
