from threading import Timer
import json
import os

import item_manager
import leaderboard


class Project:
    """Keep track of items for a project"""

    def __init__(self, config_file):
        self.items = item_manager.Items() # Create items object
        self.leaderboard = leaderboard.Leaderboard() # Create leaderboard object
        self.config_path = config_file

        with open(config_file, 'r') as jf: # Open project config file
            configfile = json.loads(jf.read()) # Load project config

            # Put project config into dictionaries
            self.meta = configfile['project-meta']
            self.status = configfile['project-status']
            self.automation = configfile['automation']

        # Get item files
        self.items_folder = os.path.join('projects', self.meta['items-folder'])
        self.item_files = []
        
        for file in os.listdir(self.items_folder):
            if file.endswith('.txt'):
                self.item_files.append(file)

        self.item_files.sort()

        if not self.status['paused']: # If not paused
            try:
                self.queue_next_items() # Load items into queue
            except IndexError:
                print('Project has no items.')

        # Check if there is a leaderboard json file

        leaderboard_json_file = os.path.join('projects', f"{self.meta['name']}-leaderboard.json")

        if os.path.isdir(leaderboard_json_file):
            # Load leaderboard stats from file
            self.leaderboard.loadfile(leaderboard_json_file)

        Timer(30, self.saveproject).start() # Start saving project every 30s

    def saveproject(self):
        """Save project files every 30 seconds"""

        try:
            if not self.status['paused']: # Make sure project is not paused

                # Write parsed file back to disk. This
                # file will be loaded first upon startup.
                with open(os.path.join(self.items_folder, '.queue-save.txt'), 'w') as f:
                    f.write(self.items.dumpfile())

                # Save leaderboard
                with open(os.path.join('projects', f"{self.meta['name']}-leaderboard.json"), 'w') as ljf:
                    ljf.write(self.leaderboard.get_leaderboard())

        finally:
            # Reset timer
            Timer(30, self.saveproject).start()

    def update_config_file(self):
        """Write changed config back to the config file"""

        configfile = {}
        configfile['project-meta'] = self.meta
        configfile['project-status'] = self.status
        configfile['automation'] = self.automation

        with open(self.config_path, 'w') as jf:
            jf.write(json.dumps(configfile))

    def queue_next_items(self):
        """Get next items file, and load it into queue"""

        # Get file from list, and remove it from the list.
        items_file = os.path.join('projects', self.meta['items-folder'],
                                        self.item_files.pop(0))
        self.items.loadfile(items_file) # Queue items

        print(f'Added {items_file.split(os.sep)[-1]} to the queue.')

        # Remove the text file so it will not load again
        os.remove(items_file)

    # Wrappers for varius tasks
    def get_item(self, username, ip):
        if self.status['paused']: # Check if project is paused
            return 'ProjectNotActive'

        if len(self.items.queue_items) == 0: # Check if queue is empty
            try:
                self.queue_next_items()
            except IndexError:
                return 'NoItemsLeft'

        return self.items.getitem(username, ip)

    def heartbeat(self, item_name, ip):
        return self.items.heartbeat(item_name, ip)

    def finish_item(self, item_name, itemsize, ip):
        done_stat = self.items.finishitem(item_name, ip)

        if done_stat not in ['IpDoesNotMatch', 'InvalidItem']:
            # Add item to downloader's leaderboard entry
            self.leaderboard.additem(done_stat[1], itemsize)

            return done_stat[0]

        else:
            return done_stat

    def get_leaderboard(self):
        return self.leaderboard.get_leaderboard()
