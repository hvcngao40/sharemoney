from flasgger import swag_from
from flask_restful import reqparse, Resource

from config import db
from database import Group


group_parser = reqparse.RequestParser()
group_parser.add_argument('name', type=str, required=True)
group_parser.add_argument('group_type', type=str)
group_parser.add_argument('currency', type=str)
group_parser.add_argument('link', type=str)


class GroupListResource(Resource):
    @swag_from('../swagger/group/group_get_list.yaml')  # Áp dụng Swagger YAML cho phương thức GET
    def get(self):
        groups = Group.query.all()
        return {"groups": [group.serialize() for group in groups]}

    @swag_from('../swagger/group/group_post.yaml')  # Áp dụng Swagger YAML cho phương thức POST
    def post(self):
        # Lấy thông tin về nhóm từ request
        data = group_parser.parse_args()
        name = data.get("name")
        group_type = data.get("group_type")
        currency = data.get("currency")
        link = data.get("link")

        # Tạo một nhóm mới
        group = Group(name=name, group_type=group_type, currency=currency, link=link)
        db.session.add(group)
        db.session.commit()

        return {"message": "Group created successfully"}


class GroupResource(Resource):
    @swag_from('../swagger/group/group_get.yaml')  # Áp dụng Swagger YAML cho phương thức GET
    def get(self, group_id=None):
        if not group_id:
            groups = Group.query.all()
            return {"groups": [group.serialize() for group in groups]}
        else:
            group = Group.query.get(group_id)
            if not group:
                return {"message": "Group not found"}, 404
            return group.serialize()

    @swag_from('../swagger/group/group_put.yaml', endpoint='put')  # Áp dụng Swagger YAML cho phương thức PUT
    def put(self, group_id):
        # Lấy thông tin về nhóm từ request
        data = group_parser.parse_args()
        name = data.get("name")
        group_type = data.get("group_type")
        currency = data.get("currency")
        link = data.get("link")

        # Cập nhật thông tin nhóm trong CSDL
        group = Group.query.get(group_id)
        if not group:
            return {"message": "Group not found"}, 404

        group.name = name
        group.group_type = group_type
        group.currency = currency
        group.link = link
        db.session.commit()

        return {"message": "Group updated successfully"}

    @swag_from('../swagger/group/group_delete.yaml', endpoint='delete')  # Áp dụng Swagger YAML cho phương thức DELETE
    def delete(self, group_id):
        # Xóa nhóm trong CSDL
        group = Group.query.get(group_id)
        if not group:
            return {"message": "Group not found"}, 404

        db.session.delete(group)
        db.session.commit()

        return {"message": "Group deleted successfully"}
