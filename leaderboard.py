from datetime import datetime
import json

class Leaderboard:
    """Stores how much data, and how many items a user has completed"""

    def __init__(self):
        self.usernames = {}

    def additem(self, username, itemsize):
        """Adds an item, and it's size to the downloader's leaderboard entry"""

        try:
            # Add one item to leaderboard entry
            self.usernames[username]['items'] += 1

        except KeyError: # Username does not exist in leaderboard
            self.usernames[username] = {} # Create entry for username
            self.usernames[username]['items'] = 1
            self.usernames[username]['data'] = 0

        # Add size of completed item to leaderboard entry
        self.usernames[username]['data'] += itemsize

        # Set last done
        self.usernames[username]['last_done'] = datetime.utcnow().isoformat()

    def get_leaderboard(self):
        """return the entire leaderboard"""

        return self.usernames

    def loadfile(self, filepath):
        """Get leaderboard stats from save file"""

        with open(filepath, 'r') as f:
            self.usernames = json.load(f)

    def savefile(self, filepath):
        """Save leaderboard stats to file"""

        with open(filepath, 'w') as f:
            json.dump(self.usernames, f)
