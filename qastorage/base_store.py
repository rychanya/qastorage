import abc

class AbstractStore(abc.ABC):
    @abc.abstractmethod
    def get_or_create_base(self):
        ...