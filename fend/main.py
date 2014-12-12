from flask import Flask, request, jsonify
from mongoengine import ValidationError
from mongoengine.queryset import DoesNotExist
from models import Project, Author

app = Flask(__name__)

@app.route('/projects', methods=['POST'])
def create_project():
    json = request.get_json()

    if json.get('author_id') is not None:
        Author.objects(id=json['author_id']).get()

    project = Project(**json)
    project.save()

    return project.to_json(), 201


@app.route('/projects')
def get_projects():
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    offset = (page - 1) * per_page

    projects = Project.objects[offset:per_page]

    return projects.to_json()


@app.route('/projects/<project_id>')
def get_project_details(project_id):
    project = Project.objects(id=project_id).get()

    return project.to_json()


@app.route('/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    pass


@app.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.objects(id=project_id).get()
    project.delete()

    return project.to_json()



@app.errorhandler(ValidationError)
def handle_validation_error(error):
    errors = [dict(field=key, message=value) for key, value in error.to_dict().iteritems()]
    message = 'Validation Error' if len(errors) > 0 else error.message
    return jsonify(message=message, errors=errors), 422

@app.errorhandler(DoesNotExist)
def handle_does_not_exist(error):
    return jsonify(error=error.message), 404
