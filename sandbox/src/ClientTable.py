"""HTML table parsing.

ClientTable is a Python module for generic HTML table parsing.  It is
most useful when used in conjunction with other parsers (htmllib or
HTMLParser, regular expressions, etc.), to divide up the parsing work
between your own code and ClientTable.

RFC 1866: HTML 2.0
RFC 1942: HTML Tables
HTML 4.01 Specification, W3C Recommendation 24 December 1999

Requires Python 2.2.


Copyright 2002-2003 John J. Lee <jjl@pobox.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the MIT License (see the file COPYING included with
the distribution).
"""

# XXXX
# Need to be able to match headers, rather than requiring exact string match.
#  Maybe indexing should do this?  Should indexing ignore HTML tags?
#  Current plan: match by substring; treat string as re if re_search boolean arg
#   is true; tags are ignored or not as per strip_tags arg of ParseFile.
#   ignore_tags and exact_match args can be added later.
# Accept string or string-*like* args?
# Character entities.
# Implement single_span.
# Implement nr_toplevel_to_parse.

# XXX
# TD elements often indicate a scope -- this could be used to find cells,
#  so there should probably be a method for this.
# Need an interface for getting at HTML attributes in tables
# What to do with illegally overlapping elements (rows and rows, cols and
#  cols, rows and cols)?
# More relaxed parsing?
# Incremental parsing of tables, while HTML is still downloading?
# Deal with character sets and unicode properly.

# Notes
# -----
# How to cope with non-unity span of rows and columns?
#  Cell class has rowspan and colspan attrs., and a data attr, with the
#   text in it.
#  Cells with non-unity span get returned twice (or more) by iterators
#   and by indexing.  Clients need to know when they're getting the same
#   cell, so allow them to assume that identical cell objects will be
#   returned.
# Directionality doesn't matter.

# Perl's HTML::TableExtractor has a very elaborate system for parsing only
# those tables that match particular constraints.  I don't think I care
# enough about this to copy it.  HTML::TableExtractor can (for example):
#  Find table by headers, or depth and index, or both.
#  Depth only returns all tables at that depth.  Index only returns
#   all tables at that index.  Headers only returns all tables anywhere
#   with those headers.  Otherwise, all tables match.
#  Chaining: {"headers": ["Senator", "Sugar?"],
#                         "chain": {"headers": ["blah"]}}

try: True
except NameError:
    True = 1
    False = 0

import HTMLParser, re, copy, string
from htmlentitydefs import entitydefs
from types import StringType, UnicodeType, \
     IntType, LongType, FloatType

VERSION = "0.0.1a"

CHUNK = 1024  # size of chunks fed to parser, in bytes
WHITESPACE_RE = re.compile(r"\s+")
def collapse_whitespace(text): return WHITESPACE_RE.sub(" ", text)

NumericTypes = (IntType, LongType, FloatType)

def issequence(object):
    """Test whether object is a sequence."""
    try:
        object[0]
    except (TypeError, KeyError):
        return 0
    except IndexError:
        pass
    return 1

def isstringlike(object):
    if (isinstance(object, StringType) or isinstance(object, UnicodeType)):
        return True
    return False

def ParseFile(file,
              nr_to_parse=-1,
              nr_toplevel_to_parse=-1,
              single_span=False,
              strip_tags=False,
              collapse_whitespace=False,
              recode_entities=None):
    """Parse HTML tables and return a list of HTMLTable objects.

    file: file object
    nr_to_parse: stop after parsing this many tables; negative means parse all
     of them
    single_span: return cells that span multiple columns or rows only
     once, rather than once for every row / column they span
    strip_tags: remove HTML tags from cell contents
    collapse_whitespace: collapse consecutive whitespace characters (anything
     matching r"\s")to a single space
    recode_entities: recode HTML entities according to this dict

    Note that passing in the return value of urllib2.urlopen here as the file
    argument is fine.

    """
    tp = TableParser(nr_to_parse,
                     nr_toplevel_to_parse,
                     single_span,
                     strip_tags,
                     collapse_whitespace,
                     recode_entities)
    while 1:
        data = file.read(CHUNK)
        try:
            tp.feed(data)
        except ParseFinished:
            break
        if len(data) != CHUNK: break

    for table in tp.tables:
        table.fixup()

    return tp.tables


