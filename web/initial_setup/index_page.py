import flask

# A simple Flask App which takes
# a user's name as input and responds
# with "Hello {name}!"

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def get_part_of_day(h):
    return (
        "morning"
        if 5 <= h <= 11
        else "afternoon"
        if 12 <= h <= 17
        else "evening"
        if 18 <= h <= 22
        else "night"
    )

def index():
    # To use current hour:
    from datetime import datetime
    part = get_part_of_day(datetime.now().hour)
    message = f"Good {part}! Welcome to our project Presentation!"
    #if flask.request.method == 'POST':
    #    message = 'Hello ' + flask.request.form['name-input'] + '!'
    return flask.render_template('index.html', message=message)

if __name__ == '__main__':
    app.run()