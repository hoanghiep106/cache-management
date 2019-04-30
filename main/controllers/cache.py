import json

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from db import db

from main.models.queries import QueryModel
from main.libs.file import write_json_file, read_json_file

cache = Blueprint('cache', __name__)

REQUIRED_FIELDS = ['latitude', 'longitude']

# km unit
DISTANCE_LIMIT = 5


class ResponseType:
    FULLY_HIT = 'fully_hit'
    PARTIALLY_HIT = 'partially_hit'
    MISSED = 'missed'


@cache.route('/queries', methods=['GET'])
def get_cached_queries():
    params = request.args
    # Check required fields
    for field in REQUIRED_FIELDS:
        if params.get(field) is None:
            return jsonify({'message': '{} is a required field'.format(field)}), 400

    latitude = params['latitude']
    longitude = params['longitude']
    # Add location to the query
    query = QueryModel.query.filter(func.acos(func.sin(func.radians(latitude)) *
                                              func.sin(func.radians(QueryModel.latitude))
                                              + func.cos(func.radians(latitude)) *
                                              func.cos(func.radians(QueryModel.latitude))
                                              * func.cos(func.radians(QueryModel.longitude)
                                                         - (func.radians(longitude))))
                                    * 6371 <= DISTANCE_LIMIT)

    categories = params.get('categories')
    if categories:
        query.filter(QueryModel.category.in_(categories))

    cached_queries = query.all()

    # Extract results from data file
    results = []
    for cached_query in cached_queries:
        data = read_json_file(cached_query.result_path)
        results += data

    return jsonify({
        'results': results,
    })


@cache.route('/queries', methods=['POST'])
def store_query_to_cache():
    data = json.loads(request.data)
    # Check required fields
    for field in REQUIRED_FIELDS:
        if data.get(field) is None:
            return jsonify({'message': '{} is a required field'.format(field)}), 400

    results = data.get('results')
    if not results:
        return jsonify({'message': 'results is required'}), 400

    latitude = data['latitude']
    longitude = data['longitude']

    # Write results to file to reduce cache size
    result_path = write_json_file(results)

    query = QueryModel(latitude=latitude, longitude=longitude, result_path=result_path)
    db.session.add(query)
    db.session.commit()
    return jsonify({}), 201
