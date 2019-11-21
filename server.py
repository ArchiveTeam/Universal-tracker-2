import tornado.web
import tornado.ioloop

import item_manager


class basicrh(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello World')

class start_item(tornado.web.RequestHandler):
    def get(self):
        username = self.get_argument('username')
        item = items.getitem(username, self.request.remote_ip)

        if item == 'NoItemsLeft':
            self.set_status(404)

        self.write(item)


class finish_item(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument('id')
        done_stat = items.finishitem(id, self.request.remote_ip)

        if done_stat in ['IpDoesNotMatch', 'InvalidID']:
            self.set_status(403)

        self.write(str(done_stat))


items = item_manager.Items()
items.loadfile('items.txt')


if __name__ == "__main__":
    PORT = 80

    app = tornado.web.Application([
        (r'/', basicrh),
        (r'/item/get', start_item),
        (r'/item/done', finish_item)
    ])


    app.listen(PORT)
    print(f'Listening on {PORT}')
    tornado.ioloop.IOLoop.current().start()
