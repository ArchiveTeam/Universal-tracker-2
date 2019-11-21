import time
import json

class Items:
    def __init__(self):
        self.queue_items = {}
        self.inprogress_items = {}
        self.done_items = {}
        self.current_id = 0

    def loadfile(self, file):
        with open(file, 'r') as jf:
            for line in jf.readlines():
                line = line.replace('\n', '')

                if line.startswith('#') == False and line != '':
                    self.queue_items[self.current_id] = {
                        'id': self.current_id,
                        'values': line.split(',')
                    }
                    self.current_id += 1

    def getitem(self, username, ip):
        try:
            id = min(self.queue_items, key=int)
            item = self.queue_items.pop(id)

            item['username'] = username
            item['ip'] = ip
            item['times'] = {}
            item['times']['starttime'] = int(time.time())

            self.inprogress_items[id] = item
            print(f'giving id {id} to {username}')
            return json.dumps({'id': item['id'], 'values': item['values']})

        except ValueError:
            return 'NoItemsLeft'

    def finishitem(self, id, ip):
        try:
            id = int(id)
            item = self.inprogress_items[id]

            if item['ip'] == ip:
                self.inprogress_items.pop(id)

                print(f"{item['username']} finished {id}")
                self.done_items[id] = item

                return 'Success'

            else:
                return 'IpDoesNotMatch'

        except KeyError:
            return 'InvalidID'
