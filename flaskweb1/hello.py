import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import  datetime
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))    # 获取当前文件夹的（项目）的绝对路径

app = Flask(__name__)
app.config['SECRET_KEY'] = "hard to guess string"
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')     # 程序时用的数据库URL必须保存到Flask配置对象的SQLALCHEMY_DATABASE_URI键中
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True      # 将SQLALCHEMY_COMMIT_ON_TEARDOWN设置为True，每次请求结束后都自动提交数据库的变动
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager = Manager(app)  # 此处不配置进入不了shell模式
bootstrap = Bootstrap(app)
moment = Moment(app)    # 时间处理
db = SQLAlchemy(app)      # 数据库


# 定义模型
class Role(db.Model):
    __tablename__ = 'roles'     # 定义表名称
    id = db.Column(db.Integer, primary_key=True)    # 定义id列属性为整型，主键
    name = db.Column(db.String(64), unique=True)    # 定义name属性为6长度64的字符串 不可重复
    users = db.relationship('User', backref='role')     # users属性返回与角色关联的用户组成的列表 backref向User模型中添加一个role属性，从而半箱定义关系

    def __repr__(self):
        return '<Role %r>' % self.name       # 该方法返回一个具有可读性的字符串表示模型


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)    # index设置为True 为这列设置索引提高查询
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# 定义表单类
class NameForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])    # 相当于type为text的input DataRequires确保有数据
    submit = SubmitField('Submit')      # 相当于type为submit的input


# methods参数告诉flask在url映射中把这个视图函数注册为GET和POST请求的处理程序，如果没有这个参数，默认为GET请求
@app.route('/', methods=['GET', 'POST'])
def index():
    # return render_template('index.html')
    # name = None
    form = NameForm()
    # 提交表单后，如果数据能被所有验证函数接受，那么validate_on_submit方法返回True，否则返回False
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data    # 将用户输入的姓名存储在session
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return  render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
