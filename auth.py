import json

from passlib.hash import argon2

class Auth:
    def __init__(self):
        try:
            with open('admins.json', 'r') as jf:

                # Load json file with accounts
                self.accounts = json.loads(jf.read())

        except FileNotFoundError:
            self.accounts = {}

    def saveaccounts(self):
        """Saves accounts to disk"""

        # Write out self.accounts to json file
        with open('admins.json', 'w') as jf:
            jf.write(json.dumps(self.accounts))

    def newacct(self, username, password):
        """Creates an account"""

        if username.lower() in self.accounts: # Check if username already exists
            return 'AcctExists'

        else:

            # Hash password using argon2
            self.accounts[username.lower()] = argon2.using(
                                                rounds=50).hash(password)
            self.saveaccounts()

    def changepass(self, username, oldpass, newpass):
        """Change password for an account"""

        # Verify that username is correct
        if username.lower() in self.accounts:

            # Verify that credentials are correct
            if self.verify(username, oldpass) == True:

                # Hash new password using argon2
                self.accounts[username.lower()] = argon2.using(
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

                return 'Success'

            else:
                return 'InvalidPassword'

        else:
            return 'InvalidAcct'

    def verify(self, username, password):
        """Verify password for account"""

        try:
            # Check password hashes match
            return argon2.verify(password, self.accounts[username.lower()])

        except KeyError:
            return 'InvalidAcct'