class HTMLTable:
    """Represents (surprise!) an HTML table.

    At the moment, tables may not be nested.

    HTMLTable instances are iterators over TableRows.  This includes any
    header rows.

    Public attributes: headers_row, headers_col.

    headers_row is a TableRow instance used to index columns in the table.
    headers_col is a TableColumn instance used to index columns in the table.

    """
    is_table = None
    def __init__(self, single_span=False):
        self._single_span = single_span
        self._data = []
        self._sub_tables = []

    def push_row(self, row):
        self._data.append(row)

    def push_table(self, table):
        self._data.append(table)

    def set_max_cols(self, max_cols):
        self._max_cols = max_cols

    def fixup(self):
        for obj in self._data:
            obj.fixup()  # row or table

        # Duplicate cells according to cell rowspans, and pad rows to correct
        # number of columns.  Duplication of cells for colspans was done by
        # row.fixup()
        cells_done = {}
        nr_rows = len(self._data)
        rows = [None]*nr_rows
        for i in range(nr_rows):
            row = self._data[i]
            if hasattr(row, "is_table"):
                # stick tables that are outside of any row in their own row
                table = row
                row = TableRow()
                row.push_table(table)
                self._data[i] = row
            else:
                # duplicate cells according to cell rowspans
                for j in range(len(row)):
                    cell = row[j]
                    if hasattr(cell, "is_table"): continue
                    if cells_done.has_key(cell): continue
                    cells_done[cell] = None
                    if cell.rowspan != 1:
                        for k in range(cell.rowspan-1):
                            row2 = self._data[i+k+1]
                            row2.insert(j, cell)

            # pad table to uniform number of columns
            to_pad = self._max_cols - len(row)
            while to_pad > 0:
                row.push_cell(None)
                to_pad -= 1

        self.headers_row = None
        # first row of headers are keys for indexing cols
        for row in self._data:
            if row.is_header:
                self.headers_row = row
                break
        for row in self._data:
            row.headers_row = self.headers_row

        # first col of headers are keys for indexing rows
        nr_cols = len(self._data[0])
        data = self._data
        for i in range(nr_cols):
            if self._col_is_header(i):
                self.headers_col = self._col_from_index(i)

        for table in self._sub_tables:
            table.fixup()

    def _col_is_header(self, colnr):
        for row in self._data:
            try:
                el = row[colnr].element_type
            except AttributeError:
                # This cell is padding to make up missing TD/TH elements on
                # this row.
                return False
            else:
                if el != "th":
                    return False
        return True

    def _col_from_index(self, colnr):
        tc = TableColumn(self._col_is_header(colnr))
        for row in self._data:
            obj = row[colnr]
            if hasattr(obj, "is_table"):
                tc.push_table(obj)
            else:
                tc.push_cell(obj)
        tc.fixup()
        return tc

    def __getitem__(self, key):
        if isstringlike(key):
            return self.get_col_by_name(key)
        return self._data[key]

    def get_col_by_name(self, colname):
        """Get column by finding its name in the headers_row attribute."""
        if self.headers_row is None:
            raise KeyError, "no header row has been set"
        i = self.headers_row.index(colname)
        return self._col_from_index(i)

    def get_row_by_name(self, rowname):
        """Get row by finding its name in the headers_col attribute."""
        if self.headers_col is None:
            raise KeyError, "no header column has been set"
        i = self.headers_col.index(rowname)
        return self._data[i]

    def get_col_by_nr(self, colnr):
        """Get column by integer index."""
        tc = TableColumn()
        for row in self._data:
            obj = row[colnr]
            if hasattr(obj, "is_table"):
                tc.push_table(obj)
            else:
                tc.push_cell(obj)
        tc.fixup()
        return tc

    def get_row_by_nr(self, rownr):
        """Get row by integer index."""
        return self._data[rownr]

    def col_iter(self):
        """Return iterator over columns of table."""
        return iterator(self.get_col_by_nr)
        #raise NotImplementedError

    def __iter__(self): return iterator(self.get_row_by_nr)

    def __str__(self):
        rep = []
        for row in self._data:
            rep.append("    %s" % row)
        return "%s[\n%s]" % (self.__class__.__name__, string.join(rep, "\n"))

    def __len__(self):
        return len(self._data)


