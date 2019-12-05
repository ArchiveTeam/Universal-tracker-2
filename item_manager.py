import time
import json

class Items:
    """Manage and keep track of items"""

    def __init__(self):
        self.queue_items = {}
        self.inprogress_items = {}

        # Assign only one id per item
        self.current_id = 0

    def loadfile(self, file):
        """Open a csv file, and create one item per line"""

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

    def dumpfile(self):
        """Save the current queue"""

        values = []
        value_str = ''

        # Extract values
        for key in self.queue_items:
            values.append(self.queue_items[key]['values'])

        for key in self.inprogress_items:
            values.append(self.inprogress_items[key]['values'])

        # Parse values into file
        for value in values:
            for arg in value:
                value_str += f'{arg},' # Add value to line

            value_str += '\n' # Add newline after every list of values

        return value_str

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

        except ValueError: # No items left
            return 'NoItemsLeft'

    def heartbeat(self, id, ip):
        """Logs heartbeat for item"""
        try:
            id = int(id) # Convert item to an integer
            item = self.inprogress_items[id] # Get item from inprogress_items

            if item['ip'] == ip: # Check if ip is the same as requester
                # Set item heartbeat to now
                self.inprogress_items[id]['times']['heartbeat'] = int(time.time())

                return 'Success'

            else:
                return 'IpDoesNotMatch'

        except KeyError:
            return 'InvalidID'

    def finishitem(self, id, ip):
        """Removes item from inprogress_items"""
        try:
            id = int(id) # Convert item to an integer
            item = self.inprogress_items[id] # Get item from inprogress_items

            if item['ip'] == ip: # Check if ip is the same as requester
                self.inprogress_items.pop(id) # remove item from inprogress_items

                print(f"{item['username']} finished {id}")
                return ('Success', item['username'])

            else:
                return 'IpDoesNotMatch'

        except KeyError:
            return 'InvalidID'
