import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from datetime import datetime
import json
import sys
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

class CrumbleClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Connected to server")

    def onMessage(self, payload, isBinary):
        self.factory.app.handle_update(json.loads(payload))

    def onClose(self, wasClean, code, reason):
        print("Websocket connection closed: {0}".format(reason))

class Circuit(BoxLayout):
    name_label = ObjectProperty(None)
    userlist_layout = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(Circuit, self).__init__(**kwargs)

class HomeScreen(Screen):
    circuit_grid = ObjectProperty(None)
    clock_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_clock, 0.5)

    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("%a %d %b\n%H:%m:%S")

    def update_circuits(self, circuits):
        self.circuit_grid.clear_widgets()
        for circuit in circuits:
            circuit_widget = Circuit()
            circuit_widget.name_label.text = circuit['Name']
            for user in circuit['Users']:
                user_label = Label(text=user['Name'])
                circuit_widget.userlist_layout.add_widget(user_label)
            self.circuit_grid.add_widget(circuit_widget)


class CrumbleApp(App):
    server = ''
    def run(self, server, **kwargs):
        self.server = server
        super(CrumbleApp, self).run(**kwargs)

    def handle_update(self, data):
        self.homescreen.update_circuits(data['Circuits'])

    def build(self):
        print 'Connecting to server: ' + self.server
        factory = WebSocketClientFactory(u'ws://'+ self.server)
        factory.protocol = CrumbleClientProtocol
        factory.app = self
        reactor.connectTCP(self.server.split(":")[0], int(self.server.split(":")[1]), factory)
        sm = ScreenManager()
        self.homescreen = HomeScreen(name='home')
        sm.add_widget(self.homescreen)
        return sm

if __name__ == '__main__':
    CrumbleApp().run(sys.argv[1])