class iterator:
    def __init__(self, index_fn):
        """
        index_fn: function behaving like __getitem__ for simple sequence
         object (ie. taking integer argument and returning a corresponding
         object, and raising IndexError if argument is out-of-bounds; valid
         indices must be consecutive)
        """
        self.__i = 0
        self.__index_fn = index_fn
    def __iter__(self): return self
    def next(self):
        try:
            r = self.__index_fn(self.__i)
        except IndexError:
            raise StopIteration
        self.__i += 1
        return r


class Cell:
    """A single cell of an HTML table.

    Note that a single cell may span many rows or columns (or both).

    Public readable attributes: data, rowspan, colspan, element_type.

    """
    def __init__(self, data, element_type="td",
                 rowspan=1, colspan=1):
        """
        data: string-lke object: contents of cell
        element_type: HTML element type; should be "td" or "th"
        rowspan: horizontal span of cell (nr. of rows occupied by cell)
        rowspan: horizontal span of cell (nr. of columns occupied by cell)

        """
        if not isstringlike(data):
            raise TypeError, "a string-like object is required for data"
        if not isinstance(rowspan, NumericTypes):
            raise TypeError, "an integer is required for rowspan"
        if not isinstance(colspan, NumericTypes):
            raise TypeError, "an integer is required for colspan"
        self.data = data
        self.element_type = element_type
        self.rowspan = rowspan
        self.colspan = colspan

    def __cmp__(self, other):
        if isinstance(other, Cell):
            if self.data == other.data: return 0
        elif self.data == other: return 0
        return 1

    def __str__(self): return self.data
    def __repr__(self):
        if self.rowspan != 1 or self.colspan != 1:
            span = "%dx%d " % (self.rowspan, self.colspan)
        else:
            span = ""
        return "<%sCell[%s]>" % (span, self.data)

    def __hash__(self): return id(self)


class TableSeq:
    """Abstract base class for TableRow and TableColumn."""
    def __init__(self, is_header=False):
        if is_header: self.is_header = True
        else: self.is_header = False
        self.headers = None
        self._data = []

    def fixup(self): pass

    def push_table(self, table):
        assert isinstance(table, HTMLTable), table.__class__.__name__
        self._data.append(table)

    def __str__(self):
        rep = []
        for line in self._data:
            rep.append(repr(line))
        return "%s[%s]" % (self.__class__.__name__, ", ".join(rep))
    def __contains__(self, item): return item in self._data
    def __len__(self): return len(self._data)
    def __getitem__(self, i): return self._data[i]
    def insert(self, i, item):
        assert isinstance(item, Cell), item.__class__.__name__
        self._data.insert(i, item)
    def count(self, item): return self._data.count(item)
    def index(self, item): return self._data.index(item)


# XXX TableRow and TableColumn are identical ATM, other than for names...
#  ...and push_cell, but that may be because TableColumn.push_cell is
#  incorrect
class TableRow(TableSeq):
    """Row of an HTML table.

    Indexing with a string gets a cell using the headers_row attribute.
    Indexing with an integer gets a cell.

    """
    def __init__(self, is_header=False):
        TableSeq.__init__(self, is_header)
        self.headers_row = None

    def push_cell(self, cell):
        if cell is not None:
            assert isinstance(cell, Cell), cell.__class__.__name__
            for i in range(cell.colspan):
                self._data.append(cell)
        else:
            assert cell is None
            self._data.append(cell)

    def __getitem__(self, key):
        if isstringlike(key):
            return self.get_cell_by_name(key)
        return self._data[key]

    def get_cell_by_nr(self, colnr):
        """Get cell by integer index."""
        return self._data[colnr]

    def get_cell_by_name(self, colname):
        """Get row by finding its name in the headers_row attribute."""
        if self.headers_row is None:
            raise KeyError, "no header row has been set"
        else:
            i = self.headers_row.index(colname)
            return self._data[i]


