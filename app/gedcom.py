import re
import sys
import os
import typing

EOL = "\r\n"
LINE_LENGTH = 253

REGEX_TAG = '[_A-Z][_A-Z0-9]*'
REGEX_XREF = '[A-Za-z0-9:_-]+'
REGEX_VALUE = '.+'


def data_split(gedcom: str, level=0):
    datapoints = re.split(r'\n(?={})'.format(level), gedcom)
    return datapoints


def record_identifier(data: str):
    datapoints = re.match(r'^0 (?:@(?P<xref>[A-Za-z0-9:_-]+)@ )?(?P<tag>{})'.format(REGEX_TAG), data)
    assert datapoints is not None, data
    return datapoints.group('xref'), datapoints.group('tag')

fact_classes = {

}


class Fact(object):
    def __init__(self, gedcom: str, level=0) -> None:
        self.xref = None
        self.tag = None
        self.level = level

        self.value = None
        self.gedcom = gedcom
        self.children = []

        self.parse_gedcom(gedcom)

    def parse_gedcom(self, gedcom):
        datalines = data_split(gedcom, self.level + 1)
        assert len(datalines) > 0
        assert datalines[0][0] == str(self.level), "{} {}".format(self.level,
                                                                  datalines[0])

        REGEX_GEDLINE = r'^{} (?:@(?P<xref>{})@ )?(?P<tag>{})(?: (?P<value>{}))?'

        fact_type = re.match(REGEX_GEDLINE.format(self.level,
                                                  REGEX_XREF,
                                                  REGEX_TAG,
                                                  REGEX_VALUE),
                             datalines.pop(0))

        assert fact_type is not None
        assert fact_type.group('tag') is not None

        self.xref = fact_type.group('xref') or None
        self.tag = fact_type.group('tag')

        if fact_type.group('value') is not None:
            self.value = fact_type.group('value')

        while len(datalines) > 0:
            fact = datalines.pop(0)
            self.children.append(Fact.parse(fact, level=self.level + 1))

    def to_gedcom(self):
        output = []

        this_line = ["{}".format(self.level)]

        if self.xref is not None:
            this_line.append("@{}@".format(self.xref))
        
        this_line.append(self.tag)
        
        if self.value is not None:
            this_line.append(self.value)
        
        output.append(" ".join(this_line))

        if len(self.children) > 0:
            for fact in self.children:
                output.append(fact.to_gedcom())
        return ("\n").join(output)

    def to_dict(self):
        # outdata = {'tag': self.tag}
        outdata = {}

        if self.xref:
            outdata['xref'] = self.xref
        
        if self.value:
            outdata['value'] = self.value
        
        if len(self.children) > 0:
            for ch in self.children:
                if ch.tag not in outdata:
                    outdata[ch.tag] = ch.to_dict()
                else:
                    if type(outdata[ch.tag]) != list:
                        outdata[ch.tag] = [outdata[ch.tag], ]
                    
                    outdata[ch.tag].append(ch.to_dict())
                
            # outdata['sub'] = [ch.to_dict() for ch in self.children]
    
        return outdata

    def __repr__(self):
        if self.value:
            return self.value
        else:
            return ""
    
    def get_fact(self, tag: str):
        output = []
        for fact in self.children:
            if fact.tag == tag:
                output.append(fact)
        if len(output) < 1:
            return None
        
        if len(output) == 1:
            return output[0]

        return output

    @classmethod
    def parse(cls, gedcom: str, level=1):
        r = cls(gedcom, level)
        if r.tag in fact_classes:
            return fact_classes[r.tag](gedcom, level)
        return r


def register_tag(tag):
    def classdecorator(classname):
        global fact_classes
        fact_classes[tag] = classname
        return classname
    return classdecorator


@register_tag('TEXT')
class FactText(Fact):
    def to_dict(self):
        return {
            'tag': self.tag,
            'xref': self.xref,
            'value': "\n".join([self.value or ""] +
                               [ch.value or ""
                                for ch in self.children or []
                                if ch.tag == "CONT"])
        }


@register_tag('NOTE')
class FactNote(FactText):
    pass



class Gedcom(object):
    def __init__(self, filename: str) -> None:
        self.data = ""
        self.filename = filename
        self.header = None
        assert os.path.isfile(filename)
        self.all_records = {}
        self.tag_index = {}

    def parse(self, level=0):
        data = ""
        with open(self.filename, 'r') as f:
            data = f.read()

        ged_records = data_split(data, level=level)

        while len(ged_records) > 0:

            ged_rec = ged_records.pop(0)
            r = Fact.parse(ged_rec, level=level)

            if r.tag == 'HEAD':  # Header
                self.header = r
                continue
            
            if r.tag == 'TRLR':  # End of data
                break

            if r.xref in self.all_records:
                raise IndexError

            if r.tag not in self.tag_index:
                self.tag_index[r.tag] = {}
            
            self.tag_index[r.tag][r.xref] = r

            self.all_records[r.xref] = r
        


def main():
    test_data = "0 @I1@ INDI\n1 SEX M\n1 BIRT\n2 DATE 1642\n1 NAME John Doe /Smith/\n2 GIVN John Doe\n2 NICK Johnny\n1 DEAT\n2 DATE 1721\n2 PLAC Re, Vestfold, Norway\n1 RESI\n2 DATE FROM 1675 TO 1708\n2 PLAC Sandefjord, Vestfold, Norway\n2 ADDR Bruk 1\n1 FAMS @F323@\n1 FAMC @F328@\n1 NOTE @N58@\n1 CHAN\n2 DATE 29 APR 2018\n3 TIME 09:15:43\n2 _WT_USER greger"

    record = Fact.parse(test_data, level=0)

    assert record.xref == 'I1'
    assert record.tag == 'INDI'
    assert record.get_fact('SEX') is not None
    assert record.get_fact('SEX').value == 'M'
    assert record.get_fact('BIRT') is not None
    assert record.get_fact('NAME') is not None
    assert record.get_fact('DEAT') is not None

    assert record.to_gedcom() == test_data, record.to_gedcom()
    return

if __name__ == '__main__':
    if len(sys.argv) < 2:
        main()
    else:
        ged = Gedcom(sys.argv[1])
        ged.parse()

