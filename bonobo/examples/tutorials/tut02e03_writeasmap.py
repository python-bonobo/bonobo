import json

import bonobo


def split_one_to_map(line):
    k, v = line.split(', ', 1)
    return {k: v}


class MyJsonWriter(bonobo.JsonWriter):
    prefix, suffix = '{', '}'

    def write(self, fs, file, lineno, **row):
        return bonobo.FileWriter.write(
            self, fs, file, lineno,
            json.dumps(row)[1:-1]
        )


graph = bonobo.Graph(
    bonobo.FileReader('coffeeshops.txt'),
    split_one_to_map,
    MyJsonWriter('coffeeshops.json', fs='fs.output'),
)


def get_services():
    return {
        'fs': bonobo.open_examples_fs('datasets'),
        'fs.output': bonobo.open_fs(),
    }


if __name__ == '__main__':
    bonobo.run(graph, services=get_services())
