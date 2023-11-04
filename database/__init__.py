from config import db
from sqlalchemy.orm import relationship


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    group_type = db.Column(db.String(200))
    currency = db.Column(db.String(10))
    link = db.Column(db.String(100))
    members = relationship("Member", backref='group', cascade="all, delete")
    expenses = relationship("Expense", backref='group', cascade="all, delete")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'group_type': self.group_type,
            'currency': self.currency,
            'link': self.link,
            'members': [member.serialize() for member in self.members],
            'expenses': [expense.serialize() for expense in self.expenses]
        }


class MemberExpense(db.Model):
    __tablename__ = 'member_expense'

    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete="CASCADE"), primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id', ondelete="CASCADE"), primary_key=True)
    coefficient = db.Column(db.Float, default=1.0)

    member = db.relationship("Member", backref=db.backref("member_expense", lazy='dynamic'))
    expense = db.relationship("Expense", backref=db.backref("expense_member", lazy='dynamic'))


class Member(db.Model):
    __tablename__ = 'member'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete="CASCADE"), index=True)
    is_host = db.Column(db.Boolean)
    is_active_member = db.Column(db.Boolean)

    def serialize(self, money=None):
        if not money:
            money = 0
            for expense in self.expenses:
                dict_amount = expense.get_dict_amount_by_member()
                amount_to_pay = dict_amount[self.id]
                money += amount_to_pay

        return {
            'id': self.id,
            'name': self.name,
            'group_id': self.group_id,
            'is_host': self.is_host,
            'is_active_member': self.is_active_member,
            'money': money
        }


class Expense(db.Model):
    __tablename__ = 'expense'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime)
    count = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('member.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('member.id'))
    spent_by = db.Column(db.Integer, db.ForeignKey('member.id'))
    split_type = db.Column(db.Enum('default', 'coefficient', name='split_type'))
    members = relationship('Member', secondary=MemberExpense.__tablename__, backref='expenses', cascade="all, delete")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)

    def get_dict_amount_by_member(self):
        generator_dict = ({item.member_id: item.coefficient} for item in self.expense_member)
        dict_coefficient = {key: value for item in generator_dict for key, value in item.items()}
        total_coefficient = sum(value for value in dict_coefficient.values())
        dict_amount_by_member = {}

        for member in self.members:
            coefficient = dict_coefficient.get(member.id, 1.0)
            amount_to_pay = self.count * coefficient/total_coefficient
            dict_amount_by_member[member.id] = amount_to_pay
        return dict_amount_by_member

    def serialize(self):
        dict_amount_by_member = self.get_dict_amount_by_member()

        return {
            'id': self.id,
            'name': self.name,
            'date': str(self.date),
            'count': self.count,
            'created_by': self.created_by,
            'spent_by': self.spent_by,
            'split_type': self.split_type,
            'members': [member.serialize(dict_amount_by_member[member.id]) for member in self.members],
            'group_id': self.group_id
        }


