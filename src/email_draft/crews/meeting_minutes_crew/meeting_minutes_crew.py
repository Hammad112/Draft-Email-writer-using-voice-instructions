from crewai import Agent, Crew, Process, Task ,LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from crewai_tools import FileWriterTool

file_writer_tool_summary = FileWriterTool(filename="summary.txt",directory="meeting_minutes")
file_writer_tool_action_items = FileWriterTool(filename='action_items.txt',directory="meeting_minutes/action_items")
file_writer_tool_sentiment = FileWriterTool(filename='sentiment.txt',directory="meeting_minutes/sentiment")

llm = LLM(
    model="groq/llama-3.1-70b-versatile",
    api_key="",
    provider="groq"
)

@CrewBase
class MeetingMinutesCrew:
    """Poem Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def meeting_minutes_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_minutes_summarizer"],  # type: ignore[index]
            tools=[file_writer_tool_summary,file_writer_tool_action_items,file_writer_tool_sentiment],
            llm=llm
        )
    
    @agent
    def meeting_minutes_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_minutes_writer"],  # type: ignore[index]
            llm=llm
            )

    @task
    def meeting_minutes_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_summary_task"],  # type: ignore[index]
        )
    
    @task
    def meeting_minutes_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_writing_task"],  # type: ignore[index]
        )






    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""


        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
