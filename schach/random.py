import uos

def rand():
    return int.from_bytes(uos.urandom(4), 'little')


def randint(a, b):
    return (rand() % (b - a)) + a


def choice(a):
    return a[rand() % len(a)]

def sample(a, n):
    ret = []
    for i in range(n):
        randEl = choice(a)
        ret.append(randEl)
        a.remove(randEl)
    return ret