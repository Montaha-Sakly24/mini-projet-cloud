from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import redis

app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'admin')}@{os.getenv('DB_HOST', 'db')}:5432/tasks"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Redis cache
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    # Check cache first
    cached = redis_client.get('tasks')
    if cached:
        return jsonify(eval(cached))
    
    tasks = Task.query.all()
    result = [{"id": t.id, "title": t.title, "done": t.done} for t in tasks]
    redis_client.set('tasks', str(result), ex=60)  # cache 60 seconds
    return jsonify(result)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    task = Task(title=data['title'], done=data.get('done', False))
    db.session.add(task)
    db.session.commit()
    redis_client.delete('tasks')  # clear cache
    return jsonify({"id": task.id, "title": task.title, "done": task.done}), 201

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        redis_client.delete('tasks')  # clear cache
        return jsonify({"message": "Task deleted"})
    return jsonify({"message": "Task not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)