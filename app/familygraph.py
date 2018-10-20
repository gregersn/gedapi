import sys

from individual import Individual
from gedcom import Gedcom


def main():
    ged = Gedcom(sys.argv[1])
    ged.parse()

    records = ged.tag_index['INDI']
    data = []
    for rec in list(records.keys()):
        record = Individual(records[rec], ged)

        data.append(record)
    
    indi_index = {}
    for person in data:
        indi_index[person.id] = person
    
    queue = []
    visited = []

    print("There are {} people".format(len(data)))
    queue.append(data[0])

    while len(queue) > 0:
        cur = queue.pop(0)
        if cur.id in visited:
            print("Repeat {}".format(cur))
            continue
    
        for parent in cur.parents:
            queue.append(indi_index[parent])

        visited.append(cur.id)
    print("Visited {} people".format(len(visited)))
        


if __name__ == '__main__':
    main()