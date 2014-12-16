from flask import Flask, request, jsonify, url_for
from itertools import chain
from mongoengine import ValidationError
from mongoengine.queryset import DoesNotExist
from models import Project, Author

app = Flask(__name__)


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    """Retrieves a list of projects from the database or create a new project.
    When retrieving a list of projects, the URL can contain pagination parameters
    page and per_page which default respectively to 1 and 10 if omitted.
    """
    if request.method == 'GET':
        return paginate(resource_name='projects', endpoint='projects', objects=Project.objects)

    json = request.get_json()

    author_id = json.get('author_id')
    if author_id is not None:
        assert_author_exists(json.get('author_id'))

    project = Project(**json)
    project.save()

    # Add the project in the list of the author projects.
    Author.objects(id=project.author_id).update_one(push__projects=project.id)

    return jsonify(project.to_dict()), 201


@app.route('/projects/<project_id>')
def get_project(project_id):
    """Retrieves the project matching the id project_id."""
    return jsonify(Project.objects(id=project_id).get().to_dict())


@app.route('/projects/<project_id>', methods=['PATCH'])
def update_project(project_id):
    """Updates the project matching the id project_id.
    Only the parameters to update or to add should be passed in the request body.
    """
    project = Project.objects(id=project_id).get()
    patched = Project(**dict(chain(project.to_dict().items(), request.get_json().items())))
    patched.save()

    return jsonify(patched.to_dict())


@app.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Deletes the project matching the id project_id."""
    project = Project.objects(id=project_id).get()
    project.delete()

    # Removes the project from the list of the author projects.
    Author.objects(id=project.author_id).update_one(pull__projects=project.id)

    return jsonify(project.to_dict())


@app.route('/authors', methods=['GET', 'POST'])
def authors():
    """Retrieves a list of authors from the database or create a new author.
    When retrieving a list of authors, the URL can contain pagination parameters
    page and per_page which default to 1 and 10 if omitted.
    """
    if request.method == 'GET':
        return paginate(resource_name='authors', endpoint='authors', objects=Author.objects)

    author = Author(**request.get_json())
    author.save()

    return jsonify(author.to_dict()), 201


@app.route('/authors/<author_id>')
def get_author(author_id):
    """Retrieves the author matching the id author_id."""
    return jsonify(Author.objects(id=author_id).get().to_dict())


@app.route('/authors/<author_id>', methods=['PATCH'])
def update_author(author_id):
    """Updates the author matching the id author_id.
    Only the parameters to update or to add should be passed in the request body.
    """
    author = Author.objects(id=author_id).get()
    patched = Author(**dict(chain(author.to_dict().items(), request.get_json().items())))
    patched.save()

    return jsonify(patched.to_dict())


@app.route('/authors/<author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Deletes the author matching the id author_id."""
    author = Author.objects(id=author_id).get()

    # Deletes all the projects of this author.
    for project_id in author.projects:
        delete_project(project_id)

    author.delete()

    return jsonify(author.to_dict())


@app.route('/authors/<author_id>/projects', methods=['GET'])
def get_author_projects(author_id):
    """Retrieves a list of projects created by the author matching the id author_id.
    Pagination parameters page and per_page can be passed in the URL. They default
    respectively to 1 and 10 if omitted.
    """
    return paginate(resource_name='projects', endpoint='get_author_projects',
                    objects=Project.objects(author_id=author_id),
                    endpoint_params={'author_id': author_id})


def assert_author_exists(author_id):
    """Asserts that an author matching the id author_id exists.
    If such an author does not exist, the exception Author.DoesNotExist
    will be raised."""
    Author.objects.get(id=author_id)


def paginate(resource_name, endpoint, objects, endpoint_params={}):
    """Retrieves a subset of `objects`. Uses the `page` and `per_page` parameters
    passed in the URL to perform pagination. `(page - 1) * per_page` elements
    are skipped and the result is limited to `per_page` elements.
    Also builds and inserts pagination links in the response.

    :param resource_name: the name of the resource to retrieve.
    :param endpoint: the name of the function handling the GET request.
    :param objects: the list of database documents to paginate.
    :param endpoint_params: dict of other necessary URL parameters other than page and per_page. This
        parameter is necessary for building the pagination links.
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page

    def url(page_num, page_count):
        """Returns the URL for `endpoint` where `page = page_num` and `per_page = page_count`."""
        return url_for(endpoint, **dict(chain({'page': page_num, 'per_page': page_count}.items(),
                                              endpoint_params.items())))

    paginated_objects = objects.skip(offset).limit(per_page)

    objects_count = objects.count()
    paginated_objects_count = paginated_objects.count()

    # The pagination links are embedded in an object `metadata`.
    metadata = dict(page=page, per_page=per_page, page_count=paginated_objects_count, total_count=objects_count)
    metadata['links'] = dict(self=url(page, per_page))

    if page > 1:
        metadata['links']['prev'] = url(page - 1, per_page)
        metadata['links']['first'] = url(1, per_page)

    if page * per_page < objects_count:
        metadata['links']['next'] = url(page + 1, per_page)

        last_page = objects_count / per_page
        if objects_count % per_page > 0:
            last_page += 1

        metadata['links']['last'] = url(last_page, per_page)

    return jsonify({'metadata': metadata, resource_name: [obj.to_dict() for obj in paginated_objects]})


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    errors = [dict(field=key, message=value) for key, value in error.to_dict().iteritems()]
    message = 'Validation Error' if len(errors) > 0 else error.message

    return jsonify(message=message, errors=errors), 422


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(error):
    return jsonify(error=error.message), 404


@app.errorhandler(ValueError)
def handle_value_error(error):
    return jsonify(error='wrong url parameter type'), 400


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify(error='error parsing JSON'), 400
