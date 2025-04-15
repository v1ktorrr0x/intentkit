"""DappLooker skills for crypto market data and analytics."""

import logging
import os
from typing import TypedDict

from abstracts.skill import SkillStoreABC
from skills.base import SkillConfig, SkillState
from skills.dapplooker.base import DappLookerBaseTool
from skills.dapplooker.dapplooker_token_data import DappLookerTokenData

# Cache skills at the system level, because they are stateless
_cache: dict[str, DappLookerBaseTool] = {}

logger = logging.getLogger(__name__)


class SkillStates(TypedDict):
    dapplooker_token_data: SkillState


class Config(SkillConfig):
    """Configuration for DappLooker skills."""

    states: SkillStates
    api_key: str


async def get_skills(
    config: "Config",
    is_private: bool,
    store: SkillStoreABC,
    **_,
) -> list[DappLookerBaseTool]:
    """Get all DappLooker skills.

    Args:
        config: The configuration for DappLooker skills.
        is_private: Whether to include private skills.
        store: The skill store for persisting data.

    Returns:
        A list of DappLooker skills.
    """
    available_skills = []

    # Include skills based on their state
    for skill_name, state in config["states"].items():
        if state == "disabled":
            continue
        elif state == "public" or (state == "private" and is_private):
            available_skills.append(skill_name)

    # Get each skill using the cached getter
    result = []
    for name in available_skills:
        skill = get_dapplooker_skill(name, store)
        if skill:
            result.append(skill)
    return result


def get_dapplooker_skill(
    name: str,
    store: SkillStoreABC,
) -> DappLookerBaseTool:
    """Get a DappLooker skill by name.

    Args:
        name: The name of the skill to get
        store: The skill store for persisting data

    Returns:
        The requested DappLooker skill
    """
    if name == "dapplooker_token_data":
        if name not in _cache:
            _cache[name] = DappLookerTokenData(
                skill_store=store,
            )
        return _cache[name]
    else:
        logger.warning(f"Unknown DappLooker skill: {name}")
        return None
