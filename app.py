from flask import Flask , request , render_template

app = Flask(__name__)

@app.route('/')
def home():
    questions = [
        {'id':1 , 'questionLink':'DSE2026P2Q18.jpg' , 'answerLink':'DSE2026P2Q18-ans.jpg'},
        {'id':2 , 'questionLink':'DSE2026P2Q21.jpg' ,  'answerLink':'DSE2026P2Q21-ans.jpg'},
        {'id':3 ,  'questionLink':'DSE2026P2Q25.jpg' ,  'answerLink':'DSE2026P2Q25-ans.jpg'} 
     ]
    return render_template('index.html',questions=questions)

@app.route('/tutor/<id>')
def tutor(id):
    return f'your id is {id}'

@app.route('/search')
def search():
    topicSearch = request.args.get('topic','nothing')
    return f'you searched for {topicSearch}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)