def empty_node() -> dict:
    return {"chld": {}, "word_ends": False}  # chld for children nodes, word_ends for checking the end of the word


class Trie:  # the trie structure

    def __init__(self):
        self.root = empty_node()  # an empty root for initialization

    def insert_token(self, token: str):  # inserts token to the trie char by char
        current_node = self.root  # initialize the current node as root
        for char in token:
            if char not in current_node["chld"]:  # if char not in the children, then create a new child
                current_node["chld"][char] = empty_node()
            current_node = current_node["chld"][char]  # change the current to the next node
        current_node["word_ends"] = True  # each char is added to the trie

    def search(self, input_token: str) -> (bool, bool):  # searchs for both prefix* and word char by char
        current_node = self.root  # initialize the current node as root
        is_prefix: bool = False  # checks if it is a prefix search
        if input_token[-1] == "*":  # if input token ends with *, it is prefix search
            input_token = input_token[:-1]  # removes the * sign
            is_prefix = True  # assign it to True, since it is the input token is prefix*

        for char in input_token:  # for each char in the input token check if the char is in current node's child
            if char not in current_node["chld"]:
                return False, is_prefix  # token is not found!
            current_node = current_node["chld"][char]  # change the current to the next node

        if is_prefix:
            return True, is_prefix  # returns true since each char is in the trie
        return current_node["word_ends"], is_prefix  # founded pattern in trie, but it returns true if it is end of the branch
