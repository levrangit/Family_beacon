"""
Agents module for Family Beacon project.
Provides Agent and Runner classes for orchestrating AI-powered development tasks.
"""

import logging
from typing import Any, Optional
from dataclasses import dataclass

import anthropic
from anthropic import APIError, APIConnectionError, RateLimitError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            
        Raises:
            APIConnectionError: If unable to connect to Anthropic API
            RateLimitError: If rate limit exceeded
            APIError: For other API errors
        """
        try:
            logger.info(f"Agent '{self.name}' processing task")
            
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
            logger.info(f"Agent '{self.name}' completed successfully")
            
            return AgentResult(
                final_output=response_text,
                messages=[{"role": "assistant", "content": response_text}],
            )
            
        except APIConnectionError as e:
            logger.exception(f"Connection error for agent '{self.name}'")
            raise
        except RateLimitError as e:
            logger.exception(f"Rate limit exceeded for agent '{self.name}'")
            raise
        except APIError as e:
            logger.exception(f"API error for agent '{self.name}'")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in agent '{self.name}'")
            raise


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
            
        Raises:
            APIConnectionError: If unable to connect to API
            RateLimitError: If rate limit exceeded
            APIError: For other API errors
        """
        try:
            logger.info(f"Runner: Starting execution with agent '{agent.name}'")
            result = await agent.process(task)
            logger.info(f"Runner: Execution completed with agent '{agent.name}'")
            return result
        except (APIConnectionError, RateLimitError, APIError) as e:
            logger.exception(f"Runner: Failed to execute with agent '{agent.name}'")
            raise
