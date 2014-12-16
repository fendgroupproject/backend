from bson.objectid import ObjectId
# from datetime import datetime


def document_to_dict(document):
    """Converts a mongoengine Document to a Python dict.
    Builds an external representation of the document. For
    example convert `'_id': ObjectId('54dqf8ad6sdfq14ad')` to
    ''id': '54dqf8ad6sdfq14ad'`.

    :param document: the mongoengine Document to convert
    """
    return _sanitize(document.to_mongo().to_dict())


def _sanitize(value):
    if type(value) is dict:
        return _sanitize_dict(value)
    elif type(value) is list:
        return [_sanitize(e) for e in value]

    return _sanitize_scalar(value)


def _sanitize_dict(d):
    rv = {}

    for key, value in d.iteritems():
        rv[key] = _sanitize(value)

        if key is '_id':
            rv['id'] = rv.pop(key)

    return rv


def _sanitize_scalar(s):
    if type(s) is ObjectId:
        return str(s)

    # if type(s) is datetime:
    #     return s.isoformat()

    return s