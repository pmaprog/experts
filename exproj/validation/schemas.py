from schema import Schema, And, Optional

registration = Schema({
    'name': str,
    'surname': str,
    'password': str,
    'email': str,
    'position': str,
})

user_update = Schema(And(
    lambda x: x != {},
    {
        Optional('name'): str,
        Optional('surname'): str,
        Optional('email'): str,
        Optional('position'): str
    }
))

question = Schema({
    'title': And(str, lambda s: 20 < len(s) <= 128),
    'body': And(str, lambda s: 0 < len(s) <= 1024),
    'only_experts_answer': bool,
    'only_chosen_domains': bool,
    'closed': bool,
    'domains': [int]
})

article = Schema({
    'title': And(str, lambda s: 20 < len(s) <= 128),
    'body': And(str, lambda s: 0 < len(s) <= 1024)
})

# comment = Schema({
#     'text': And(str, lambda s: 20 < len(s) <= 250),
# })
