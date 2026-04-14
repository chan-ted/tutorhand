from flask import Flask , request

app = Flask(__name__)

@app.route('/')
def home():
    return 'tutorhand'

@app.route('/tutor/<id>')
def tutor(id):
    return f'your id is {id}'

@app.route('/search')
def search():
    topicSearch = request.args.get('topic','nothing')
    return f'you searched for {topicSearch}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)