# wise/fact_checker.py

import json
from wise.utils import get_chat_completion

class FactChecker:
    def __init__(self, aoai_client, product_facts, model='gpt-4o'):
        self.client = aoai_client
        self.product_details = product_facts
        self.model = model
        self.system_prompt = f"""You are a call transcript analyzer.
You have been provided with a transcript of a call between a Wealth Advisor and a potential client.
Your task is to review the transcript and identify any factual inaccuracies or misleading information.

### Step by step instructions:
1. Read the transcript carefully, only focus on the last turn of the Advisor.
2. Identify if there's any facts shared by the advisor in the last turn of the transcript
3. If you don't find any facts, stop the review
4. If you find any facts, check the facts against the provided fact reference
5. Use the previous questions to understand the context of the conversation, ensure you are checking the information relative to the right product
6. Return a list of facts shared, whether they are accurate or not and citations to support it. If the fact shared does not exist in the fact reference, mark it as "unknown" and provide a citation as "not found in the reference".
 
### Output
You must use a structured JSON format to provide the facts, their accuracy, and citations.
{{"facts": [{{"fact": "fact1", "accuracy": "accurate/inaccurate/unknown", "citation": "source"}}, {{"fact": "fact2", "accuracy": "accurate/inaccurate", "citation": "source"}}]}}

### Fact reference
{self.product_details}

"""

    def _check_facts(self, conversation_script):
        checked_facts = []
        transcript = conversation_script
        for turn in transcript:
            if turn['speaker'] == 'Advisor':
                current_index = transcript.index(turn)
                conversation_upto_now = transcript[:current_index + 1]
                user_prompt = f""""
                #### Transcript
                {conversation_upto_now}
                """
                messages  = [{"role": "system", "content": self.system_prompt},
                             {"role": "user", "content": user_prompt}]
                
                try:
                    response = get_chat_completion(self.client, 
                                                   messages, 
                                                   model=self.model, 
                                                   response_format={"type":"json_object"})
                    checked_facts.append(json.loads(response))
                except Exception as e:
                    print(f'execution failed: {e}')
        return checked_facts
    
    def _fact_accuracy_report(self, checked_facts):
        # Initialize counters
        total_non_empty_facts = 0
        accurate_facts_count = 0
        total_facts=[]

        # Iterate through the checked_facts list
        inaccurate_facts_count = 0
        unverifiable_facts_count = 0

        for item in checked_facts:
            facts_list = item['facts']
            if facts_list:
                total_non_empty_facts += len(facts_list)
                accurate_facts_count += sum(1 for fact in facts_list if fact['accuracy'] == 'accurate')
                inaccurate_facts_count += sum(1 for fact in facts_list if fact['accuracy'] == 'inaccurate')
                unverifiable_facts_count += sum(1 for fact in facts_list if fact['accuracy'] == 'unknown')
            for fact in facts_list:
                total_facts.append(fact)

        return {
            'total_facts_shared': total_non_empty_facts,
            'accurate_facts_count': accurate_facts_count,
            'inaccurate_facts_count': inaccurate_facts_count,
            'unverifiable_facts_count': unverifiable_facts_count,
            'fact_details': total_facts
        }

    def check_transcript(self, transcript):
        checked_facts = self._check_facts(transcript)
        return self._fact_accuracy_report(checked_facts)