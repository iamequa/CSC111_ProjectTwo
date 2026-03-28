class TextBoxProcessor:
    """This class processes what the user inputs and sends it to correct computation.
        Instance Attributes:
        - all_text_inputted: list[str]
        - limit: int

    """
    all_text_inputted: list[str]
    limit: int

    # add recipe tree

    def __init__(self, limit: int):
        self.all_text_inputted = []
        self.limit = limit
        self.recipe_tree = None
        self.recipe_graph = None

    def process_final_answer(self, text_inputted: str):
        """Updates final answer """
        if len(self.all_text_inputted) < self.limit:
            print('if reached')
            self.all_text_inputted.append(text_inputted)
            if len(self.all_text_inputted) == self.limit:
                return 'Limit Reached'
        return None

    def refresh_answers(self):
        self.all_text_inputted = []

    def send_to_computation(self, inputs: list[list[str]]):
        """Send to the correct computation
            Preconditions:
                - len(inputs) == 4
                - len(inputs) is in the order of previous method
            """
        q1, q2, q3, q4 = inputs[0], inputs[1], inputs[2], inputs[3]
        if q4[0].strip() == '':
            ...  # implement recipe graph
        else:

            ...  # implement tree graoh
