from abc import ABC, abstractmethod
from typing import List, Optional, Iterator
from datetime import datetime
from uuid import uuid4


# Component interface for Composite Pattern
class TraceComponent(ABC):
    @abstractmethod
    def display(self, depth: int = 0) -> str:
        """Display the trace information with indentation"""
        pass

    @abstractmethod
    def add(self, component: "TraceComponent") -> None:
        """Add a child component to this component"""
        pass

    @abstractmethod
    def remove(self, component: "TraceComponent") -> None:
        """Remove a child component from this component"""
        pass


# Leaf component for Composite Pattern
class TraceEvent(TraceComponent):
    def __init__(self, name: str, timestamp: Optional[datetime] = None):
        self.name = name
        self.timestamp = timestamp or datetime.now()
        self.id = str(uuid4())

    def display(self, depth: int = 0) -> str:
        indent = "  " * depth
        return f"{indent}- {self.name}: {self.timestamp.isoformat()}"

    def add(self, component: "TraceComponent") -> None:
        raise NotImplementedError("Cannot add to a leaf node")

    def remove(self, component: "TraceComponent") -> None:
        raise NotImplementedError("Cannot remove from a leaf node")


# Composite component for Composite Pattern
class TraceGroup(TraceComponent):
    def __init__(self, name: str):
        self.name = name
        self.children: List[TraceComponent] = []
        self.timestamp = datetime.now()
        self.id = str(uuid4())

    def display(self, depth: int = 0) -> str:
        indent = "  " * depth
        result = [f"{indent}+ {self.name}: {self.timestamp.isoformat()}"]

        for child in self.children:
            result.append(child.display(depth + 1))

        return "\n".join(result)

    def add(self, component: TraceComponent) -> None:
        self.children.append(component)

    def remove(self, component: TraceComponent) -> None:
        self.children.remove(component)

    # Iterator Pattern - allows traversing through all children
    def __iter__(self) -> Iterator[TraceComponent]:
        return iter(self.children)


# Trace context manager - Memento Pattern to capture state
class TraceContext:
    _instance = None  # Singleton Pattern

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TraceContext, cls).__new__(cls)
            cls._instance.root = TraceGroup("Request Trace Root")
            cls._instance.current_group = cls._instance.root
        return cls._instance

    def start_group(self, name: str) -> TraceGroup:
        """Start a new trace group and make it the current group"""
        group = TraceGroup(name)
        self.current_group.add(group)
        self.current_group = group
        return group

    def end_group(self) -> None:
        """End the current trace group and return to parent group"""
        # Find parent group that contains current group
        self._find_parent_group(self.root, self.current_group)

    def _find_parent_group(self, node: TraceComponent, target: TraceComponent) -> bool:
        """Helper to find parent of a group"""
        if isinstance(node, TraceGroup):
            for child in node.children:
                if child == target:
                    self.current_group = node
                    return True
                if isinstance(child, TraceGroup) and self._find_parent_group(
                    child, target
                ):
                    return True
        return False

    def add_event(self, name: str) -> TraceEvent:
        """Add an event to the current trace group"""
        event = TraceEvent(name)
        self.current_group.add(event)
        return event

    def get_trace(self) -> str:
        """Get the full trace as a string"""
        return self.root.display()

    def reset(self) -> None:
        """Reset the trace context"""
        self.root = TraceGroup("Request Trace Root")
        self.current_group = self.root


# Utility functions
def trace_request(name: str) -> None:
    """Add a trace event for a request"""
    context = TraceContext()
    context.add_event(f"Request: {name}")


def start_trace_group(name: str) -> None:
    """Start a new trace group"""
    context = TraceContext()
    context.start_group(name)


def end_trace_group() -> None:
    """End the current trace group"""
    context = TraceContext()
    context.end_group()


def get_trace() -> str:
    """Get the full trace"""
    context = TraceContext()
    return context.get_trace()


def reset_trace() -> None:
    """Reset the trace context"""
    context = TraceContext()
    context.reset()
