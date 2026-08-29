"""
Agents module for Family Beacon project.
Provides Agent and Runner classes for orchestrating AI-powered development tasks.
"""

import json
from typing import Any, Optional
from dataclasses import dataclass

import anthropic


@dataclass
class AgentResult:
    """Result from running an agent."""
    final_output: str
    messages: list[dict[str, Any]] | None = None


class Agent:
    """
    An AI agent that can process instructions and tasks.
    Wraps Claude API for executing development tasks.
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        """
        Initialize an agent.
        
        Args:
            name: Name of the agent
            instructions: System instructions for the agent
            model: Model to use (default: Claude 3.5 Sonnet)
        """
        self.name = name
        self.instructions = instructions
        self.model = model
        self.client = anthropic.Anthropic()
    
    async def process(self, task: str) -> AgentResult:
        """
        Process a task with the agent.
        
        Args:
            task: The task to process
            
        Returns:
            AgentResult containing the agent's output
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.instructions,
            messages=[
                {
                    "role": "user",
                    "content": task,
                }
            ],
        )
        
        response_text = message.content[0].text if message.content else ""
        
        return AgentResult(
            final_output=response_text,
            messages=[{"role": "assistant", "content": response_text}],
        )


class Runner:
    """
    Runner orchestrates execution of agents for development tasks.
    """
    
    @staticmethod
    async def run(agent: Agent, task: str) -> AgentResult:
        """
        Run an agent with a given task.
        
        Args:
            agent: The agent to run
            task: The task to execute
            
        Returns:
            AgentResult from the agent's execution
        """
        return await agent.process(task)
