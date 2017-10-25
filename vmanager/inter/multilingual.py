# Internationalization module.


class MultiLingual(object):
    def __init__(self, vocab):
        """
        """
        self.vocab_dict = vocab_dict

    def set_language(self, lan):
        self.lan = lan

    def get_text(self, name):
        return self.vocab.get(name).get(self.lan)