class TableColumn(TableSeq):
    """Row of an HTML table.

    Indexing with a string gets a cell using the headers_col attribute.
    Indexing with an integer gets a cell.

    """
    def __init__(self, is_header=False):
        TableSeq.__init__(self, is_header)
        self.headers_col = None

    def push_cell(self, cell):
        # XXX shouldn't this do the same as TableColumn??
        self._data.append(cell)

    def __getitem__(self, key):
        if isstringlike(key):
            return self.get_cell_by_name(key)
        return self._data[key]

    def get_cell_by_nr(self, rownr):
        """Get cell by integer index."""
        return self._data[rownr]

    def get_cell_by_name(self, colname):
        """Get column by finding its name in the headers_col attribute."""
        if self.headers_col is None:
            raise KeyError, "no header column has been set"
        else:
            i = self.headers_col.index(rowname)
            return self._data[i]

# Notes about cell spans.
# "rowspan" is nr rows spanned.
# "colspan" is nr cols spanned.
# COL has rowspan, colspan attributes.
# COLs default to unity span.
# TD and TH have rowspan, colspan attributes.
# COLGROUP has span attribute (which is a colspan).
# COLGROUPs default to unity span.
# COLGROUPs with no COLs have unity span.
# COLGROUPs with contained COLs have span equal to sum of colspans of
#  contained COLs (the COLGROUP's span itself counts for nothing in this
#  case).
# If no COLGROUPs or COLs, nr of cols is determined by max row length
#  (taking TD and TH colspans into account).  Pad short rows up to this nr
#  of cols.  Even if there *are* COLGROUPs or COLs, this col. width should
#  agree (in theory) with that calculated from COLGROUP and COL spans, but
#  should use COLGROUP/COL algorithm in preference to counting row
#  lengths.

class ParseState:
    def __init__(self):
        self.cell_data = []  # TD and TH element data (strings)

        # set to HTMLTable object iff nested sub-table is being parsed
        self.table = None
        self.tablerow = None

        # following are true iff in named element
        self.in_table = False
        self.in_tr = False
        self.in_th = False
        self.in_td = False
        self.in_colgroup = False

        # current position in table
        self.col = 0
        self.row = 0

        # true after parsing row iff this is a header row
        self.in_header_row = False
        # true after parsing table iff COL or COLSPAN was seen in this table
        self.have_col = False

        # column-counting for case where self.have_col is false after parsing
        self.tx_colspan = 1
        self.tx_rowspan = 1
        self.tx_cols = 0  # total span from TDs and THs

        # column-counting for case where self.have_col is true after parsing
        self.colgroup_span = 0  # span due to COLGROUP containing no COLs
        self.colgroup_cols = 0  # total span of COLGROUP due to contained COLs
        self.col_cols = 0  # total span from COLs and COLSPANs


class ParseError(Exception): pass
class ParseFinished(Exception): pass

# XXX
# Look at HTML::TreeBuilder to check implicit td / th (etc.) rules.
# THEAD -- contains TRs, but is header.
# Move implicit element ending stuff to handle_starttag / handle_endtag?

