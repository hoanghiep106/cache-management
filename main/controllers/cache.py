from flask import Blueprint, request, jsonify
from sqlalchemy import func

from main.models.queries import QueryModel

cache = Blueprint('cache', __name__)

REQUIRED_FIELDS = ['latitude', 'longitude']

# km unit
DISTANCE_LIMIT = 0.5


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
            return jsonify({'message': '{} is a required field'.format(field)}, 200)

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
    # query = QueryModel.query.filter(
    #     func.asin(func.sqrt(0.5 - func.cos(func.radians(latitude) - func.radians(QueryModel.latitude)) / 2
    #                         + func.cos(func.radians(QueryModel.latitude))
    #                         * func.cos(func.radians(latitude))
    #                         * (1 - func.cos(func.radians(longitude - QueryModel.longitude))) / 2)
    #               ) * 12742 <= DISTANCE_LIMIT)

    # query = QueryModel.query.filter(
    #     6373 * 2 *
    #     func.atan2(func.sqrt(func.sin((func.radians(latitude) - func.radians(QueryModel.latitude)) / 2) ** 2
    #                          + func.cos(func.radians(QueryModel.latitude)) * func.cos(func.radians(latitude))
    #                          * func.sin((func.radians(longitude) - func.radians(QueryModel.longitude)) / 2) ** 2),
    #                func.sqrt(1 - (func.sin((func.radians(latitude) - func.radians(QueryModel.latitude)) / 2) ** 2
    #                               + func.cos(func.radians(QueryModel.latitude))
    #                               * func.cos(func.radians(latitude))
    #                               * func.sin((func.radians(longitude) - func.radians(QueryModel.longitude)) / 2) ** 2)
    #                          )
    #                )
    # )

    categories = params.get('categories')
    if categories:
        query.filter(QueryModel.category.in_(categories))

    results = query.all()

    # result_categories = set([item.category for item in results if item is not None])
    # missed_categories = [category for category in categories if category not in result_categories]

    # names = params.get('names')
    # if names:
    #     results = [result for result in results if ]

    return jsonify({
        'results': results,
    })


def compute_response_type(results):
    return ResponseType.MISSED


def get_cache(latitude, longitude, types, names):
    return []
