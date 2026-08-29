import asyncio
from pathlib import Path

from dotenv import load_dotenv

from agents import Runner

from orchestrator.agent import orchestrator


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / "agent" / ".env"

load_dotenv(ENV_FILE)


async def main() -> None:
    task = """
Analyze the current Family Beacon project.

We want to implement the next backend feature:
Devices.

A device belongs to a child.
Parents should be able to manage devices belonging to children
in their family.

Do not modify any files.

Prepare an implementation plan for Builder, Reviewer and Tests.
"""

    result = await Runner.run(orchestrator, task)

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
