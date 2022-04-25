import time
import json

from exceptions import *

class Items:
    """Manage and keep track of items"""

    def __init__(self):
        self.queue_items = []
        self.inprogress_items = {}
        self.done_items = 0

    def loadfile(self, file):
        """Open a csv file, and create one item per line"""

        with open(file, 'r') as jf:
            for line in jf.readlines():

                # Remove newline character from line
                line = line.replace('\n', '')

                # If line is not a comment, or empty
                if line.startswith('#') == False and line != '':

                    # Create item
                    self.queue_items.append(line)

    def savefile(self, filepath):
        """Save the current queue"""

        items = []
        items.extend(self.queue_items)
        items.extend(self.inprogress_items.keys())

        with open(filepath, 'w') as f:
            f.write('\n'.join(items) + '\n')

    def getitem(self, username, ip):
        """Gets an item, and moves it to inprogress_items"""

        try:
            # Get first item from queue_items
            item_name = self.queue_items.pop(0)
        except ValueError: # No items left
            raise NoItemsLeftException()

        # Add item to inprogress_items
        item = {
            'username': username, # Log username
            'ip': ip, # Log ip
            'times': {
                'starttime': int(time.time()), # Log start time
            }
        }
        self.inprogress_items[item_name] = item

        # Return json of item
        return {'item_name': item_name}

    def heartbeat(self, item_name, ip):
        """Logs heartbeat for item"""
        try:
            item = self.inprogress_items[item_name] # Get item from inprogress_items
        except KeyError:
            raise InvalidItemException()

        if item['ip'] != ip: # Check if ip does not match requester
            raise IpDoesNotMatchException()

        # Set item heartbeat to now
        self.inprogress_items[item_name]['times']['heartbeat'] = int(time.time())

    def finishitem(self, item_name, ip):
        """Removes item from inprogress_items"""
        try:
            item = self.inprogress_items[item_name] # Get item from inprogress_items
        except KeyError:
            raise InvalidItemException()

        if item['ip'] != ip: # Check if ip does not match requester
            raise IpDoesNotMatchException()

        self.inprogress_items.pop(item_name) # remove item from inprogress_items
        self.done_items += 1 # Keep track of total number of items finished

        return item['username']
