from flask import Flask
app = Flask(__name__)

db = {}

@app.route('/put/<id>/<flag>')
def put(id, flag):
    print("PUT", id, flag)
    db[id] = flag
    return 'OK'

@app.route('/get/<id>')
def get(id):
    print("GET", id)
    if id in db:
        return db[id]
    return 'HUJ'

if __name__ == "__main__":
    app.run(host='0.0.0.0')

