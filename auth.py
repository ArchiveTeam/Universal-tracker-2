import secrets
import time
import json
import re

from passlib.hash import argon2
from itsdangerous import Signer
from itsdangerous.exc import BadSignature
import toml


class Auth:
    def __init__(self):

        try:
            with open('admins.json', 'r') as jf:

                # Load json file with accounts
                self.accounts = json.loads(jf.read())

        except FileNotFoundError:
            self.accounts = {}

        self.signer = Signer(self.config['secret_key'])

    def saveaccounts(self):
        """Saves accounts to disk"""

        # Write out self.accounts to json file
        with open('admins.json', 'w') as jf:
            jf.write(json.dumps(self.accounts))

    def newacct(self, username, password):
        """Creates an account"""

        # Make sure username is under 24 characters and only contains
        # a-b, A-B, 0-9, and underscore.
        if not re.match('^\w{3,24}$', username):
            return 'InvalidName'

        if username.lower() in self.accounts: # Check if username already exists
            return 'AcctExists'

        else:

            # Create account object and hash password using argon2
            self.accounts[username.lower()] = {
                'password': argon2.using(rounds=50).hash(password),
                'sessions': {}
            }

            self.saveaccounts()

    def changepass(self, username, oldpass, newpass):
        """Change password for an account"""

        # Verify that username is correct
        if username.lower() in self.accounts:

            # Verify that credentials are correct
            if self.verify(username, oldpass) == True:

                # Hash new password using argon2
                self.accounts[username.lower()]['password'] = argon2.using(
                                                    rounds=50).hash(newpass)

                self.saveaccounts()

                return 'Success'

            else:
                return 'InvalidPassword'

        else:
            return 'InvalidAcct'

    def removeacct(self, username, password):
        """Delete an account"""

        # Verify that username is correct
        if username.lower() in self.accounts:

            # Verify that credentials are correct
            if self.verify(username, password) == True:

                # Remove the account
                self.accounts.pop(username.lower())
                self.saveaccounts()

                return 'Success'

            else:
                return 'InvalidPassword'

        else:
            return 'InvalidAcct'

    def verify(self, username, password):
        """Verify password for account"""

        try:
            # Check password hashes match
            return argon2.verify(password, self.accounts[username.lower()]['password'])

        except KeyError:
            return 'InvalidAcct'

    def new_session(self, username, name):
        """Create a login session token"""

        session = secrets.token_urlsafe(64) # Generate session token
        # Expire x days in the future
        expire = round(time.time()) + 86400*self.config['session_expire']

        # Make sure username is under 24 characters and only contains
        # a-b, A-B, 0-9, and underscore.
        if not re.match('^\w{3,24}$', name):
            return 'InvalidName'

        if username.lower() in self.accounts: # Verify that username is correct
            self.accounts[username.lower()]['sessions'][session] = {
                'name': name,
                'expire': expire
            }

            self.saveaccounts()

            # Return signed login cookie
            return (self.signer.sign(session).decode('utf-8'), expire)

        else:
            return 'InvalidAcct'

    def verify_session(self, username, signed_session):
        """Verify a login session token"""

        if username.lower() in self.accounts: # Verify that username is correct
            try:
                # Unsign the session cookie
                session = self.signer.unsign(signed_session).decode('utf-8')

                # Check if session is expired
                if round(time.time()) < self.accounts[username.lower()]['sessions'][session]['expire']:
                    return 'Success'

                else:
                    # If session expired, remove the token.
                    self.accounts[username.lower()]['sessions'].pop(session)
                    self.saveaccounts()

                    return 'InvalidSession'

            except (BadSignature, KeyError):
                return 'InvalidSession'

        else:
            return 'InvalidAcct'
