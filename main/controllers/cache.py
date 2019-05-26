import json
from datetime import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_
from db import db

from main.models.entry import EntryModel
from main.models.result import ResultModel
from main.engines import entry_result
from main.libs.identifier import generate_id

cache = Blueprint('cache', __name__)

REQUIRED_FIELDS = ['latitude', 'longitude', 'radius']

MAIN_CATEGORIES = ['food', 'drinks', 'art']


@cache.route('/queries', methods=['GET'])
def get_cached_queries():
    params = request.args
    # Check required fields
    for field in REQUIRED_FIELDS:
        if params.get(field) is None:
            return jsonify({'message': '{} is a required field'.format(field)}), 400
    page = params.get('page') or 1

    # Generate hashed value and check in the cache
    hashed_id = generate_id(params, ['latitude', 'longitude', 'radius', 'categories'])
    query = EntryModel.query.get(hashed_id)
    if query is not None:
        print('query existed')
        results = entry_result.get_entry_results(hashed_id, page)
        total_pages = entry_result.get_entry_total_pages(hashed_id)
        return jsonify({
            'results': results,
            'page': page,
            'total_pages': total_pages
        })
    latitude = params.get('latitude') and float(params.get('latitude'))
    longitude = params.get('longitude') and float(params.get('longitude'))
    radius = params.get('radius') and float(params.get('radius'))

    # Add location to the query according to the formula in Appendix B
    related_queries = EntryModel.query.filter(and_(
        func.asin(func.sqrt(0.5 - func.cos(func.radians(latitude) - func.radians(EntryModel.latitude)) / 2
                            + func.cos(func.radians(EntryModel.latitude))
                            * func.cos(func.radians(latitude))
                            * (1 - func.cos(func.radians(longitude - EntryModel.longitude))) / 2)
                  ) * 12742 <= 0.2 * radius,
        func.abs(radius - EntryModel.radius) <= 0.2 * radius
    )).all()

    if len(related_queries) > 0:
        categories = params.get('categories')
        if categories:
            # The list of related queries is expected to be so small that a loop doesn't affect the performance much
            for query in related_queries:
                print('Create references')
                if query.categories == categories:
                    # This means the 2 queries should have the same results
                    first_page_results, total_pages = copy_entry(query.id, hashed_id, latitude,
                                                                 longitude, radius, categories)
                    return jsonify({
                        'results': first_page_results,
                        'page': 1,
                        'total_pages': total_pages
                    })
        no_category_queries = [query for query in related_queries if not query.categories]
        if len(no_category_queries) > 0:
            print('Created references')
            # This means the 2 queries should have the same results
            first_page_results, total_pages = copy_entry(no_category_queries[0].id, hashed_id, latitude,
                                                         longitude, radius, categories)
            return jsonify({
                'results': first_page_results,
                'page': 1,
                'total_pages': total_pages
            })
        main_category_queries = [query for query in related_queries
                                 if len([category for category in MAIN_CATEGORIES
                                         if category in query.categories
                                         ]) > 0]
        if len(main_category_queries) > 1:
            # Merge the queries and return
            merged_results = []
            for query in main_category_queries:
                query_results = ResultModel.query.filter_by(entry_id=query.id).all()
                for result in query_results:
                    merged_results += entry_result.get_entry_results(query.id, result.page)
            new_query = EntryModel(id=hashed_id,
                                   latitude=latitude,
                                   longitude=longitude,
                                   radius=radius,
                                   categories=categories)
            db.session.add(new_query)
            db.session.commit()
            entry_result.store_entry_results(hashed_id, merged_results)

    return jsonify({}), 404


@cache.route('/queries', methods=['POST'])
def store_query_to_cache():
    data = json.loads(request.json)
    # Check required fields
    for field in REQUIRED_FIELDS:
        if data.get(field) is None:
            return jsonify({'message': '{} is a required field'.format(field)}), 400

    results = data.get('results')
    if not results:
        return jsonify({'message': 'results field is required'}), 400

    categories = data.get('categories')
    latitude = data['latitude']
    longitude = data['longitude']
    radius = data['radius']

    hashed_id = generate_id({
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'categories': categories,
    }, ['latitude', 'longitude', 'radius', 'categories'])

    query = EntryModel.query.get(hashed_id)
    if query is not None:
        now = datetime.utcnow()
        if (now - query.updated).days > 7:
            entry_result.clear_entry_results(hashed_id)
            # Write results to file to reduce cache size
            entry_result.store_entry_results(hashed_id, results)
            query.updated = now
            db.session.commit()
    else:
        query = EntryModel(id=hashed_id,
                           latitude=latitude,
                           longitude=longitude,
                           radius=radius,
                           categories=categories)
        db.session.add(query)
        db.session.commit()

        # Write results to file to reduce cache size
        entry_result.store_entry_results(hashed_id, results)

    return jsonify({
        'results': entry_result.get_entry_results(hashed_id, 1),
        'page': 1,
        'total_pages': entry_result.get_entry_total_pages(hashed_id)
    }), 201


def copy_entry(existed_entry_id, entry_id, latitude, longitude, radius, categories):
    # Create a new query, so the later requests can be access fast
    new_query = EntryModel(id=entry_id,
                           latitude=latitude,
                           longitude=longitude,
                           radius=radius,
                           categories=categories)
    db.session.add(new_query)
    db.session.commit()
    # Create references to page results
    for page_result in ResultModel.query.filter(ResultModel.entry_id == existed_entry_id).all():
        new_page_result = ResultModel(entry_id=new_query.id, data_path=page_result.data_path,
                                      page=page_result.page)
        db.session.add(new_page_result)
    db.session.commit()

    first_page_results = entry_result.get_entry_results(new_query.id, 1)
    total_pages = entry_result.get_entry_total_pages(new_query.id)
    return first_page_results, total_pages
