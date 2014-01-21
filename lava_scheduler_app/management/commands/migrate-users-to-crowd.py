#!/usr/bin/python
# Copyright (C) 2013 Linaro
#
# Author: Milo Casagrande <milo.casagrande@linaro.org>
# This file is part of the Patchmetrics package.
#
# Patchmetrics is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Patchmetrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchmetrics; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import _pythonpath
import sys

from django.conf import settings
from django.contrib.auth.models import User

from patchmetrics.crowd import (
    Crowd,
    CrowdException,
    CrowdNotFoundException,
)

if __name__ == '__main__':
    if settings.AUTH_CROWD_APPLICATION_USER:
        crwd = Crowd(settings.AUTH_CROWD_APPLICATION_USER,
                     settings.AUTH_CROWD_APPLICATION_PASSWORD,
                     settings.AUTH_CROWD_SERVER_REST_URI)

        users = User.objects.all().distinct()
        for user in users:
            if user and (user.is_active and user.email):
                crowd_usr = None
                try:
                    crowd_usr = crwd.get_user(user.email)
                    if crowd_usr.name != user.username:
                        if len(user.email) > 255:
                            sys.stderr.write(
                                "Impossible to save user, email is longer "
                                "than 255 chars: {0}\n".format(user.email))
                            continue
                        else:
                            split_name = crowd_usr.display_name.split()
                            user.first_name = split_name[0]
                            user.last_name = " ".join(split_name[1:])
                            # Use the email from crowd, since some users looks
                            # like have an email with capital letters that
                            # shouldn't be.
                            user.username = crowd_usr.emails[0]
                            user.save()
                except CrowdNotFoundException:
                    # Silently ignore, user is not in Crowd we can't really do
                    # much here.
                    pass
                except CrowdException, ex:
                    sys.stderr.write("{0}\n".format(str(ex)))
    else:
        sys.stderr.write("No Crowd credentials found.\n")
        sys.exit(1)
