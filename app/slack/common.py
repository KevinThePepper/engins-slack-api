"""
Common classes and methods for actions, commands, and events.
"""

class IAction:
    name: str
    description: str

    def __str__(self) -> str:
        return self.name
