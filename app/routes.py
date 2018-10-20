from app import app

from flask import jsonify
from flask import url_for

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

from .individual import Individual


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/record/<string:id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_record(id):
    ged = app.config['GEDCOM']
    return jsonify(ged.all_records[id].to_dict())


@app.route('/individuals', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_individuals():
    ged = app.config['GEDCOM']
    records = ged.tag_index['INDI']
    data = []
    for rec in list(records.keys()):
        record = Individual(records[rec], ged)

        data.append(record.to_json())
    return jsonify(data)


@app.route('/tags/<string:id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_tag(id):
    ged = app.config['GEDCOM']
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
    ged = app.config['GEDCOM']
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
