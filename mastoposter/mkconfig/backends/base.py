from abc import ABC, abstractmethod
from configparser import ConfigParser


class BaseBackend(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def pre_run(self):
        raise NotImplementedError

    @abstractmethod
    def configure(self):
        raise NotImplementedError

    @abstractmethod
    def generate_config(self) -> ConfigParser:
        raise NotImplementedError
