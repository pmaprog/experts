from schema import Schema, And, Optional

registration = Schema({
    'name': str,
    'surname': str,
    'password': str,
    'email': str
})

user_update = Schema(And(
    lambda x: x != {},
    {
        Optional('name'): str,
        Optional('surname'): str,
        Optional('email'): str,
        Optional('position'): str,
        Optional('tags'): [str],
        Optional('interests'): [str]
    }
))

question = Schema({
    'title': And(str, lambda s: 20 < len(s) <= 128),
    'body': And(str, lambda s: 0 < len(s) <= 1024),
    'only_experts_answer': bool,
    'only_chosen_tags': bool,
    'closed': bool,
    'tags': [str]
})

article = Schema({
    'title': And(str, lambda s: 20 < len(s) <= 128),
    'body': And(str, lambda s: 0 < len(s) <= 1024),
    'tags': [str]
})

# comment = Schema({
#     'text': And(str, lambda s: 20 < len(s) <= 250),
# })
