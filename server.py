import asyncio
import json
import os
import re

from sanic import Sanic
from sanic import response
from sanic.log import logger
import yaml

from exceptions import *
import project
import auth

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

app = Sanic(name='universal-tracker-2')

@app.post('<project_name>/request')
async def request(request, project_name):
    """API endpoint for requesting an item"""

    try:
        username = request.json['downloader'] # Get username
    except KeyError:
        return response.json({'error': 'InvalidParams'}, status=400)

    # Make sure username is under 24 characters and only contains
    # a-b, A-B, 0-9, and underscore.
    if not re.match(r'^\w{3,24}$', username):
        return response.json({'error': 'InvalidUsername'}, status=400)

    try:
        project = projects[project_name]
    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

    try:
        # Get item from the project's item_manager
        item = project.get_item(username, request.ip)
    except ProjectNotActiveException:
        return response.json({'error': 'ProjectNotActive'}, status=404)
    except NoItemsLeftException:
        return response.json({'error': 'NoItemsLeft'}, status=404)

    # Respond with the output from item_manager
    return response.json(item, escape_forward_slashes=False)

@app.post('<project_name>/heartbeat')
async def heartbeat(request, project_name):
    """API endpoint for heartbeat"""

    try:
        item_name = request.json['item'] # Get item
    except KeyError:
        return response.json({'error': 'InvalidParams'}, status=400)

    try:
        project = projects[project_name]
    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

    try:
        # Tell project's item_manager to set heartbeat
        print(item_name, request.ip)
        project.heartbeat(item_name, request.ip)
    except InvalidItemException:
        return response.json({'error': 'InvalidItem'}, status=404)
    except IpDoesNotMatchException:
        return response.json({'error': 'IpDoesNotMatch'}, status=403)

    return response.json({'status': 'Success'})

@app.post('<project_name>/done')
async def done(request, project_name):
    """API endpoint for finishing an item"""

    try:
        item_name = request.json['item'] # Get item
        itemsize = int(sum(request.json['bytes'].values())) # Get item size
    except (KeyError, ValueError):
        return response.json({'error': 'InvalidParams'}, status=400)

    try:
        project = projects[project_name]
    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

    try:
        # Tell item_manager to finish item
        project.finish_item(item_name, itemsize, request.ip)
    except InvalidItemException:
        return response.json({'error': 'InvalidItem'}, status=404)
    except IpDoesNotMatchException:
        return response.json({'error': 'IpDoesNotMatch'}, status=403)

    return response.text('OK')

@app.route('<project_name>/api/leaderboard')
async def get_leaderboard(request, project_name):
    """API endpoint for getting the leaderboard"""

    try:
        project = projects[project_name]
    except KeyError: # Project not found
        return response.json({'error': 'InvalidProject'}, status=404)

    # Return the leaderboard
    return response.json(project.get_leaderboard())

async def periodic_save():
    """Periodic project saving loop"""

    while True:
        await asyncio.sleep(30)

        for project_name in projects:
            try:
                projects[project_name].saveproject()
            except:
                logger.exception('Error while periodically saving projects')

@app.listener('after_server_start')
async def after_server_start(app, loop):
    """Create periodic project save task after server start"""

    app.periodic_save_task = loop.create_task(periodic_save())

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    """Cancel periodic project save task before server stop"""

    app.periodic_save_task.cancel()

@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    """Save projects on server stop"""

    logger.info("Saving projects")

    for project_name in projects:
        try:
            projects[project_name].saveproject()
        except:
            logger.exception('Error while saving projects')

projects = {} # Dictionary of project objects

for p in os.listdir('projects'):
    if p.endswith('.json') and not p.endswith('-leaderboard.json') and not p.endswith('-data.json'):
        with open(os.path.join('projects', p), 'r') as jf:

            # Read project info
            project_name = json.loads(jf.read())['project-meta']['name']

        # Create one project object for every project found
        projects[project_name] = project.Project(os.path.join('projects', p))

if __name__ == "__main__":
    # WARNING: The current code is not thread-safe. If you care for your data, never set more than a single worker.
    app.run(host=config['host'], port=config['port'], workers=1)


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
