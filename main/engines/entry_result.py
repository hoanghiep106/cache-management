import os
import json
import uuid

from db import db
from main.models.result import ResultModel

DATA_FOLDER_NAME = 'data'

PAGE_LIMIT = 12


def store_entry_results(entry_id, results):
    total_pages = len(results) / PAGE_LIMIT + 1
    for i in xrange(0, total_pages - 1):
        page = i + 1
        page_data = results[i * PAGE_LIMIT:(i + 1) * PAGE_LIMIT]
        file_path = _write_json_file(page_data)
        result_page = ResultModel(entry_id=entry_id, data_path=file_path, page=page)
        db.session.add(result_page)
    if (total_pages - 1) * PAGE_LIMIT < len(results):
        last_page_data = results[(total_pages - 1) * PAGE_LIMIT:]
        file_path = _write_json_file(last_page_data)
        result_page = ResultModel(entry_id=entry_id, data_path=file_path, page=total_pages)
        db.session.add(result_page)
    db.session.commit()


def clear_entry_results(entry_id):
    result_pages = ResultModel.query.filter_by(entry_id=entry_id).all()
    for result_page in result_pages:
        try:
            _delete_file(result_page.data_path)
        except Exception as e:
            print(e, result_page.data_path)
        db.session.delete(result_page)
    db.session.commit()


def get_entry_results(entry_id, page):
    result_page = ResultModel.query.filter(ResultModel.entry_id == entry_id, ResultModel.page == page).first()
    if not result_page:
        return []
    return _read_json_file(result_page.data_path)


def get_entry_total_pages(entry_id):
    return ResultModel.query.filter_by(entry_id=entry_id).count()


def _write_json_file(data):
    filename = uuid.uuid4()
    data_path = '{}/{}'.format(os.getcwd(), DATA_FOLDER_NAME)
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
    file_path = '{}/{}.json'.format(data_path, filename)
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)
    return file_path


def _read_json_file(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def _delete_file(path):
    os.remove(path)
