import threading, asyncio, logging

class EventHandler:
    """https://lukaszmieczkowski.com/2021/03/29/handling-celery-events/"""
    def __init__(self, app):
        self._app = app
        self._state = app.events.State()
        self._logger = logging.getLogger("eAsset.clry.events")

    def _event_handler(handler):
        def wrapper(self, event):
            self._state.event(event)
            task = self._state.tasks.get(event.get("uuid",None))
            # log event here
            handler(self, event)
        return wrapper

    @_event_handler
    def _broadcast(self, event):
        print(event["message"])

    @_event_handler
    def _private_message(self, event):
        print(event["message"])

    def emit(self, key, message):
        with self._app.events.default_dispatcher() as dispatcher:
            dispatcher.send(key, message=message)
            dispatcher.close()

    def reciever(self):
        with self._app.connection() as connection:
            recv = self._app.events.Receiver(connection, handlers={
                'broadcast': self._broadcast,
                'private-message': self._private_message,
            })
            recv.capture(limit=None, timeout=None, wakeup=True)

    def start_listener(self):
        """
            capture celery events in the background
        """
        thread = threading.Thread(target=self.reciever, daemon=True)
        thread.start()