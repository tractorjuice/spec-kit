from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class WardleyComponent:
    """Represents a single component on a Wardley map."""

    name: str
    visibility: float
    evolution: float
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert component to a serialisable dictionary."""
        return {
            "name": self.name,
            "visibility": self.visibility,
            "evolution": self.evolution,
            "dependencies": list(self.dependencies),
        }


@dataclass
class WardleyMap:
    """Container for Wardley map components and metadata."""

    components: List[WardleyComponent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_component(self, component: WardleyComponent) -> None:
        """Add a component to the map."""
        self.components.append(component)

    def link_components(self, source: str, target: str) -> None:
        """Create a dependency link from *source* to *target* component."""
        src = self.get_component(source)
        tgt = self.get_component(target)
        if src is None or tgt is None:
            raise ValueError("Both source and target components must exist")
        if target not in src.dependencies:
            src.dependencies.append(target)

    def get_component(self, name: str) -> Optional[WardleyComponent]:
        for comp in self.components:
            if comp.name == name:
                return comp
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert map into dictionary form."""
        return {
            "components": [c.to_dict() for c in self.components],
            "metadata": dict(self.metadata),
        }


# YAML serialisation helpers -------------------------------------------------

def load_map(path: Path) -> WardleyMap:
    """Load a Wardley map from *path*.

    Parameters
    ----------
    path:
        File path to read from.
    """
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    components = [
        WardleyComponent(
            name=c["name"],
            visibility=c.get("visibility", 0.0),
            evolution=c.get("evolution", 0.0),
            dependencies=c.get("dependencies", []),
        )
        for c in data.get("components", [])
    ]

    metadata = data.get("metadata", {})
    return WardleyMap(components=components, metadata=metadata)

def save_map(map_obj: WardleyMap, path: Path) -> None:
    """Serialise *map_obj* to YAML at *path*."""
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(map_obj.to_dict(), fh, sort_keys=False)


# Convenience helpers -------------------------------------------------------

def add_component(map_obj: WardleyMap, component: WardleyComponent) -> None:
    """Add *component* to *map_obj*.

    This is a thin wrapper around :meth:`WardleyMap.add_component`.
    """
    map_obj.add_component(component)


def link_components(map_obj: WardleyMap, source: str, target: str) -> None:
    """Link two components by name."""
    map_obj.link_components(source, target)


def to_dict(map_obj: WardleyMap) -> Dict[str, Any]:
    """Return a serialisable dictionary for *map_obj*."""
    return map_obj.to_dict()

