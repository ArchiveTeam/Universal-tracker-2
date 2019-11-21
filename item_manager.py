import time
import json

class Items:
    """Manage and keep track of items"""

    def __init__(self):
        self.queue_items = {}
        self.inprogress_items = {}
        self.done_items = {}

        # Assign only one id per item
        self.current_id = 0

    def loadfile(self, file):
        # Open a csv file, and create one item per line

        with open(file, 'r') as jf:
            for line in jf.readlines():

                # Remove newline character from line
                line = line.replace('\n', '')

                # If line is not a comment, or empty
                if line.startswith('#') == False and line != '':

                    # Create item
                    self.queue_items[self.current_id] = {
                        'id': self.current_id,
                        'values': line.split(',')
                    }

                    self.current_id += 1 # Add one to the current id

    def getitem(self, username, ip):
        """Gets an item, and moves it to inprogress_items"""

        try:
            # Get item with the lowest id from queue_items
            id = min(self.queue_items, key=int)
            item = self.queue_items.pop(id)

            # Add item to inprogress_items
            item['username'] = username # Log username
            item['ip'] = ip # Log ip
            item['times'] = {}
            item['times']['starttime'] = int(time.time()) # Log start time
            self.inprogress_items[id] = item

            print(f'giving id {id} to {username}')

            # Return json of item
            return json.dumps({'id': item['id'], 'values': item['values']})

        except ValueError: # no items left
            return 'NoItemsLeft'

    def finishitem(self, id, ip):
        """Gets an item in progress, and moves it to done_items"""
        try:
            id = int(id) # Convert item to an integer
            item = self.inprogress_items[id] # Get item from inprogress_items

            if item['ip'] == ip: # Check if ip is the same as requester
                self.inprogress_items.pop(id) # remove item from inprogress_items

                item['times']['finishtime'] = int(time.time()) # Log finish time

                self.done_items[id] = item # add item to done_items

                print(f"{item['username']} finished {id}")
                return 'Success'

            else:
                return 'IpDoesNotMatch'

        except KeyError:
            return 'InvalidID'
