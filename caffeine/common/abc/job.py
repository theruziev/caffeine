from abc import ABC, abstractmethod


class BaseJob(ABC):
    @abstractmethod
    async def listen(self, *args, **kwargs):
        pass
