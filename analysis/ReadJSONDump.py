__author__ = 'Sushant'
import json
import types
import sys


class ReadJSONDump(object):
    def __init__(self, input_file, load_ids_only=False):
        self.dict = {}
        self.ids = []
        self.load_json(input_file, load_ids_only)
        print repr(len(self.ids)) + " objects read!"

    def print_json(self, inp):
        if type(inp) is types.DictionaryType:
            for x in inp:
                sys.stdout.write(repr(x))
                sys.stdout.write(" : ")
                if type(inp[x]) is types.DictionaryType or type(inp[x]) is types.ListType:
                    self.print_json(inp[x])
                else:
                    sys.stdout.write(repr(inp[x]))
                print ""
        elif type(inp) is types.ListType:
            for x in inp:
                self.print_json(x)
        else:
            sys.stdout.write(repr(inp))
        print ""

    def load_json(self, input_file, load_ids_only=False):
        with open(input_file, "rb") as in_file:
            while True:
                ret = self.sequential_read_line(in_file)
                if len(self.ids) % 1000 == 0:
                    print repr(len(self.ids)) + " read!"
                if ret is None:
                    break
                decoded = json.loads(ret)

                if load_ids_only:
                    self.ids.append(decoded['_id']['$oid'])
                else:
                    self.ids.append(decoded['_id']['$oid'])
                    self.dict[decoded['_id']['$oid']] = decoded


    def sequential_read_line(self, in_file):
        buf = None
        while True:
            r = in_file.read(1)
            if not r:
                break
            elif not buf:
                buf = ""
            buf = buf + r
            if r == "\n":
                break
        return buf
