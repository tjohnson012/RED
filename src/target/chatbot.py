"""
Target LLM Application - A Gemini-powered customer service chatbot.
This is the "victim" that RED will attack.
"""

import os
from google import genai
from google.genai import types
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm, workflow, task

from .system_prompt import SYSTEM_PROMPT, FAKE_CUSTOMER_DATA


class TargetChatbot:
    """
    A vulnerable chatbot that RED will attempt to compromise.
    Instrumented with Datadog LLM Observability.
    """

    def __init__(self):
        # Initialize Gemini client for Vertex AI
        self.client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )
        self.model = "gemini-2.0-flash-001"
        self.conversation_history = []

    @workflow(name="customer_service_chat")
    def chat(self, user_message: str, session_id: str = "default") -> dict:
        """
        Process a user message and return a response.
        Fully instrumented for LLM Observability.
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        # Build the full prompt with system instructions
        response = self._generate_response(user_message, session_id)

        # Add assistant response to history
        self.conversation_history.append({
            "role": "model",
            "parts": [{"text": response}]
        })

        return {
            "response": response,
            "session_id": session_id,
            "message_count": len(self.conversation_history)
        }

    @llm(model_name="gemini-2.0-flash-001", model_provider="google", name="generate_response")
    def _generate_response(self, user_message: str, session_id: str) -> str:
        """
        Generate a response using Gemini.
        The @llm decorator automatically traces this call.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self.conversation_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=1024,
                    # Intentionally weak safety settings for demonstration
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_ONLY_HIGH"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_ONLY_HIGH"
                        ),
                    ]
                )
            )

            # Annotate the span with additional context
            LLMObs.annotate(
                span=None,  # Current span
                input_data=user_message,
                output_data=response.text,
                metadata={
                    "session_id": session_id,
                    "model": self.model,
                    "conversation_length": len(self.conversation_history)
                },
                tags={
                    "application": "target-chatbot",
                    "environment": os.getenv("DD_ENV", "development")
                }
            )

            return response.text

        except Exception as e:
            LLMObs.annotate(
                span=None,
                metadata={"error": str(e)},
                tags={"error": "true"}
            )
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"

    @task(name="lookup_customer")
    def lookup_customer(self, query: str) -> dict:
        """
        Simulated customer lookup that could leak PII.
        This is intentionally vulnerable for demonstration.
        """
        # This is a vulnerability - in a real app, this should be protected
        for customer in FAKE_CUSTOMER_DATA["customers"]:
            if query.lower() in customer["name"].lower() or query.lower() in customer["email"].lower():
                return customer
        return {"error": "Customer not found"}

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
