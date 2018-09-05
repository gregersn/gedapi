from app import app

from flask import jsonify
from flask import url_for


@app.route('/record/<string:id>', methods=['GET'])
def get_record(id):
    ged = app.config['GEDCOM']
    return jsonify(ged.all_records[id].to_dict())


@app.route('/tags/<string:id>', methods=['GET'])
def get_tag(id):
    records = ged.tag_index[id]
    data = []
    for rec in records.keys():
        record = records[rec]
        rec_dict = record.to_dict()
        if record.xref:
            rec_dict['_links'] = {
                'self': url_for('get_record', id=record.xref)
            }
        data.append(rec_dict)
    return jsonify(data)


@app.route('/')
@app.route('/index')
@app.route('/tags')
def index():
    tags = ged.tag_index.keys()
    data = {
        'tags': []
    }

    for tag in tags:
        data['tags'].append({
            'tag': tag,
            '_links': {
                'self': url_for('get_tag', id=tag)
            }
        })
    response = jsonify(data)
    return response
