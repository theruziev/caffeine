from abc import abstractmethod, ABC
from queue import LifoQueue

from caffeine.common.logger import logger


class BaseBootstrap(ABC):
    shutdown_events: LifoQueue = LifoQueue()

    @abstractmethod
    async def init(self):
        pass

    async def shutdown(self):
        logger.info("Shutting down app..")
        while not self.shutdown_events.empty():
            shutdown = self.shutdown_events.get()
            await shutdown()
