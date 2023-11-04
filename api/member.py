from flasgger import swag_from
from flask_restful import reqparse, Resource

from config import db
from database import Member


member_parser = reqparse.RequestParser()
member_parser.add_argument('name', type=str, required=True)
member_parser.add_argument('is_host', type=bool)
member_parser.add_argument('is_active_member', type=bool)


class MemberListResource(Resource):
    @swag_from('../swagger/member/member_get_list.yaml')
    def get(self, group_id):
        members = Member.query.filter_by(group_id=group_id).all()
        return {"members": [member.serialize() for member in members]}

    @swag_from('../swagger/member/member_post.yaml')
    def post(self, group_id):
        # Lấy thông tin về thành viên từ request
        data = member_parser.parse_args()
        name = data.get("name")
        is_host = data.get("is_host")
        is_active_member = data.get("is_active_member")

        # Tạo một thành viên mới trong nhóm
        member = Member(name=name, group_id=group_id, is_host=is_host, is_active_member=is_active_member)
        db.session.add(member)
        db.session.commit()

        return {"message": "Member created successfully"}


class MemberResource(Resource):
    @swag_from('../swagger/member/member_get.yaml')
    def get(self, group_id, member_id):
        member = Member.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return {"message": "Member not found"}, 404
        return member.serialize()

    @swag_from('../swagger/member/member_put.yaml')
    def put(self, group_id, member_id):
        # Lấy thông tin về thành viên từ request
        data = member_parser.parse_args()
        name = data.get("name")
        is_host = data.get("is_host")
        is_active_member = data.get("is_active_member")

        # Cập nhật thông tin thành viên trong CSDL
        member = Member.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return {"message": "Member not found"}, 404

        member.name = name
        member.is_host = is_host
        member.is_active_member = is_active_member
        db.session.commit()

        return {"message": "Member updated successfully"}

    @swag_from('../swagger/member/member_delete.yaml')
    def delete(self, group_id, member_id):
        # Xóa thành viên khỏi nhóm trong CSDL
        member = Member.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return {"message": "Member not found"}, 404

        db.session.delete(member)
        db.session.commit()

        return {"message": "Group deleted successfully"}
