from flask_restful import Api
from flasgger import Swagger

from api.expense import ExpenseResource, ExpenseListResource
from api.group import GroupResource, GroupListResource
from api.member import MemberResource, MemberListResource
from config import app, db

swagger = Swagger(app)
api = Api(app)
api.add_resource(GroupListResource, '/group')
api.add_resource(GroupResource, '/group/<int:group_id>')
api.add_resource(MemberListResource, '/group/<int:group_id>/member')
api.add_resource(MemberResource, '/group/<int:group_id>/member/<int:member_id>')
api.add_resource(ExpenseListResource, '/group/<int:group_id>/expense')
api.add_resource(ExpenseResource, '/group/<int:group_id>/expense/<int:expense_id>')

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(port=5000)
