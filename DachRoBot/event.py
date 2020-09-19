import ast
import os

fileName = "event.txt"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Event(metaclass=Singleton):
    def __init__(self):
        tmp = self.load_initial_file()
        self._data = {'pinned_message_id': tmp['pinned_message_id'],
                      'pinned_message_user': tmp['pinned_message_user'],
                      'pinned_event': tmp['pinned_event'],
                      'chat_id': tmp['chat_id'],
                      'maxTickets': tmp['maxTickets'],
                      'event_text': tmp['event_text'],
                      'limited': tmp['limited'],
                      'guests': tmp['guests']}

    @property
    def pinned_message_id(self):
        return self._data['pinned_message_id']

    @property
    def pinned_message_user(self):
        return self._data['pinned_message_user']

    @property
    def pinned_event(self):
        return self._data['pinned_event']

    @property
    def chat_id(self):
        return self._data['chat_id']

    @property
    def maxTickets(self):
        return self._data['maxTickets']

    @property
    def event_text(self):
        return self._data['event_text']

    @property
    def limited(self):
        return self._data['limited']

    @property
    def guests(self):
        return self._data['guests']

    @pinned_message_id.setter
    def pinned_message_id(self, value):
        self._data['pinned_message_id'] = value
        self.save_file()

    @pinned_message_user.setter
    def pinned_message_user(self, value):
        self._data['pinned_message_user'] = value
        self.save_file()

    @pinned_event.setter
    def pinned_event(self, value):
        self._data['pinned_event'] = value
        self.save_file()

    @chat_id.setter
    def chat_id(self, value):
        self._data['chat_id'] = value
        self.save_file()

    @maxTickets.setter
    def maxTickets(self, value):
        self._data['maxTickets'] = value
        self.save_file()

    @event_text.setter
    def event_text(self, value):
        self._data['event_text'] = value
        self.save_file()

    @limited.setter
    def limited(self, value):
        self._data['limited'] = value
        self.save_file()

    @guests.setter
    def guests(self, value):
        self._data['guests'] = value
        self.save_file()

    def upsertGuest(self, name, personCount):
        if name in self._data['guests']:
            self._data['guests'][name] += personCount
        else:
            self._data['guests'][name] = personCount
        self.save_file()

    def deleteGuest(self, name):
        del self._data['guests'][name]
        self.save_file()

    def load_initial_file(self):
        try:
            with open(fileName, "r") as data:
                return ast.literal_eval(data.read())
        except FileNotFoundError:
            return {
                'pinned_message_id': '',
                'pinned_message_user': '',
                'pinned_event': False,
                'chat_id': os.environ['DACHKULTUR_CHAT_ID'],
                'maxTickets': 0,
                'event_text': '',
                'limited': False,
                'guests': {}
            }

    def save_file(self):
        with open(fileName, 'w') as f:
            print(self._data, file=f)
