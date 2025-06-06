import re

from factscore.api_requests import APICompletions

INSTRUCT_PROMPT = """Task: Given the following sentence, name main entities mentioned in the sentence. If the sentence is inadequate or doesn't contain any information, answer "No entities to extract".

Example 1:
Input Sentence: "During World War II, Turing worked for the Government Code and Cypher School at Bletchley Park, Britain's codebreaking centre that produced Ultra intelligence."
Output:
- Turing
- Government Code and Cypher School
- Bletchley Park

Example 2:
Input Sentence: "Michael Collins was born on October 31, 1930"
Output:
- Michael Collins

Example 3:
Input Sentence: "Photosynthesis is essential for plant growth and development."
Output:
- Photosynthesis
- Plant

Example 4:
Input Sentence: "Hermann Einstein and Pauline Koch were middle-class."
Output:
- Hermann Einstein
- Pauline Koch

"""


class EntitiesRetriever:
    demos = INSTRUCT_PROMPT

    def __init__(self, llm: APICompletions):
        self.llm = llm

    def run(self, sentences):
        assert isinstance(sentences, list), "generation must be a list"

        return self.get_entities(sentences)

    async def get_entities(self, sentences):
        prompts = []
        for sentence in sentences:
            prompt = (
                self.demos
                + f"""Now process the following sentence:\nInput sentence: "{sentence}"\nOutput\n:"""
            )
            prompts.append(prompt)

        responses = await self.llm.generate(prompts)

        sent_to_entities = {}  # dict {sentence: entities from the sentence}
        if responses is not None:
            for i, output in enumerate(responses):
                sent_to_entities[sentences[i]] = await self.text_to_entities(output)
            return sent_to_entities

    async def text_to_entities(self, text):
        facts = text.split("- ")[1:]
        facts = [
            fact.strip()[:-1]
            if len(fact) > 0 and fact.strip()[-1] == "\n"
            else fact.strip()
            for fact in facts
        ]
        facts = [re.sub(r"\n\n.*", "", fact, flags=re.DOTALL).strip() for fact in facts]
        if len(facts) > 0:
            if facts[-1][-1] != ".":
                facts[-1] = facts[-1]
        return facts
