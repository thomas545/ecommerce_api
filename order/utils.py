import random
import string


def random_string_generator(size=20, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))

