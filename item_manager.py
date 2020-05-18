import time
import json

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

    def dumpfile(self):
        """Save the current queue"""

        items = []
        items.extend(self.queue_items)
        items.extend(self.inprogress_items.keys())

        return '\n'.join(items) + '\n'

    def getitem(self, username, ip):
        """Gets an item, and moves it to inprogress_items"""

        try:
            # Get first item from queue_items
            item_name = self.queue_items.pop(0)

            # Add item to inprogress_items
            item = {
                'username': username, # Log username
                'ip': ip, # Log ip
                'times': {
                    'starttime': int(time.time()), # Log start time
                }
            }
            self.inprogress_items[item_name] = item

            print(f'giving item {item_name} to {username}')

            # Return json of item
            return {'item_name': item_name}

        except ValueError: # No items left
            return 'NoItemsLeft'

    def heartbeat(self, item_name, ip):
        """Logs heartbeat for item"""
        try:
            item = self.inprogress_items[item_name] # Get item from inprogress_items

            if item['ip'] == ip: # Check if ip is the same as requester
                # Set item heartbeat to now
                self.inprogress_items[item_name]['times']['heartbeat'] = int(time.time())

                return 'Success'

            else:
                return 'IpDoesNotMatch'

        except KeyError:
            return 'InvalidItem'

    def finishitem(self, item_name, ip):
        """Removes item from inprogress_items"""
        try:
            item = self.inprogress_items[item_name] # Get item from inprogress_items

            if item['ip'] == ip: # Check if ip is the same as requester
                self.inprogress_items.pop(item_name) # remove item from inprogress_items
                self.done_items += 1 # Keep track of total number of items finished

                print(f"{item['username']} finished {item_name}")
                return ('Success', item['username'])

            else:
                return 'IpDoesNotMatch'

        except KeyError:
            return 'InvalidItem'
