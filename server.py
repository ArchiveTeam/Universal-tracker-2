import tornado.web
import tornado.ioloop

import item_manager


class homepage(tornado.web.RequestHandler):
    """This will eventually serve the tracker homepage"""
    def get(self):
        self.write('Hello World')

class start_item(tornado.web.RequestHandler):
    """API endpoint for requesting an item"""

    def get(self):
        username = self.get_argument('username') # Get url parameter

        # Get item from item_manager
        item = items.getitem(username, self.request.remote_ip)

        if item == 'NoItemsLeft':
            self.set_status(404) # return 403 forbidden

        self.write(item) # Respond with the output from item_manager


class finish_item(tornado.web.RequestHandler):
    """API endpoint for finishing an item"""

    def get(self):
        id = self.get_argument('id') # Get url parameter

        # Tell item_manager to finish item
        done_stat = items.finishitem(id, self.request.remote_ip)

        # If there is an error finishing item
        if done_stat in ['IpDoesNotMatch', 'InvalidID']:
            self.set_status(403) # return 403 forbidden

        self.write(str(done_stat)) # Respond with the output from item_manager


items = item_manager.Items() # create items object
items.loadfile('items.txt') # Load items


if __name__ == "__main__":
    PORT = 80 # Set server port

    # Create url paths
    app = tornado.web.Application([
        (r'/', homepage),

        # API urls
        (r'/item/get', start_item),
        (r'/item/done', finish_item)
    ])

    app.listen(PORT) #start listening on PORT
    print(f'Listening on {PORT}')
    tornado.ioloop.IOLoop.current().start() # Start server
