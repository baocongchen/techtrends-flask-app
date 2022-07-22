import sqlite3
from flask import Flask, logging, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys
import logging

# Function to get a database connection.
# This function connects to database with the name `database.db`


def get_db_connection():
    global concurrent_connections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    concurrent_connections += 1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Initialize global variable that stores count of concurrent connections
concurrent_connections = 0

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error('Error: 404; Post with id ' +
                         str(post_id) + ' does not exist')
        return render_template('404.html'), 404
    else:
        title = post[2]
        app.logger.info('Article "' + title + '" retrieved!')
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    app.logger.info('About Us page is retrieved')
    return render_template('about.html')

# Define the Healthcheck endpoint


@app.route('/healthz')
def health_check():
    try:
        connection = get_db_connection()
        posts = connection.execute(
            'SELECT count(id) FROM posts').fetchall()[0][0]
        print(posts)
        connection.close()
        if int(posts) > 0:
            response = jsonify({"status": 200, "result": "OK - healthy"})
            return response
        else:
            response = jsonify({"status": 500, "result": "ERROR - unhealthy"})
            return response

    except:
        response = jsonify({"status": 500, "result": "ERROR - unhealthy"})
        return

# Define the Metrics endpoint


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()[0][0]
    connection.close()
    return jsonify({"db_connection_count": concurrent_connections, "post_count": len(posts)})


# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            app.logger.info('Article \"' + title + '\" is created')
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    # Setup logging
    log_level = logging.DEBUG
    app.logger.setLevel(log_level)
    werkzeug_logger = logging.getLogger('werkzeug')
    _format = '%(levelname)s:%(name)s:%(asctime)s, %(message)s'
    formatter = logging.Formatter(_format)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    file_handler = logging.FileHandler('app.log')

    stdout_handler.setLevel(log_level)
    stderr_handler.setLevel(logging.ERROR)
    file_handler.setLevel(log_level)
    werkzeug_logger.setLevel(logging.INFO)

    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    app.logger.addHandler(stderr_handler)
    app.logger.addHandler(stdout_handler)
    app.logger.addHandler(file_handler)
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(stdout_handler)
    app.run(port=3111, debug=True)
