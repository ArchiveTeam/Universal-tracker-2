import json
import os

import tornado.web
import tornado.template
import tornado.ioloop

import project
import auth


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

        except KeyError: # Project not found
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

        except KeyError: # Project not found
            self.set_status(404)
            self.write('InvalidProject')

class AdminHandler(tornado.web.RequestHandler):
    """Base class for any admin page except login"""

    def get_current_user(self):

        # Return login cookie
        return self.get_secure_cookie("user")

class admin_login(tornado.web.RequestHandler):
    """Account login function"""

    def get(self):
        msg = self.get_query_argument('msg', default=False)

        # Render login form template
        self.write(html_loader.load(
                    'admin/login.html').generate(msg=msg))

    def post(self):
        # Get login form data
        username = self.get_body_argument('username')
        password = self.get_body_argument('password')

        # Verify if login info is correct
        if auth.verify(username, password) == True:
            self.set_secure_cookie('user', username) # Set login cookie
            self.redirect('/admin')

        else:
            # Upon error, redirect to login with error message
            self.redirect("/admin/login?msg=Invalid%20username%20or%20password")

class admin_logout(AdminHandler):
    """Account logout function"""

    @tornado.web.authenticated # Verify the user is logged in
    def get(self):
        self.clear_all_cookies() # Clear site cookies, and the login cookie.
        self.redirect("/admin/login?msg=Logout%20success") # Redirect to login

class admin(AdminHandler):
    """Main admin page"""

    @tornado.web.authenticated # Verify the user is logged in
    def get(self):
        # Render admin manage template
        self.write(html_loader.load(
                    'admin/manage.html').generate(projects=projects))


class manage_project(AdminHandler):
    """Manage project admin page"""

    @tornado.web.authenticated # Verify the user is logged in
    def get(self, project):
        try:
            # Render manage project template
            self.write(html_loader.load(
                    'admin/project.html').generate(project=projects[project]))

        except KeyError: # Project not found
            self.set_status(404)
            self.write('InvalidProject')

# Template loader object
html_loader = tornado.template.Loader('templates')

projects = {} # Dictionary of project objects

auth = auth.Auth() # Authentication object

for p in os.listdir('projects'):
    if p.endswith('.json') and not p.endswith('leaderboard.json'):
        with open(os.path.join('projects', p), 'r') as jf:

            # Read project info
            project_name = json.loads(jf.read())['project-meta']['name']

        # Create one project object for every project found
        projects[project_name] = project.Project(os.path.join('projects', p))


if __name__ == "__main__":
    PORT = 80 # Set server port

    # Settings for tornado server
    settings = {
        'compiled_template_cache': False,
        'login_url': '/admin/login',
        'cookie_secret': 'CHANGEME',
    }

    # Create url paths
    app = tornado.web.Application([
        (r'/', homepage),

        # API urls
        (r'/(.*?)/item/get', start_item),
        (r'/(.*?)/item/heartbeat', heartbeat),
        (r'/(.*?)/item/done', finish_item),
        (r'/(.*?)/api/leaderboard', get_leaderboard),

        # Admin
        (r'/admin', admin),
        (r'/admin/login', admin_login),
        (r'/admin/logout', admin_logout),
        (r'/admin/project/(.*?)', manage_project),
    ], **settings,
    )

    app.listen(PORT) #start listening on PORT
    print(f'Listening on {PORT}')
    tornado.ioloop.IOLoop.current().start() # Start server
