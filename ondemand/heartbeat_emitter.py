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

"""
This script generates a periodic heartbeat in order to keep traffic going
across the Mozmill queue. This prevents the on-demand queue daemons from
freezing due to silent sockets closing themselves.
"""

# System default packages
import sys
import datetime
from time import sleep

# Pulse packages
from mozillapulse import publishers
from mozillapulse.messages import base


def main():
    # Make a publisher
    pulse = publishers.PulseTestPublisher()

    # Send the message to the broker through the proper exchange with the
    # correct routing key and payload
    try:
        while 1:
            # Message to send
            mymessage = base.GenericMessage()
            mymessage.routing_parts.append('mozmill.heartbeat')
            mymessage.data['what'] = ('This is a mozmill pulse framework '
                                      'heartbeat')

            now = datetime.datetime.now().isoformat()
            print "Sending heartbeat: %(when)s" % {'when': now}
            pulse.publish(mymessage)
            sleep(60)
    finally:
        # Disconnect to be nice to the server
        pulse.disconnect()


if __name__ == "__main__":
    main()
