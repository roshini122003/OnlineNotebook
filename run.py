from flask import Flask, render_template, request,redirect,url_for,send_file, make_response
import mysql.connector as sql

app = Flask(__name__, template_folder='templates')
app.config['STATIC_FOLDER'] = 'static'

subjects_list=['Web_Technologies','Data_Analytics','Operating_Systems','Data_Structure']
user_list=['']

def db():
    return sql.connect(
        host='localhost',
        user='root',
        password='',
        database='miniproject'
    )

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/query', methods=['GET', 'POST'])
def handle_question():
    if request.method == 'POST':
        get_query = request.form['query']
        conn = db()
        cursor = conn.cursor()
        query = 'INSERT INTO query_box (question) VALUES (%s)'
        cursor.execute(query, (get_query,))
        conn.commit()
        conn.close()
        return redirect(url_for("display_queries"))

@app.route("/submit_answer", methods=["POST"])
def handle_answer():
    get_answer = request.form['answer']
    qid = request.form['qid'] 
    conn = db()
    cursor = conn.cursor()
    answer = "UPDATE query_box SET answer='{a}' WHERE qid='{b}'".format(a=get_answer,b=qid)
    cursor.execute(answer)
    conn.commit()
    conn.close()
    return redirect(url_for("display_queries"))

@app.route("/question")
def display_queries():
    conn=db()
    cursor=conn.cursor()
    query='select * from query_box  order by qid  LIMIT 10'
    cursor.execute(query)
    res=cursor.fetchall()
    return render_template("question.html",queries=res)

@app.route("/submit_file",methods=["POST"])
def submit_file():
    try:
        conn = db()
        cursor = conn.cursor()
        get_file = request.files['notes']
        get_subject = request.form['subject']
        get_upload_type = request.form['upload_type']
        file_name = get_file.filename
        mime_type = get_file.mimetype
        data = get_file.read()
        query = "INSERT INTO file (filename,mimetype,filetype,subject,file) VALUES (%s, %s, %s,%s, %s)"
        cursor.execute(query, (file_name, mime_type,get_upload_type,get_subject, data))
        conn.commit()
        conn.close()
        return 'Successful!'
    except Exception as e:
        return "Error occurred: " + str(e)

@app.route("/file/<subject>")
def get_all_files(subject):
    query='select filename from file where subject="{sub_name}"'.format(sub_name=subject)
    conn=db()
    cursor=conn.cursor()
    cursor.execute(query)
    records=cursor.fetchall()
    files=[row[0]for row in records]
    return render_template("files.html",files=files)


@app.route("/subject")
def index():
    subjects=subjects_list
    return render_template("subject.html",subjects=subjects)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        query='INSERT INTO login(uname,password)VALUES("{username}","{password}")'.format(username=username,password=password)
        conn=db()
        cursor=conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        un=request.form['username']
        pwd=request.form['password']
        query="SELECT password from login where uname='{}'".format(un)
        conn=db()
        cursor=conn.cursor()
        cursor.execute(query)
        result=cursor.fetchone()
        if result and pwd==result[0]:
            global user_list
            user_list.append(un)
            return redirect(url_for("gohome"))
            
        else:
            return "Incorrect Password"
    else:
        return render_template('login.html')
        
@app.route("/download/<file>")
def sendfile(file):
    conn=db()
    cursor=conn.cursor()
    query='SELECT file from file where filename="{}"'.format(file)
    cursor.execute(query)
    res_file=cursor.fetchone()
    return send_file(res_file, as_attachment=False, download_name=file)

@app.route("/home")
def gohome():
    global user_list
    user=user_list[-1]
    return render_template("index.html",user=user)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/logout")
def logout():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)