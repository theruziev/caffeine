from abc import abstractmethod, ABC
from queue import LifoQueue


class BaseBootstrap(ABC):
    shutdown_events: LifoQueue = LifoQueue()

    @abstractmethod
    async def init(self) -> None:
        pass

    async def shutdown(self) -> None:
        while not self.shutdown_events.empty():
            shutdown = self.shutdown_events.get()
            await shutdown()
