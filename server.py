import flask
from flask import jsonify, request
from flask.views import MethodView
from models import User, Advertisment, Session
from sqlalchemy.exc import IntegrityError
import json


app = flask.Flask("app")


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    http_response = jsonify({"status": "error", "message": error.message})
    http_response.status = error.status_code
    return http_response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(http_response: flask.Response):
    request.session.close()
    return http_response


def add_to_session(obj):
    try:
        request.session.add(obj)
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, f"{obj.__class__.__name__} error")
    return obj


def get_from_session(model, obj_id):
    obj = request.session.get(model, obj_id)
    if obj is None:
        raise HttpError(404, f"{model.__name__} not found")
    return obj


class BaseView(MethodView):

    model = None

    def get(self, obj_id: int):
        obj = get_from_session(self.model, obj_id)
        return json.dumps(obj.json, ensure_ascii=False)

    def post(self):
        json_data = request.json
        obj = self.model(**json_data)
        obj = add_to_session(obj)
        return json.dumps(obj.json, ensure_ascii=False)

    def patch(self, obj_id: int):
        obj = get_from_session(self.model, obj_id)
        json_data = request.json
        for key, value in json_data.items():
            setattr(obj, key, value)
        obj = add_to_session(obj)
        return json.dumps(obj.json, ensure_ascii=False)

    def delete(self, obj_id: int):
        obj = get_from_session(self.model, obj_id)
        request.session.delete(obj)
        request.session.commit()
        return jsonify({"status": "deleted"})


class UserView(BaseView):
    model = User


class AdvertismentView(BaseView):
    model = Advertisment


user_view = UserView.as_view("user")
advertisment_view = AdvertismentView.as_view("advertisment")

if __name__ == "__main__":

    app.add_url_rule("/user/", view_func=user_view, methods=['POST'])
    app.add_url_rule('/user/<int:obj_id>/', view_func=user_view,
                     methods=['GET', 'PATCH', 'DELETE'])
    app.add_url_rule("/advertisment/", view_func=advertisment_view,
                     methods=['POST']
                     )
    app.add_url_rule("/advertisment/<int:obj_id>/",
                     view_func=advertisment_view,
                     methods=['GET', 'PATCH', 'DELETE'])

    app.run()
