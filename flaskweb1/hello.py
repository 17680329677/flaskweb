from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import  datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = "hard to guess string"
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


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
