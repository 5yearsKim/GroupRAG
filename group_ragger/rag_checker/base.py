from abc import ABC, abstractmethod
import re
import json
from ..schema import RetrievalInput, Message

class BaseRagChecker(ABC):
    @abstractmethod
    def check_rag(self, messages: list[Message]) -> RetrievalInput:
        pass


    def parse_response(self, response: str) -> RetrievalInput:

        # Regular expression to match 'should_retrieve' not enclosed in double quotes
        # and replace it with "should_retrieve"
        json_keys = ['should_retrieve', 'query']
        fixed_str = response
        for jkey in json_keys:
            # Dynamically create the regex pattern using the current jkey
            pattern = r'(?<!")(\b{}\b)(?!")'.format(jkey)
            fixed_str = re.sub(pattern, r'"\1"', fixed_str)


        try:
            # parse json
            parsed = json.loads(fixed_str)
            return RetrievalInput(
                should_retrieve=parsed['should_retrieve'],
                query=parsed.get('query', '')
            )
        except Exception as e:
            print(response, ' : ', e)
            return RetrievalInput(should_retrieve=False)