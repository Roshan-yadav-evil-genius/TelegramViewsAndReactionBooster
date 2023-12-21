
from dataclasses import dataclass, field

class TokenException(Exception):
    def __init__(self, message="TokenException Ocuured"):
        self.message = message
        super().__init__(self.message)


@dataclass(order=True)
class Target:
    Achieved: bool = field(default=False)
    Attempt: int = field(default=0)
    maxRetry: int = field(default=5)


@dataclass(order=True)
class Post:
    url: str
    status: bool = field(default=False)
    views: int = field(default=None)
    requiredViews: int = field(default=None)
