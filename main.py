from app import app
from app.gedcom import Gedcom
import sys

def main():
    if len(sys.argv) < 2:
        print("Specify ged-file")
        sys.exit(0)
    
    ged = Gedcom(sys.argv[1])
    ged.parse()

    app.config['GEDCOM'] = ged
    app.run(debug=True)

if __name__ == '__main__':
    main()