class Individual(object):
    def __init__(self, gedcom, db):
        data = gedcom # .to_dict()

        self.id = data.xref

        self.name = data.get_fact('NAME')
        self.birth = data.get_fact('BIRT')
        # print(self.birth.to_dict())

        self.parent_family = ""
        self.parents = []

        famc = data.get_fact('FAMC')
        if famc:
            if type(famc) == list:
                self.parent_family = famc
                # self.parent_family = data['FAMC'][0]['value']
            else:
                self.parent_family = [famc]

            for parfam in self.parent_family:
                family_record = db.all_records[parfam.value[1:-1]].to_dict()
                if 'HUSB' in family_record:
                    self.parents.append(family_record['HUSB']['value'][1:-1])
                
                if 'WIFE' in family_record:
                    self.parents.append(family_record['WIFE']['value'][1:-1])

    def to_json(self):
        return {
            'id': self.id,
            'parent_family': self.parent_family,
            'parents': self.parents
        }
    
    def __repr__(self):
        return "{}: {} ({})".format(self.id, self.name, self.birth.get_fact('DATE'))

