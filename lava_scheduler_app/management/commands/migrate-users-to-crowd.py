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

import sys
from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from crowd import (
    Crowd,
    CrowdException,
    CrowdNotFoundException,
)

class Command(BaseCommand):

    help = "Migrate OpenID users to Crowd"
    option_list = (
        make_option('--really',
                    action='store_true',
                    default=False,
                    help="Actually perform migration (default - dry run)"),
    ) + BaseCommand.option_list

    def handle(self, *args, **options):
        if not options["really"]:
            print "WARNING: Dry run mode"

        if not settings.AUTH_CROWD_APPLICATION_USER:
            sys.stderr.write("No Crowd credentials found.\n")
            return -1

        crwd = Crowd(settings.AUTH_CROWD_APPLICATION_USER,
                     settings.AUTH_CROWD_APPLICATION_PASSWORD,
                     settings.AUTH_CROWD_SERVER_REST_URI)

        total_users = 0
        matched_users = 0
        matched_by_realname = 0
        migrated_users = 0
        users = User.objects.all().distinct()
        for user in users:
            if user and (user.is_active and user.email):
                print
                print "Processing:", user.username, user.email
                total_users += 1
                crowd_usr = None
                try:
                    try:
                        crowd_usr = crwd.get_user(user.email)
                    except CrowdNotFoundException:
                        crowd_usr = crwd.get_user_by_realname(user.first_name, user.last_name)
                        print "Matched by realname"
                        matched_by_realname += 1
                    matched_users += 1
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
                            if options["really"]:
                                user.save()
                            migrated_users += 1
                except CrowdNotFoundException:
                    print "User not found in Crowd"
                except CrowdException, ex:
                    sys.stderr.write("{0}\n".format(str(ex)))

        print "Total Django users: %d, matched Crowd users: %d (by realname: %d), migrated users: %d" \
              % (total_users, matched_users, matched_by_realname, migrated_users)

        if not options["really"]:
            print "WARNING: Dry run mode"
