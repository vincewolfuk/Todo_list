from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__)) 
os.makedirs(os.path.join(basedir, 'db'), exist_ok=True)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db/sqlite4.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {'done': 'sqlite:///' + os.path.join(basedir, 'db/done.db')}

db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    assigned_by = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):        
        return f'<Todo {self.id}>'
    
class Donetask(db.Model):
    __bind_key__ = 'done'
    __tablename__ = 'donetask'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    assigned_by = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    original_date_created = db.Column(db.DateTime)
    todo_id = db.Column(db.Integer)

with app.app_context():
    db.create_all()  # Creates 'todo' in sqlite4.db
    db.create_all(bind_key='done')


    def __repr__(self):        
        return f'<Donetask  {self.id}>'    
    
     
@app.route('/', methods=['POST','GET'])
def indef():
    if request.method == 'POST':
        task_content = request.form['content'].strip()
        task_assigned = request.form['assigned_by'].strip()

        if not task_content:
            flash('Task content cannot be empty!')
            return redirect('/')

        if not task_assigned:
            flash('Please add who assined it!')
            return redirect('/')

        new_task = Todo(content=task_content, assigned_by=task_assigned)

        try:
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!')
            return redirect('/')
        except:
            return 'There was an issue adding your task'
            
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.assigned_by = request.form['assigned_by']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem updating that task'
    else:
        return render_template('update.html', task=task)
    
@app.route('/done/<int:id>')
def done(id):
    task_to_save = Todo.query.get_or_404(id)    
    done_task = Donetask(content=task_to_save.content, assigned_by=task_to_save.assigned_by, original_date_created=task_to_save.date_created, todo_id=task_to_save.id)

    try:
        db.session.add(done_task)       
        db.session.delete(task_to_save)
        db.session.commit()

        flash('Task saved successfully!')
        return redirect('/')
    except IntegrityError as e:  # Catch IntegrityError specifically        
        db.session.rollback()
        return f'There was an issue saving your task: {e}' 

    except SQLAlchemyError as e:  # Catch SQLAlchemyError specificall        
        db.session.rollback()
        return f'There was an issue deleting your task: {e}' 

    except Exception as e:  # Catch any other exception (general error)        
        db.session.rollback()
        return f'An unexpected error occurred: {e}' 
    


@app.route('/done_tasks') 
def done_task():
    done_task = Donetask.query.order_by(Donetask.date_created).all()
    return render_template('done.html', done_task=done_task)


if __name__ == "__main__":
    app.run(debug=True)  # Start the Flask development server