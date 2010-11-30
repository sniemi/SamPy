class FileLoader(object):
    def __init__(self, fname, coltypes = {}, separator = None):
        self.types = coltypes
        if type(fname) == str:
            ofile = open(fname)
        else:
            ofile = fname
        self.rows = [x.split(separator) for x in ofile]

    def __getitem__(self, *args):
        index = args[0]
        if type(index) != int:
            raise TypeError("The index must be an integer, but I got '%s'" % index)
        row = tuple(self.types.get(colno, str)(colval)
                      for (colno, colval)
                      in enumerate(self.rows[index]))

        return row

    def __iter__(self):
        class IterObject(object):
            def __init__(self, fl):
                self.iterable = fl
                self.pointer = 0
            def next(self):
                try:
                    val = self.iterable[self.pointer]
                    self.pointer += 1
                    return val
                except IndexError:
                    raise StopIteration
        return IterObject(self)

class WheelLoader(object):
    def __init__(self, fname):
        if type(fname) == str:
            ofile = open(fname)
        else:
            ofile = fname
        self.rows = [self.splitRow(x) for x in ofile]

    def splitRow(self, string):
        elements = []
        partial = string.lstrip()
        while partial:
            if partial[0] == "'":
                elem, partial = self.__processString(partial)
            else:
                elem, partial = [x.lstrip() for x in self.__processNonString(partial)]
            elements.append(elem)

        return elements

    def __processNonString(self, string):
        splitted = string.split(' ', 1)
        if len(splitted) < 2:
            rest = ""
        else:
            rest = splitted[1].lstrip()
        
        return splitted[0].strip(), rest

    def __processString(self, string):
        retval = ""

        done = False
        partial = string[1:]
        while not done:
            end = partial.find("'")
            if end == -1:
                raise ValueError("Missing end quote in [%s]" % string)

            retval += partial[:end]
            partial = partial[end+1:]

            if partial.startswith("'"):
                retval += "'"
                partial = partial[end+1:]
            if not partial.startswith(" "):
                retval += "'"
            else:
                partial = partial.lstrip()
                done = True

        return retval, partial

    def __getitem__(self, *args):
        index = args[0]
        if type(index) != int:
            raise TypeError("The index must be an integer, but I got '%s'" % index)
        return tuple(self.rows[index])

    def __iter__(self):
        class IterObject(object):
            def __init__(self, fl):
                self.iterable = fl
                self.pointer = 0
            def next(self):
                try:
                    val = self.iterable[self.pointer]
                    self.pointer += 1
                    return val
                except IndexError:
                    raise StopIteration
        return IterObject(self)

example_file = """0  1050.0   1013.92
1  1050.0   1025.65
2  1138.3   1010.90
3  1118.9   1050.0
4  1119.0    995.0
5  1050.0   1006.98
6  1050.0   1015.05
7  1050.0   1011.7
9  1021.0    880.0
10 1182.0    997.0
11 1116.0    999.9
12 1132.0    996.8
13 1220.0    992.0
14  750.0   1003.7
15 1107.0    902.1
16  999.9    999.8
17 1050.0   1015.0
33 1212.    1212.4
34 1086.    1080.
37 1152.    1370.
40  687.    1011.
55 1063.05   936.63
66 1181.69  1266.05
77 1175.0   1047.0
88  1103.9   1025.0
"""

example_wheel_file = """0  'Open'            0
1  'Hal_rs45 696_5'  58
2  'u'_Slo 350_65'   82
3  'u'_Slo 353_55'   109
4  'Halp 656_3'      21
5  'Cont 662_4'      77
6  '[SII] 672_5'     123
"""

if __name__ == '__main__':
    from StringIO import StringIO

    print "Sample: 6th row with no converters"
    print FileLoader(StringIO(example_file))[5]
    print
    print "Sample: 6th row with converters = {0: int, 1:float}"
    print FileLoader(StringIO(example_file),
                       coltypes = {0: int, 1:float})[5]
    print

    print "Sample: Iterate over the whole file; converters = {0: int, 1:float, 2:float}"
    fl = FileLoader(StringIO(example_file),
                    coltypes = {0: int, 1:float, 2:float})

    for tpl in fl:
        print tpl

    print "Sample: Iterate over a wheel file"
    fl = WheelLoader(StringIO(example_wheel_file))

    for tpl in fl:
        print tpl