class TableParser(HTMLParser.HTMLParser):
    """HTML Table parser."""
    table_tags = "table", "tr", "td", "th", "col", "colgroup"  # XXXX
    def __init__(self, nr_to_parse=-1,
                 nr_toplevel_to_parse=-1,
                 single_span=False,
                 strip_tags=False,
                 collapse_whitespace=False,
                 recode_entities=None):
        """
        nr_to_parse: only parse this number of tables, then stop; if negative,
         parse all tables in the document
        single_span: return cells that span multiple columns or rows only
         once, rather than once for every row / column they span
        collapse_whitespace: convert all consecutive whitespace characters
         to a single space
        # XXX name recode_entities is poor if this is a dict
        recode_entities: recode HTML entities according to this dict
        depth: internal use only

        """
        HTMLParser.HTMLParser.__init__(self)

        if nr_toplevel_to_parse >= 0:
            raise NotImplementedError, \
                  "nr_toplevel_to_parse not yet implemented"
        if single_span != False:
            raise NotImplementedError, \
                  "single_span not yet implemented"

        self._nr_to_parse = nr_to_parse
        self._nr_toplevel_to_parse = nr_toplevel_to_parse
        if single_span: self._single_span = True
        else: self._single_span = False
        if strip_tags: self._strip_tags = True
        else: self._strip_tags = False
        if collapse_whitespace: self._collapse_whitespace = True
        else: self._collapse_whitespace = False
        self._recode_entities = recode_entities

        # the end result
        self.tables = []

        self._stack = []  # parse state stack
        self._depth = 0  # table nesting depth

        self._ps = ParseState()

    def handle_entityref(self, name):
        #print "handle_entityref", name
        if self.recode_entities:
            self.handle_data(self.recode_entities[name])

##     def handle_charref(self, name):
##         pass

    def handle_starttag(self, tag, attrs):
        #print "handle_starttag"
        #print "tag", tag
        if self._ps.in_colgroup and tag != "col":
            self.end_colgroup()

        # XXX put this in when rest of parser has stabilised
