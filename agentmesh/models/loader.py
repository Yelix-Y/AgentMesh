import yaml
from pathlib import Path
from agentmesh.models.agent import AgentProfile


def load_profile(path: str | Path) -> AgentProfile:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Agent profile not found: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    return AgentProfile(**data)


def load_profiles_from_dir(directory: str | Path) -> list[AgentProfile]:
    directory = Path(directory)
    profiles = []
    for yaml_file in sorted(directory.glob("*.yaml")):
        profiles.append(load_profile(yaml_file))
    return profiles
