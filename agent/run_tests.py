"""
Script to run the Test Agent for module verification.
Tests current project modules and components.
"""
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from agents import Runner
from tests.agent import test_agent


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / "agent" / ".env"

load_dotenv(ENV_FILE)


async def main() -> None:
    """Run Test Agent to verify current project modules."""
    task = """
Analyze and test the current Family Beacon project modules.

Current project structure:
- Backend: Python/FastAPI with Supabase integration
  - Main modules: auth.py, children.py, families.py, profiles.py, config.py, supabase_client.py
  - Main file: app/main.py (FastAPI application)
  
- Frontend: React/TypeScript with Vite
  - Main components: App.tsx, components (BrandLogo, ChildLockScreen, DevicesTab, etc.)
  - Main entry: src/main.tsx
  
- Database: Supabase with migrations
  - Initial migration: 001_initial.sql
  - Health check: 002_health_check.sql

Tasks:
1. Create comprehensive test cases for backend modules (auth, children, families, profiles)
2. Create test cases for frontend components
3. Verify integration between backend and frontend
4. Create tests for database migrations
5. Identify potential issues and edge cases
6. Provide testing recommendations

Do not modify any files. Only analyze and provide test plan.

Output format must include:
- TEST SUMMARY: Overview of tests created and executed
- TEST COVERAGE: Coverage areas and test cases
- TEST RESULTS: Results of test execution
- FAILURE ANALYSIS: Any test failures and their causes
- RECOMMENDATIONS: Suggestions for additional tests or improvements
- APPROVAL STATUS: Whether all tests pass and requirements are met
"""

    result = await Runner.run(test_agent, task)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
