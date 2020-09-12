from telegram.ext import Updater
import logging
import abc


class Bot(abc.ABC):
    def __init__(self, bot_token: str, data_pth: str):
        self._bot_token = bot_token
        self._data_pth = data_pth

        self._updater = Updater(token=self._bot_token, use_context=True)
        self._dispatcher = self._updater.dispatcher

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.append_handlers()

    def run(self):
        self._updater.start_polling()

    @abc.abstractmethod
    def read_data(self, key: str):
        pass

    @abc.abstractmethod
    def append_handlers(self):
        pass
