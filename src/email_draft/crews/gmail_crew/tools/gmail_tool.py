from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from .gmail_utility import authenticate_gmail, create_message, create_draft

from agentops import record_tool

class GmailToolInput(BaseModel):
    """Input schema for Gmail Input."""

    argument: str = Field(..., description="Description of the argument.")

@record_tool("This is used for gmail draft emails.")

class GmailTool(BaseTool):
    name: str = "Gmail Draft Tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        try:
            service = authenticate_gmail()
            sender = "21pwcse2041@uetpeshawar.edu.pk"
            to = "hammadnasir797@gmail.com"
            subject = "Meeting Minutes"
            message_text = argument

            message = create_message(sender, to, subject, message_text)
            draft = create_draft(service, "me", message)

            return f"Email sent successfully! Draft id {draft}"
        except Exception as e:
                return f"Error sending email: {e}"
