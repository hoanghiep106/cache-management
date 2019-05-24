def generate_id(dict, ordered_keys):
    key_values = [[key, dict.get(key)] for key in ordered_keys]
    concat_string = '_'.join(['{}:{}'.format(key_value[0], key_value[1]) for key_value in key_values])
    return hash(concat_string)
