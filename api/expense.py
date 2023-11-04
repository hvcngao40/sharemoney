from flasgger import swag_from
from flask_restful import reqparse, Resource

from api import ApiException
from config import db
from database import Expense, Member, MemberExpense

expense_parser = reqparse.RequestParser()
expense_parser.add_argument('name', type=str, required=True)
expense_parser.add_argument('date', type=str)
expense_parser.add_argument('count', type=int)
expense_parser.add_argument('created_by', type=int)
expense_parser.add_argument('updated_by', type=int)
expense_parser.add_argument('spent_by', type=int)
expense_parser.add_argument('split_type', type=str)
expense_parser.add_argument('join_members', type=int, action='append')
expense_parser.add_argument('coefficient', type=dict)


def validate_split_type(value):
    valid_statuses = ['default', 'coefficient']
    if value in valid_statuses:
        return value
    else:
        raise ApiException(message='Invalid split_type', status_code=400, payload={'split_type': value})


class ExpenseListResource(Resource):
    @swag_from('../swagger/expense/expense_get_list.yaml')
    def get(self, group_id):
        expenses = Expense.query.filter_by(group_id=group_id).all()
        return {"expenses": [expense.serialize() for expense in expenses]}

    @swag_from('../swagger/expense/expense_post.yaml')
    def post(self, group_id):
        args = expense_parser.parse_args()
        expense = Expense()
        expense.name = args['name']
        expense.date = args['date']
        expense.count = args['count']
        expense.group_id = group_id
        expense.created_by = args['created_by']
        expense.updated_by = args['updated_by']
        expense.spent_by = args['spent_by']
        expense.split_type = validate_split_type(args['split_type'])
        join_members = args['join_members']
        coefficient = args['coefficient']

        if join_members:
            for member_id in join_members:
                member = Member.query.get(member_id)
                expense.members.append(member)
        db.session.add(expense)
        for expense_member in expense.expense_member:
            expense_member.coefficient = coefficient[str(expense_member.member_id)]
        db.session.commit()
        return expense.serialize(), 201


class ExpenseResource(Resource):
    @swag_from('../swagger/expense/expense_get.yaml')
    def get(self, group_id, expense_id):
        expense = Expense.query.get(expense_id)
        if expense is None:
            return {"message": "expense not found"}, 404
        return expense.serialize()

    @swag_from('../swagger/expense/expense_put.yaml')
    def put(self, group_id, expense_id):
        expense = Expense.query.get(expense_id)
        if expense is None:
            return {"message": "expense not found"}, 404
        args = expense_parser.parse_args()
        expense.name = args['name'] if args['name'] else expense.name
        expense.date = args['date'] if args['date'] else expense.date
        expense.count = args['count'] if args['count'] else expense.count
        expense.group_id = group_id
        expense.created_by = args['created_by'] if args['created_by'] else expense.created_by
        expense.updated_by = args['updated_by'] if args['updated_by'] else expense.updated_by
        expense.spent_by = args['spent_by'] if args['spent_by'] else expense.spent_by
        expense.split_type = args['split_type'] if args['split_type'] else expense.split_type
        join_members = args['join_members']
        coefficient = args['coefficient']

        if join_members:
            for i in range(len(join_members)):
                member = Member.query.get(join_members[i])
                check = MemberExpense.query.filter_by(expense_id=expense_id, member_id=join_members[i]).first()
                if not check:
                    expense.members.append(member)

        for expense_member in expense.expense_member:
            expense_member.coefficient = coefficient[str(expense_member.member_id)]
        db.session.commit()
        return expense.serialize()

    @swag_from('../swagger/expense/expense_delete.yaml')
    def delete(self, expense_id):
        expense = Expense.query.get(expense_id)
        if expense is None:
            return {"message": "expense not found"}, 404
        db.session.delete(expense)
        db.session.commit()
        return {"message": "expense deleted"}
