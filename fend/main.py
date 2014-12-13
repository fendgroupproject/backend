from flask import Flask, request, jsonify, url_for
from itertools import chain
from mongoengine import ValidationError
from mongoengine.queryset import DoesNotExist
from models import Project, Author

app = Flask(__name__)


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'GET':
        return paginate(resource_name='projects', view_func_name='projects', get_objects_func=lambda: Project.objects)

    json = request.get_json()
    assert_author_exists(json.get('author_id'))

    project = Project(**json)
    project.save()
    Author.objects(id=project.author_id).update_one(push__projects=project.id)

    return jsonify(project.to_dict()), 201


@app.route('/projects/<project_id>')
def get_project(project_id):
    return jsonify(Project.objects(id=project_id).get().to_dict())


@app.route('/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    # Project.objects(id=project_id).update_one(**dict([('set__' + key, value) for key, value in json.iteritems()]))
    project = Project.objects(id=project_id).get()
    updated = Project(**dict(chain(project.to_dict().items(), request.get_json().items())))
    updated.save()

    return jsonify(updated.to_dict())


@app.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.objects(id=project_id).get()
    project.delete()

    Author.objects(id=project.author_id).update_one(pull__projects=project.id)

    return jsonify(project.to_dict())


@app.route('/authors', methods=['GET', 'POST'])
def authors():
    if request.method == 'GET':
        return paginate(resource_name='authors', view_func_name='authors', get_objects_func=lambda: Author.objects)

    author = Author(**request.get_json())
    author.save()

    return jsonify(author.to_dict()), 201


@app.route('/authors/<author_id>', methods=['GET'])
def get_author(author_id):
    return jsonify(Author.objects(id=author_id).get().to_dict())


@app.route('/authors/<author_id>', methods=['PUT'])
def update_author(author_id):
    author = Author.objects(id=author_id).get()
    updated = Author(**dict(chain(author.to_dict().items(), request.get_json().items())))
    updated.save()

    return jsonify(updated.to_dict())


@app.route('/authors/<author_id>', methods=['DELETE'])
def delete_author(author_id):
    author = Author.objects(id=author_id).get()
    for project_id in author.projects:
        delete_project(project_id)

    author.delete()

    return jsonify(author.to_dict())


def assert_author_exists(author_id):
    if author_id is not None:
        Author.objects.get(id=author_id)


def paginate(resource_name, view_func_name, get_objects_func):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page

    objects = get_objects_func()
    paginated_objects = objects.skip(offset).limit(per_page)

    objects_count = objects.count()
    paginated_objects_count = paginated_objects.count()

    metadata = dict(page=page, per_page=per_page, page_count=paginated_objects_count, total_count=objects_count)
    metadata['links'] = dict(self=url_for(view_func_name, page=page, per_page=per_page))

    if page > 1:
        metadata['links']['prev'] = url_for(view_func_name, page=page - 1, per_page=per_page)
        metadata['links']['first'] = url_for(view_func_name, page=1, per_page=per_page)

    if page * per_page < objects_count:
        metadata['links']['next'] = url_for(view_func_name, page=page + 1, per_page=per_page)

        last_page = objects_count / per_page
        if objects_count % per_page > 0:
            last_page += 1

        metadata['links']['last'] = url_for(view_func_name, page=last_page, per_page=per_page)

    return jsonify({'metadata': metadata, resource_name: [obj.to_dict() for obj in paginated_objects]})


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    errors = [dict(field=key, message=value) for key, value in error.to_dict().iteritems()]
    message = 'Validation Error' if len(errors) > 0 else error.message

    return jsonify(message=message, errors=errors), 422


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(error):
    return jsonify(error=error.message), 404

@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify(error='error parsing JSON'), 400
