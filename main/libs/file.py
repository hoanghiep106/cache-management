import os
import json
import uuid

DATA_FOLDER_NAME = 'data'


def write_json_file(data):
    filename = uuid.uuid4()
    data_path = '{}/{}'.format(os.getcwd(), DATA_FOLDER_NAME)
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
    file_path = '{}/{}.json'.format(data_path, filename)
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)
    return file_path
