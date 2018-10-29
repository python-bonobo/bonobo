"""
Compare passing a dict to passing a dict as kwargs to a stupid transformation

Last results (1 mill calls):

j1 1.5026444319955772
k1 1.8377482700016117
j2 1.1962292949901894
k2 1.5545833489886718
j3 1.0014333260041894
k3 1.353256585993222

"""
import json
import timeit


def j1(d):
    return {"prepend": "foo", **d, "append": "bar"}


def k1(**d):
    return {"prepend": "foo", **d, "append": "bar"}


def j2(d):
    return {**d}


def k2(**d):
    return {**d}


def j3(d):
    return None


def k3(**d):
    return None


if __name__ == "__main__":
    import timeit

    with open("person.json") as f:
        json_data = json.load(f)

    for i in 1, 2, 3:
        print(
            "j{}".format(i), timeit.timeit("j{}({!r})".format(i, json_data), setup="from __main__ import j{}".format(i))
        )
        print(
            "k{}".format(i),
            timeit.timeit("k{}(**{!r})".format(i, json_data), setup="from __main__ import k{}".format(i)),
        )
