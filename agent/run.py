import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_ROOT = PROJECT_ROOT / "agent"

if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

load_dotenv(AGENT_ROOT / ".env")

from agents import Runner
from orchestrator.agent import orchestrator


async def main() -> None:
    task = """
We are developing the Family Beacon backend.

The next feature to implement is:

DEVICES

Requirements:

- A device belongs to a child.
- A child belongs to a family.
- Parents can manage devices belonging to children in their family.
- Access must respect the existing Supabase authentication and RLS architecture.
- Do not break the existing families and children functionality.
- Do not use SQLite.
- Follow the existing project architecture.

For this run, do NOT modify any files.

Analyze the current project and produce:

1. GOAL
2. BUILDER TASKS
3. REVIEWER TASKS
4. TEST TASKS
5. EXPECTED RESULT

The Orchestrator must not claim that implementation or tests are complete.
"""


async def main() -> None:
    result = await Runner.run(orchestrator, task)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
