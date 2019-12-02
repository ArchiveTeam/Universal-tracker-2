import json
import os

import tornado.web
import tornado.ioloop

import project


class homepage(tornado.web.RequestHandler):
    """This will eventually serve the tracker homepage"""

    def get(self, x='testing.'):
        self.write(f'Hello World, {x}')

class start_item(tornado.web.RequestHandler):
    """API endpoint for requesting an item"""

    def get(self, project):
        username = self.get_argument('username') # Get url parameter

        try:
            # Get item from the project's item_manager
            item = projects[project].get_item(username, self.request.remote_ip)

            if item == 'NoItemsLeft':
                self.set_status(404)

            self.write(item) # Respond with the output from item_manager

        except KeyError: # Project not fount
            self.set_status(404)
            self.write('InvalidProject')

class heartbeat(tornado.web.RequestHandler):
    """API endpoint for heartbeat"""

    def get(self, project):
        id = self.get_argument('id') # Get url parameter

        try:
            # Tell project's item_manager to set heartbeat
            heartbeat_stat = projects[project].heartbeat(id, self.request.remote_ip)

            # If there is an error setting heartbeat
            if heartbeat_stat in ['IpDoesNotMatch', 'InvalidID']:
                self.set_status(403) # return 403 forbidden

            # Respond with the output from item_manager
            self.write(str(heartbeat_stat))

        except KeyError: # Project not fount
            self.set_status(404)
            self.write('InvalidProject')

class finish_item(tornado.web.RequestHandler):
    """API endpoint for finishing an item"""

    def get(self, project):
        # Get url parameters
        id = self.get_argument('id')
        itemsize = int(self.get_argument('size'))

        try:
            # Tell item_manager to finish item
            done_stat = projects[project].finish_item(id, itemsize, self.request.remote_ip)

            # If there is an error finishing item
            if done_stat in ['IpDoesNotMatch', 'InvalidID']:
                self.set_status(403) # return 403 forbidden

            self.write(str(done_stat)) # Respond with the output from item_manager

        except KeyError: # Project not fount
            self.set_status(404)
            self.write('InvalidProject')

class get_leaderboard(tornado.web.RequestHandler):
    """API endpoint for getting the leaderboard"""

    def get(self, project):
        try:
            # Return the leaderboard
            self.write(projects[project].get_leaderboard())

        except KeyError: # Project not fount
            self.set_status(404)
            self.write('InvalidProject')


# load projects
projects = {}

for p in os.listdir('projects'):
    if p.endswith('.json') and not p.endswith('leaderboard.json'):
        with open(os.path.join('projects', p), 'r') as jf:
            project_name = json.loads(jf.read())['project-meta']['name']

        projects[project_name] = project.Project(os.path.join('projects', p))


if __name__ == "__main__":
    PORT = 80 # Set server port

    # Create url paths
    app = tornado.web.Application([
        (r'/', homepage),

        # API urls
        (r'/(.*?)/item/get', start_item),
        (r'/(.*?)/item/heartbeat', heartbeat),
        (r'/(.*?)/item/done', finish_item),
        (r'/(.*?)/api/leaderboard', get_leaderboard),
    ])

    app.listen(PORT) #start listening on PORT
    print(f'Listening on {PORT}')
    tornado.ioloop.IOLoop.current().start() # Start server
