import os
import json
from wise.utils import get_chat_completion

class Evaluator:
    def __init__(self, aoai_client, call_theme, evaluation_criteria, model=os.environ.get("AZURE_OPENAI_GPT4O_DEPLOYMENT")):
        self.aoai_client = aoai_client
        self.evaluation_criteria = evaluation_criteria
        self.model = model
        self.theme = call_theme
        self.evaluation_system_prompt = f"""
        You are an AI specialized in analyzing phone calls of type {self.theme}.
        In your prompts, you will receive conversation transcriptions and criteria to evaluate them.
        You will also receive **EVALUATION CRITERIA** to be considered for each item. These criteria are organized by TOPIC and SCORE, with SCORE being what you need to assign if the TOPIC is met.
        You must evaluate the characteristics of the service according to the criteria and business rules.
        In your responses, always include the rationale behind your evaluations.

        # Output Format
        - You must guarantee that the output is a valid JSON object.
        - For the evaluation, your output **must contain all the fields in the structure mentioned bellow**:
          - evaluation [Dictionary that contains the evaluation information]
            - criteria [List of dictionaries that contains a single criteria used information]
              - sub_criteria [List of dictionaries that contains the sub criteria used information]
                - score [Score assigned to the criteria]
                - rationale [Rationale for the score assigned to the sub criteria]
              - score [Score assigned to the criteria]
              - rationale [Rationale for the score assigned to the criteria]
            - classification [Overall classification of the improvement suggestion.]
            - overall_score [Overall score assigned to the transcription.]
            - rationale [Rationale for the overall score assigned to the transcription.]
            - improvement_suggestion [Improvement Suggestion for the evaluated criteria that considers the subcriteria scores.]

        # Example output
        {{
          "evaluation": {{
            "criteria": [{{
              "name": "Agent Efficiency",
              "sub_criteria": [
                {{
                  "name": "Problem Understanding",
                  "score": 2,
                  "rationale": "The agent was able to understand the customer's problem quickly and efficiently."
                }},
                {{
                  "name": "Problem Resolution",
                  "score": 2,
                  "rationale": "The agent was able to solve the customer's problem quickly and efficiently."
                }}
              ],
              "criteria_score": 2,
              "criteria_rationale": "The agent was able to solve the customer's problem quickly and efficiently."
            }},
            {{
              "name": "Agent Communication",
              "sub_criteria": {{
                "name": "speech employed",
                "score": 2,
                "rationale": "The agent was able to properly communicate with the client."
              }},
              "score": 2,
              "rationale": "The agent communicated well under the given scenario."
            }}],
            "call_classification": "Good",
            "overall_score": 2,
            "rationale": "The agent was able to solve the customer's problem quickly and efficiently.",
            "improvement_suggestion": "The agent should be more polite and empathetic with the customer."
            }}
          }}
        """

    def evaluate_transcription(self, transcript):
      user_prompt = f"""Considering the following call transcription:
      {transcript}

      Evaluate the transcription according to the following criteria:
      {self.evaluation_criteria}"""

      messages = [
        {"role": "system",
         "content": self.evaluation_system_prompt},
        {"role": "user",
         "content": user_prompt}
      ]

      try:
        evaluation_response = json.loads(get_chat_completion(self.aoai_client, messages,model=self.model, response_format={"type": "json_object"}))
      except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        evaluation_response = {"error": "Failed to decode JSON response"}
      except Exception as e:
        print(f"An error occurred: {e}")
        evaluation_response = {"error": "An unexpected error occurred"}

      return evaluation_response