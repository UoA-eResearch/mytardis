"""
Management utility to create regular users.
"""

import getpass
import re
import sys

from django.contrib.auth.models import User
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from ...auth.localdb_auth import auth_key as locabdb_auth_key
from ...models import UserAuthentication

RE_VALID_USERNAME = re.compile("[\w.@+-]+$")

EMAIL_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'  # quoted-string
    r")@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$",
    re.IGNORECASE,
)  # domain


def is_valid_email(value):
    if not EMAIL_RE.search(value):
        raise exceptions.ValidationError(_("Enter a valid e-mail address."))


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments

        # Named (optional) arguments
        parser.add_argument(
            "--username",
            default=None,
            dest="username",
            help="Specifies the username for the user.",
        )
        parser.add_argument(
            "--email",
            default=None,
            dest="email",
            help="Specifies the email address for the user.",
        )
        parser.add_argument(
            "--noinput",
            default=True,
            dest="interactive",
            action="store_false",
            help=(
                "Tells Django to NOT prompt the user for input of any kind. "
                "You must use --username and --email with --noinput, and "
                "users created with --noinput will not be able to log "
                "in until they're given a valid password."
            ),
        )

    help = "Used to create a MyTardis user."

    def handle(self, *args, **options):
        username = options.get("username", None)
        email = options.get("email", None)
        interactive = options.get("interactive")
        verbosity = int(options.get("verbosity", 1))
        get_username = options.get(
            "get_username", lambda input_msg: input(input_msg + ": ")
        )
        get_email = options.get("get_email", lambda: input("E-mail address: "))
        get_password = options.get("get_password", getpass.getpass)

        # Do quick and dirty validation if --noinput
        if not interactive:
            if not username or not email:
                raise CommandError(
                    "You must use --username and --email with --noinput."
                )
            if not RE_VALID_USERNAME.match(username):
                raise CommandError(
                    "Invalid username. Use only letters, digits, and underscores"
                )
            try:
                is_valid_email(email)
            except exceptions.ValidationError:
                raise CommandError("Invalid email address.")

        # If not provided, create the user with an unusable password
        password = None

        # Try to determine the current system user's username to use as a default.
        try:
            default_username = getpass.getuser().replace(" ", "").lower()
        except (ImportError, KeyError):
            # KeyError will be raised by os.getpwuid() (called by getuser())
            # if there is no corresponding entry in the /etc/passwd file
            # (a very restricted chroot environment, for example).
            default_username = ""

        # Determine whether the default username is taken, so we don't display
        # it as an option.
        if default_username:
            try:
                User.objects.get(username=default_username)
            except User.DoesNotExist:
                pass
            else:
                default_username = ""

        # Prompt for username/email/password. Enclose this whole thing in a
        # try/except to trap for a keyboard interrupt and exit gracefully.
        if interactive:
            try:
                # Get a username
                while 1:
                    if not username:
                        input_msg = "Username"
                        if default_username:
                            input_msg += " (Leave blank to use %r)" % default_username
                        username = get_username(input_msg)
                    if default_username and username == "":
                        username = default_username
                    if not RE_VALID_USERNAME.match(username):
                        sys.stderr.write(
                            "Error: That username is invalid. Use only letters, digits and underscores.\n"
                        )
                        username = None
                        continue
                    try:
                        User.objects.get(username=username)
                    except User.DoesNotExist:
                        break
                    else:
                        sys.stderr.write("Error: That username is already taken.\n")
                        username = None

                # Get an email
                while 1:
                    if not email:
                        email = get_email()
                    try:
                        is_valid_email(email)
                    except exceptions.ValidationError:
                        sys.stderr.write("Error: That e-mail address is invalid.\n")
                        email = None
                    else:
                        break

                # Get a password
                while 1:
                    if not password:
                        password = get_password("Password: ")
                        password2 = get_password("Password (again): ")
                        if password != password2:
                            sys.stderr.write("Error: Your passwords didn't match.\n")
                            password = None
                            continue
                    if password.strip() == "":
                        sys.stderr.write("Error: Blank passwords aren't allowed.\n")
                        password = None
                        continue
                    break
            except KeyboardInterrupt:
                sys.stderr.write("\nOperation cancelled.\n")
                sys.exit(1)

        user = User.objects.create_user(username, email, password)

        authentication = UserAuthentication(
            userProfile=user.userprofile,
            username=username,
            authenticationMethod=locabdb_auth_key,
        )
        authentication.save()

        if verbosity >= 1:
            self.stdout.write("MyTardis user created successfully.\n")
