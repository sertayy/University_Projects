def empty_node() -> dict:
    return {"chld": {}, "word_ends": False}


class Trie:  # the trie structure

    def __init__(self):
        self.root = empty_node()  # an empty root for initialization

    def insert_token(self, token: str):  # inserts token to the trie char by char
        current_node = self.root
        for char in token:
            if char not in current_node["chld"]:
                current_node["chld"][char] = empty_node()
            current_node = current_node["chld"][char]
        current_node["word_ends"] = True

    def search(self, input_token: str) -> (bool, bool):  # searchs for both prefix* and word char by char
        current_node = self.root
        is_prefix: bool = False  # checks if it is a prefix search
        if input_token[-1] == "*":
            input_token = input_token[:-1]
            is_prefix = True

        for char in input_token:
            if char not in current_node["chld"]:
                return False, is_prefix
            current_node = current_node["chld"][char]

        if is_prefix:
            return True, is_prefix
        return current_node["word_ends"], is_prefix
