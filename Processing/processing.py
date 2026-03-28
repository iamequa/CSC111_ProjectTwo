from assignments.CSC111_ProjectTwo.Data.vertex import Recipe


class SearchProcessor:
    """This class processes what the user inputs and sends it to correct computation.
        Instance Attributes:
        - all_text_inputted: list[str]
        - limit: int

    """
    all_text_inputted: list[str]
    limit: int

    def __init__(self, limit: int):
        self.all_text_inputted = []
        self.limit = limit

    def process_final_answer(self, text_inputted: str):
        """Updates final answer """
        if len(self.all_text_inputted) < self.limit:
            print('if reached')
            self.all_text_inputted.append(text_inputted)
            if len(self.all_text_inputted) == self.limit:
                return 'Limit Reached'
        return None

    def send_to_computation(self, inputs: list[list[str]]) -> list[Recipe]:
        """Send to the correct computation
            Preconditions:
                - len(inputs) == 4
        """

class SurveyProcessor:
    """This class processes what the user inputs and sends it to correct computation.
        Instance Attributes:
        - all_text_inputted: list[str]
        - limit: int

    """
    all_text_inputted: list[str]
    limit: int

    def __init__(self, limit: int):
        self.all_text_inputted = []
        self.limit = limit

    def process_final_answer(self, text_inputted: str):
        """Updates final answer """
        if len(self.all_text_inputted) < self.limit:
            print('if reached')
            self.all_text_inputted.append(text_inputted)
            if len(self.all_text_inputted) == self.limit:
                return 'Limit Reached'
        return None

    def send_to_computation(self, inputs: list[str]) -> list[Recipe]:
        """Send to the correct computation
            Preconditions:
                - len(inputs) == 4

        """


def to_list(s: str) -> list[str]:
    return [item.strip() for item in s.split(",") if item.strip()]

