import json
import os

from sanic import Sanic
from sanic import response

import project
import auth

app = Sanic()

@app.route('<project>/item/get')
async def get_item(request, project):
    """API endpoint for requesting an item"""

    try:
        username = request.args['username'][0] # Get username

    except KeyError:
        return response.json({'error': 'InvalidParams'}, status=400)

    try:
        # Get item from the project's item_manager
        item = projects[project].get_item(username, request.ip)

        if item == 'NoItemsLeft':
            return response.json({'error': 'NoItemsLeft'}, status=404)

        elif item == 'ProjectNotActive':
            return response.json({'error': 'ProjectNotActive'}, status=404)

        else:
            # Respond with the output from item_manager
            return response.json(item, escape_forward_slashes=False)

    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

@app.route('<project>/item/heartbeat')
async def heartbeat(request, project):
    """API endpoint for heartbeat"""

    try:
        id = request.args['id'] # Get item ID

    except KeyError:
        return response.json({'error': 'InvalidParams'}, status=400)

    try:
        # Tell project's item_manager to set heartbeat
        print(request.args['id'][0], request.ip)
        heartbeat_stat = projects[project].heartbeat(request.args['id'][0], request.ip)

        # If there is an error setting heartbeat
        if heartbeat_stat == 'IpDoesNotMatch':
            return response.json({'error': 'IpDoesNotMatch'}, status=403)

        elif heartbeat_stat == 'InvalidID':
            return response.json({'error': 'InvalidID'}, status=404)

        else:
            # Respond with the output from item_manager
            return response.json({'status': str(heartbeat_stat)})

    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

@app.route('<project>/item/done')
async def finish_item(request, project):
    """API endpoint for finishing an item"""

    try:
        id = request.args['id'][0] # Get item ID
        itemsize = int(request.args['size'][0]) # Get item size

    except (KeyError, ValueError):
        return response.json({'error': 'InvalidParams'}, status=400)

    try:
        # Tell item_manager to finish item
        done_stat = projects[project].finish_item(id, itemsize, request.ip)

        # If there is an error finishing item
        if done_stat == 'IpDoesNotMatch':
            return response.json({'error': 'IpDoesNotMatch'}, status=403)

        elif done_stat == 'InvalidID':
            return response.json({'error': 'InvalidID'}, status=404)

        else:
            # Respond with the output from item_manager
            return response.json({'status': str(done_stat)})

    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

@app.route('<project>/api/leaderboard')
async def get_leaderboard(request, project):
    """API endpoint for getting the leaderboard"""
    
    try:
        # Return the leaderboard
        return response.json(projects[project].get_leaderboard())

    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)


projects = {} # Dictionary of project objects

for p in os.listdir('projects'):
    if p.endswith('.json') and not p.endswith('-leaderboard.json') and not p.endswith('-data.json'):
        with open(os.path.join('projects', p), 'r') as jf:

            # Read project info
            project_name = json.loads(jf.read())['project-meta']['name']

        # Create one project object for every project found
        projects[project_name] = project.Project(os.path.join('projects', p))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=4) ## TODO: Use settings file


## TODO: Port admin functions

# class AdminHandler(tornado.web.RequestHandler):
#     """Base class for any admin page except login"""
#
#     def get_current_user(self):
#
#         # Return login cookie
#         return self.get_secure_cookie("user")
#
# class admin_login(tornado.web.RequestHandler):
#     """Account login function"""
#
#     def get(self):
#         msg = self.get_query_argument('msg', default=False)
#
#         # Render login form template
#         self.write(html_loader.load(
#                     'admin/login.html').generate(msg=msg))
#
#     def post(self):
#         # Get login form data
#         username = self.get_body_argument('username')
#         password = self.get_body_argument('password')
#
#         # Verify if login info is correct
#         if auth.verify(username, password) == True:
#             self.set_secure_cookie('user', username) # Set login cookie
#             self.redirect('/admin')
#
#         else:
#             # Upon error, redirect to login with error message
#             self.redirect("/admin/login?msg=Invalid%20username%20or%20password")
#
# class admin_logout(AdminHandler):
#     """Account logout function"""
#
#     @tornado.web.authenticated # Verify the user is logged in
#     def get(self):
#         self.clear_all_cookies() # Clear site cookies, and the login cookie.
#         self.redirect("/admin/login?msg=Logout%20success") # Redirect to login
#
# class admin(AdminHandler):
#     """Main admin page"""
#
#     @tornado.web.authenticated # Verify the user is logged in
#     def get(self):
#         # Render admin manage template
#         self.write(html_loader.load(
#                     'admin/manage.html').generate(projects=projects))
#
#
# class manage_project(AdminHandler):
#     """Manage project admin page"""
#
#     @tornado.web.authenticated # Verify the user is logged in
#     def get(self, project):
#         try:
#             # Render manage project template
#             self.write(html_loader.load(
#                     'admin/project.html').generate(project=projects[project]))
#
#         except KeyError: # Project not found
#             self.set_status(404)
#             self.write('InvalidProject')
#
# # Template loader object
# html_loader = tornado.template.Loader('templates')
#
# auth = auth.Auth() # Authentication object
#
# if __name__ == "__main__":
#     PORT = 80 # Set server port
#
#     # Settings for tornado server
#     settings = {
#         'compiled_template_cache': False,
#         'login_url': '/admin/login',
#         'cookie_secret': 'CHANGEME',
#     }
#
#     # Create url paths
#     app = tornado.web.Application([
#         (r'/', homepage),
#
#         # API urls
#         (r'/(.*?)/item/get', start_item),
#         (r'/(.*?)/item/heartbeat', heartbeat),
#         (r'/(.*?)/item/done', finish_item),
#         (r'/(.*?)/api/leaderboard', get_leaderboard),
#
#         # Admin
#         (r'/admin', admin),
#         (r'/admin/login', admin_login),
#         (r'/admin/logout', admin_logout),
#         (r'/admin/project/(.*?)', manage_project),
#     ], **settings,
#     )