##         if self._depth == 0 and tag not in self.table_tags:
##             # implicit end of top-level table
##             self.end_table()

        if not self._strip_tags:
            if ((self._ps.in_td or self._ps.in_th) and
                tag not in self.table_tags):
                self._ps.cell_data.append(self.get_starttag_text())
        else:
            self._ps.cell_data.append(" ")

        try:
            method = getattr(self, "start_" + tag)
        except AttributeError:
            try:
                method = getattr(self, "do_" + tag)
            except AttributeError:
                pass
            else:
                method(attrs)
        else:
            method(attrs)

    def handle_endtag(self, tag):
        #print "handle_endtag"
        if self._ps.in_colgroup and tag != "col":
            self.end_colgroup()

        # capture
        if not self._strip_tags:
            if ((self._ps.in_td or self._ps.in_th) and
                tag not in self.table_tags):
                self._ps.cell_data.append("</%s>" % tag)
        else:
            self._ps.cell_data.append(" ")

        try:
            method = getattr(self, "end_" + tag)
        except AttributeError:
            method = None
        if method:
            method()

    def start_table(self, attrs):
        #print "start_table"
        if self._ps.in_tr:
            if self._ps.in_td: self.end_td()
            if self._ps.in_th: self.end_th()
            #self.end_tr()

        if self._nr_to_parse == 0:
            raise ParseFinished

        self._depth += 1
        self._stack.append(self._ps)
        self._ps = ParseState()
        self._ps.table = HTMLTable()

        self._ps.in_table = True
        self._ps.row = self._ps.col = 0
    def end_table(self):
        #print "end_table"
        if not self._ps.in_table: raise ParseError, "end of TABLE before start"
        if self._ps.in_tr:
            if self._ps.in_td: self.end_td()
            if self._ps.in_th: self.end_th()
            self.end_tr()

        table = self._ps.table

        # number of columns to pad to
        if self._ps.have_col: max_cols = self._ps.col_cols
        else: max_cols = self._ps.tx_cols
        table.set_max_cols(max_cols)  # XXXX yuck

        self._depth -= 1
        if self._depth == 0:
            self.tables.append(table)
        else:
            self._ps = self._stack.pop()
            if self._ps.in_tr:
                self._ps.tablerow.push_table(table)
            else:
                self._ps.table.push_table(table)

        self._nr_to_parse -= 1

    def start_col(self, attrs):
        if not self._ps.in_table: raise ParseError, "COL outside of TABLE"
        span = 1
        for k, v in attrs:
            if k == "span": span = int(v, 10)
        self._ps.have_col = True
        self._ps.colgroup_cols += span

    def start_colgroup(self, attrs):
        if not self._ps.in_table: raise ParseError, "COL outside of TABLE"
        self._ps.in_colgroup = True
        self._ps.have_col = True
        self._ps.colgroup_cols = 0
        span = 1
        for k, v in attrs:
            if k == "span": span = int(v, 10)
        self._ps.colgroup_span = span
    def end_colgroup(self):
        if not self._ps.in_colgroup:
            raise ParseError, "end of COLGROUP before start"
        self._ps.in_colgroup = False
        if self._ps.colgroup_cols == 0:
            self._ps.col_cols += self._ps.colgroup_span
        else:
            self._ps.col_cols += self._ps.colgroup_cols

    def start_tr(self, attrs):
        #print "start_tr"
        if not self._ps.in_table:
            raise ParseError, "start of TR element outside of TABLE"
        if self._ps.in_tr:
            if self._ps.in_td: self.end_td()
            if self._ps.in_th: self.end_th()
            self.end_tr()
        self._ps.tablerow = TableRow()
        self._ps.in_tr = True
        self._ps.col = 0
    def end_tr(self):
        #print "end_tr"
        if not self._ps.in_table:
            raise ParseError, "end of TR element outside of TABLE"
        if self._ps.in_td: self.end_td()
        if self._ps.in_th: self.end_th()
        self._ps.tx_cols = max(self._ps.tx_cols, len(self._ps.tablerow))
        self._ps.tablerow.is_header = self._ps.in_header_row
        self._ps.table.push_row(self._ps.tablerow)
        self._ps.in_header_row = False
        self._ps.in_tr = False
        self._ps.row += 1

    def _process_cell_data(self):
        """Consolidate data for single table entry (including headers)."""
        #print "_process_cell_data"
        if self._collapse_whitespace:
            data = "".join(self._ps.cell_data).strip()
            data = collapse_whitespace(data)
        else:
            data = "".join(self._ps.cell_data)

        if self._ps.in_th: el = "th"
        else: el = "td"

        cell = Cell(data, el, self._ps.tx_rowspan, self._ps.tx_colspan)
        self._ps.tablerow.push_cell(cell)
        self._ps.cell_data = []

    def start_th(self, attrs):
        #print "start_th"
        if not self._ps.in_table: raise ParseError, "TH outside of TABLE"
        if self._ps.in_th: self.end_th()
        if self._ps.in_td: self.end_td()
        self._ps.in_header_row = True
        self._ps.in_th = True
        self._ps.tx_colspan = self._ps.tx_rowspan = 1
        for k, v in attrs:
            if k == "colspan": self._ps.tx_colspan = int(v, 10)
            if k == "rowspan": self._ps.tx_rowspan = int(v, 10)
    def end_th(self):
        #print "end_th"
        if not self._ps.in_th: raise ParseError, "end of TH before start"
        assert self._ps.in_table
        self._process_cell_data()
        self._ps.in_th = False
        self._ps.col += 1

    def start_td(self, attrs):
        #print "start_td"
        if not self._ps.in_table: raise ParseError, "TD outside of TABLE"
        if self._ps.in_td: self.end_td()
        if self._ps.in_th: self.end_th()
        self._ps.in_td = True
        self._ps.tx_colspan = self._ps.tx_rowspan = 1
        for k, v in attrs:
            if k == "colspan": self._ps.tx_colspan = int(v, 10)
            if k == "rowspan": self._ps.tx_rowspan = int(v, 10)
    def end_td(self):
        #print "end_td"
        if not self._ps.in_td: raise ParseError, "end of TD before start"
        assert self._ps.in_table
        self._process_cell_data()
        self._ps.in_td = False
        self._ps.col += 1

    def handle_data(self, data):
        if not self._ps.in_table: return
        #print "handle_data >>%s<<" % data
        if self._ps.in_td or self._ps.in_th:
            self._ps.cell_data.append(data)
