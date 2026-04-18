import os
from flask import Flask , request , render_template ,send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from supabase import create_client

app = Flask(__name__)

db_folder = os.path.join(os.getcwd(),"database")
db_path = os.path.join(db_folder,"database.db")
os.makedirs(db_folder,exist_ok=True)
db_uri=os.environ.get("DATABASE_URL")
key=os.environ.get("SUPABASE_KEY")
UPLOAD_FOLDER='uploads'

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
# = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-local')
supabase = create_client(url, key)


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

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method=='POST':
        q_file=request.files['question_file']
        a_file=request.files['answer_file']
        q_filename=secure_filename(q_file.filename)
        a_filename=secure_filename(a_file.filename)
        # q_file.save(os.path.join(app.config['UPLOAD_FOLDER'],q_filename))
        # a_file.save(os.path.join(app.config['UPLOAD_FOLDER'],a_filename))

        supabase.storage.from_("practices").upload(
                path=q_filename,
                file=q_file.read() , 
                file_options={"content-type":q_file.content_type}
            )
        a_file.seek(0)
        supabase.storage.from_("practices").upload(
                path=a_filename,
                file=a_file.read() , 
                file_options={"content-type":a_file.content_type}
            )

        public_url_q = supabase.storage.from_("practices").get_public_url(q_filename)
        public_url_a  = supabase.storage.from_("practices").get_public_url(a_filename)
        new_practice=Practices(questionLink=public_url_q,answerLink=public_url_a)
        selected_topic_ids = request.form.getlist('topics')
        for tid in selected_topic_ids:
            topic = Topics.query.get(int(tid))
            new_practice.topics.append(topic)
        db.session.add(new_practice)
        db.session.commit()
        return "uploaded! <a href='/upload'>back</a>"        
    allTopics = Topics.query.all()
    return render_template('upload.html', all_topics=allTopics)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)



@app.route('/delete')
def delete():
    practices = Practices.query.all()   
    return render_template('delete.html', practices=practices)

@app.route('/delete/<int:id>')
def delete_practice(id):
    practice_delete = Practices.query.get_or_404(id)
    #try:
    #    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], practice.questionLink))
    #    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], practice.answerLink))
    #except:
    #    pass
    db.session.delete(practice_delete)
    db.session.commit()
    return ("deleted!  <a href='/delete'></a>")
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)