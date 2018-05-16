import os
from flask import Flask, render_template, session, redirect, url_for
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import  datetime
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))    # 获取当前文件夹的（项目）的绝对路径

app = Flask(__name__)
app.config['SECRET_KEY'] = "hard to guess string"
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite?check_same_thread=False')     # 程序时用的数据库URL必须保存到Flask配置对象的SQLALCHEMY_DATABASE_URI键中
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True      # 将SQLALCHEMY_COMMIT_ON_TEARDOWN设置为True，每次请求结束后都自动提交数据库的变动
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 配置flask-mail使用163邮箱
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'laobahepijiu@163.com'
app.config['MAIL_PASSWORD'] = 'DHZ19960618'   # 从环境变量中读取邮箱账号和密码
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <laobahepijiu@163.com>'
app.config['FLASKY_ADMIN'] = 'zyrebecca96@163.com'


manager = Manager(app)  # 此处不配置进入不了shell模式
bootstrap = Bootstrap(app)
moment = Moment(app)    # 时间处理
db = SQLAlchemy(app)      # 数据库
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)

# 定义模型
class Role(db.Model):
    __tablename__ = 'roles'     # 定义表名称
    id = db.Column(db.Integer, primary_key=True)    # 定义id列属性为整型，主键
    name = db.Column(db.String(64), unique=True)    # 定义name属性为6长度64的字符串 不可重复
    # users属性返回与角色关联的用户组成的列表 backref向User模型中添加一个role属性，从而反向定义关系 lazy设置为dynamic从而禁止自动查询
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name       # 该方法返回一个具有可读性的字符串表示模型


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)    # index设置为True 为这列设置索引提高查询
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# 让Flask-Script的shell命令自动导入特定的对象，需要为shell命令注册一个make_context回调函数
# make_shell_context()函数注册了程序、数据库实例以及模型

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


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
        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
            # flash('Looks like you have changed your name!')
        user = User.query.filter_by(username=form.name.data).first()    # 查找用户提交的名字
        if user is None:    # 查找不到则为新用户
            user = User(username=form.name.data, role_id=3)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data    # 将用户输入的姓名存储在session
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'), known=session.get('known', False))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return  render_template('500.html'), 500


if __name__ == '__main__':
    manager.run()
    app.run(debug=True)
