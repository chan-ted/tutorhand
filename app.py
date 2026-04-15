import os
from flask import Flask , request , render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_folder = os.path.join(os.getcwd(),"database")
db_path = os.path.join(db_folder,"database.db")
os.makedirs(db_folder,exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


practice_topic=db.Table('practice_topic',
    db.Column('practice_id', db.Integer,db.ForeignKey('practices.id'),primary_key=True),
    db.Column('topic_id', db.Integer,db.ForeignKey('topics.id'),primary_key=True)
    )

class Topics(db.Model):
    __tablename__='topics'
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False,unique=True)
    practices=db.relationship('Practices',secondary=practice_topic, back_populates='topics')

class Practices(db.Model):
    __tablename__='practices'
    id=db.Column(db.Integer,primary_key=True)
    questionLink = db.Column(db.String(300),nullable=False)
    answerLink = db.Column(db.String(300),nullable=False)
    topics=db.relationship('Topics',secondary=practice_topic, back_populates='practices')


def preload():
    with app.app_context():
        if Practices.query.first() is None:
            practices_all = [
            Practices(id=1 , questionLink='DSE2026P2Q18.jpg' , answerLink='DSE2026P2Q18-ans.jpg'),
            Practices(id=2 , questionLink='DSE2026P2Q21.jpg' ,  answerLink='DSE2026P2Q21-ans.jpg'),
            Practices(id=3 ,  questionLink='DSE2026P2Q25.jpg' ,  answerLink='DSE2026P2Q25-ans.jpg') 
            ]
            db.session.bulk_save_objects(practices_all)
            db.session.commit()
            print("good practices preload")

        if Topics.query.first() is None:
            topics_all = [
                Topics(id=1,name='ratio'),
                Topics(id=2,name='geometry'),
                Topics(id=3,name='mensuration')
            ]
            db.session.bulk_save_objects(topics_all)
            db.session.commit()
            print('good topics preload')
        def add_link(practice,topic):
            if topic not in practice.topics:
                practice.topics.append(topic)
        p1=Practices.query.get(1)
        p2=Practices.query.get(2)
        p3=Practices.query.get(3)

        t_ratio = Topics.query.get(1)
        t_geom = Topics.query.get(2)
        t_mens = Topics.query.get(3)

        add_link(p1,t_ratio)
        add_link(p1,t_mens)
        add_link(p2,t_ratio)
        add_link(p2,t_geom)
        add_link(p3,t_geom)
        db.session.commit() 
        print("good relationships preload")
        
            

def create_tables():
    with app.app_context():
        db.create_all()
        preload()
        
create_tables()

def filter_practices(allowed_topic_ids):
    allowed_set=set(allowed_topic_ids)
    all_practices = Practices.query.all()
    filtered = []
    for p in all_practices:
        p_topic_ids={t.id for t in p.topics}
        if len(p_topic_ids)>0 and p_topic_ids.issubset(allowed_set):
            filtered.append(p)
    return filtered

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tutor/<id>')
def tutor(id):
    return f'your id is {id}'

@app.route('/search')
def search():
    topicSearch = request.args.get('topic','nothing')
    practices = filter_practices([1,3])
    return render_template('search.html',practices=practices)


@app.route('/result')
def result():
    # .getlist() retrieves all selected values for the name "topic"
    selected_topic_ids = request.args.getlist('topic')
    
    # Convert string IDs (e.g., "1") to integers (e.g., 1)
    topic_ids = [int(tid) for tid in selected_topic_ids]
    
    # Use your existing filter function
    practices = filter_practices(topic_ids)
    
    return render_template('result.html', practices=practices)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)