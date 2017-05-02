class Util():
    @staticmethod
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    @staticmethod
    def remove_suffix(text, suffix):
        if text.endswith(suffix):
            return text[:len(text) - len(suffix)]
        return text

    @staticmethod
    def remove_prefix_suffix(text, prefix, suffix):
        return Util.remove_prefix(Util.remove_suffix(text, suffix), prefix)
