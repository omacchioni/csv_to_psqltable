#!/usr/bin/python

import csv
import time
from optparse import OptionParser


class PGTableCreator():
    """ Read a CSV file and try to guess the right DB structure to save it """

    def _duplicates(self, mylist):
        d = {}
        for elem in mylist:
            if elem in d:
                d[elem] += 1
            else:
                d[elem] = 1
        return [x for x, y in d.items() if y > 1]

    def is_type_integer(self, s):
        try:
            int(s)
            return -2147483648 <= int(s) <= +2147483647
        except (ValueError, OverflowError):
            return False

    def is_type_float(self, s):
        try:
            float(s)
            return True
        except (ValueError, OverflowError):
            return False

    def is_type_date(self, s):
        # 2012-DEC-01 to "2012-Dec-01"
        s = s.title()
        for datetime_format in (
                '%Y-%m-%d',
                '%Y-%b-%d',
                '%d-%b-%Y',
                ):
            try:
                time.strptime(s, datetime_format)
                return True
            except (ValueError, OverflowError):
                pass
        return False

    def is_type_datetime(self, s):
        # 2012-DEC-01 to "2012-Dec-01"
        s = s.title()
        for datetime_format in (
                '%Y-%m-%d %H:%M:%S',
                '%Y-%b-%d %H:%M:%S',
                '%d-%b-%Y %H:%M:%S',
                ):
            try:
                time.strptime(s, datetime_format)
                return True
            except (ValueError, OverflowError):
                pass
        return False

    def run(self, filename, tablename):
        with open(filename, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            headers = csvreader.next()
            dups = self._duplicates(headers)
            if dups:
                print "Warning - duplicate columns, %s" % str(dups)

            default_properties = {
                'integer': True,
                'float': True,
                'date': True,
                'datetime': True,
                'maxlen': 0,
            }
            header_properties = dict((h, default_properties.copy()) for h in headers)
            line = 0
            for row in csvreader:
                line += 1
                # Skip invalid lines
                if len(row) != len(headers):
                    print "Warning - skipped line %d" % (line + 1, )
                    continue
                i = 0
                for cell in row:
                    for cell_type in ['integer', 'float', 'date', 'datetime']:
                        f = getattr(self, "is_type_%s" % cell_type)
                        if cell and header_properties[headers[i]][cell_type] and not f(cell):
                            header_properties[headers[i]][cell_type] = False
                    header_properties[headers[i]]['maxlen'] = max(header_properties[headers[i]]['maxlen'], len(cell))
                    i += 1

            # Remove empty headers
            headers = filter(bool, headers)

            print "CREATE TABLE %s (" % (tablename, )
            field_declaration = []
            for h in headers:
                if header_properties[h]['integer']:
                    field_declaration.append("%s INT" % (h, ))
                elif header_properties[h]['float']:
                    field_declaration.append("%s FLOAT" % (h, ))
                elif header_properties[h]['date']:
                    field_declaration.append("%s DATE" % (h, ))
                elif header_properties[h]['datetime']:
                    field_declaration.append("%s TIMESTAMP" % (h, ))
                else:
                    field_declaration.append("%s VARCHAR(%s)" % (h, header_properties[h]['maxlen']))
            print (", ".join(field_declaration))
            print ");"

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
            help="Read data from FILE", metavar="FILE")
    parser.add_option("-t", "--table", dest="tablename",
            help="Name of the table to create", metavar="TABLENAME",
            default="xx")
    (options, args) = parser.parse_args()

    pgtc = PGTableCreator()
    pgtc.run(options.filename, options.tablename)
