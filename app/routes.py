from flask import Blueprint, render_template, request, redirect, url_for
from .forms import MyForm

my_blueprint = Blueprint('my_blueprint', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@my_blueprint.route('/form', methods=['GET', 'POST'])
def form():
    form = MyForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Process the form data
        return redirect(url_for('my_blueprint.success'))
    return render_template('form.html', form=form)

@my_blueprint.route('/success')
def success():
    return render_template('success.html')
