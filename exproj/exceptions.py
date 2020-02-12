class Error(Exception):
    pass


# todo
class QuestionNotFound(Error):
    def __init__(self, id):
        self.id = id


class NotJsonError(Error):
    pass


class NoData(Error):
    pass
