# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class NotFoundException(Exception):
    """Class for a resource not being found exception."""

    def __init__(self, message, location):
        self.location = location
        Exception.__init__(self, ': '.join([message, location]))
