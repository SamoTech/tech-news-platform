class HumanMemory:
    def __init__(self):
        self.used = set()

    def pick_unique(self, templates):
        for sentence in templates:
            if sentence not in self.used:
                self.used.add(sentence)
                return sentence

        choice = templates[0]
        self.used.add(choice)
        return choice
