from flask import Flask,render_template,request,redirect,url_for,session
import os
import pandas as pd
from datetime import datetime

app=Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

   

@app.route('/')
def home():
    return render_template('login.html')

def dashboard_load_data():
    lp_rel_path="/data/learnpgm.csv"
    lp_path=os.getcwd()+lp_rel_path
    with open(lp_path,"r") as f:
        data=f.readlines()[1:]
    lp_rows=[]
    for line in data:
        lp_rows.append(line.strip('\n').split(','))

    directory=os.getcwd()+"/static/images/"
    for file in os.listdir(directory):
        if file.split('_')[0]=='2019':
            pi_img="/static/images/"+str(file)

    today=datetime.now().date()
    qz_rel_path="/data/quiz.csv"
    qz_path=os.getcwd()+qz_rel_path 
    df_quiz=pd.read_csv(qz_path)
    df_quiz['Open_By']=pd.to_datetime(df_quiz['Open_By'])
    df_quiz['Close_By']=pd.to_datetime(df_quiz['Close_By'])
    df_quiz.loc[df_quiz['Close_By']<today,'Status']='Closed'
    df_quiz.loc[(df_quiz['Open_By']<=today) & (df_quiz['Close_By']>=today),'Status']='Active'
    df_quiz.to_csv(qz_path,index=False)
    df=df_quiz.groupby('Status')['QuizID'].count().reset_index().rename(columns={'QuizID':'Count'})

    if df[df['Status']=='Active']['Count'].values:
        active=df[df['Status']=='Active']['Count'].values[0]
    else:
        active=0
    if df[df['Status']=='Closed']['Count'].values:
        closed=df[df['Status']=='Closed']['Count'].values[0]
    else:
        closed=0
    if df[df['Status']=='Not Opened Yet']['Count'].values:
        notopyet=df[df['Status']=='Not Opened Yet']['Count'].values[0]
    else:
        notopyet=0
    
    return render_template('admin_dashboard.html',active=active,closed=closed,notop=notopyet,pi_img=pi_img,lp_rows=lp_rows)

@app.route('/admin_dashboard',methods=['POST','GET'])
def login():
    error=None
    if request.method=='POST': 
        try:      
            unm=request.form['userid']
            pwd=request.form['pwd']
            rel_path="/data/employees.csv"
            path=os.getcwd()+rel_path
            df_emp=pd.read_csv(path)
            df_emp=df_emp[df_emp['Category']==1]

            if df_emp[df_emp['Username']==unm]['Password'].values[0]==pwd:
                global logid
                logid=df_emp[df_emp['Username']==unm]['EmpID'].values[0]
                return dashboard_load_data()
            
            error="Invalid Username and Password!"

        except:
            error="Invalid Username and Password!"
        return render_template("login.html",error=error)

@app.route('/admin_dashboard.html')
def adm_dash():
    return dashboard_load_data()

@app.route('/adm_employees')
def adm_emp_but():

    rel_path="/data/employees.csv"
    path=os.getcwd()+rel_path      
    with open(path,"r") as f:
        data=f.readlines()[1:]
    rows=[]
    for line in data:
        rows.append(line.strip('\n').split(','))
    newid = int(rows[-1][0])+1
    return render_template('admin_employees.html', data=rows,new_empid=newid)

@app.route('/adm_employees',methods=['POST','GET'])
def adm_add_emp():
    if request.method=='POST':
        rel_path="/data/employees.csv"
        path=os.getcwd()+rel_path 
        with open(path,"r") as f:
            data=f.readlines()
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))

        for row in rows:
            if row[0]==request.form['empid']:
                df_emp=pd.read_csv(path)
                df_emp=df_emp.astype(str)
                df_emp.loc[df_emp['EmpID'] == request.form['empid'], 'EmpName'] = request.form['empname']
                df_emp.loc[df_emp['EmpID'] == request.form['empid'], 'EmailID'] = request.form['emailid']
                df_emp.loc[df_emp['EmpID'] == request.form['empid'], 'Username'] = request.form['username']
                df_emp.loc[df_emp['EmpID'] == request.form['empid'], 'Password'] = request.form['username']+request.form['empid']
                df_emp.loc[df_emp['EmpID'] == request.form['empid'], 'Role'] = request.form['role']
                df_emp.loc[df_emp['EmpID'] == request.form['empid'], 'Category'] = request.form['category']
                df_emp.to_csv(path,index=False)
                return redirect('/adm_employees')

        line = request.form['empid'] + ',' + request.form['empname']+ ',' + request.form['emailid'] + ',' + request.form['username'] + ',' + request.form['username']+request.form['empid'] + ',' + request.form['role'] + ',' + request.form['category']
        
        with open(path,"a") as f:
            f.write(line)
            f.write("\n")
        return redirect('/adm_employees')

@app.route('/adm_emp_del', methods=['POST','GET'])
def adm_emp_del_but():
    if request.method=='POST':
        rel_path="/data/employees.csv"
        path=os.getcwd()+rel_path
        df_emp=pd.read_csv(path)
        df_emp=df_emp.astype(str)
        df_emp=df_emp[df_emp['EmpID'] != request.form['empid']]
        df_emp.to_csv(path,index=False)
        return redirect('/adm_employees')


@app.route('/adm_categories')
def adm_cat_but(view=[]):
    rel_path="/data/categories.csv"
    path=os.getcwd()+rel_path      
    with open(path,"r") as f:
        data=f.readlines()[1:]
    rows=[]
    for line in data:
        rows.append(line.strip('\n').split(','))
    newid = int(rows[-1][0])+1
    return render_template('admin_categories.html', catdata=rows,empdata=view,new_catid=newid)

@app.route('/adm_categories', methods=['POST','GET'])
def adm_cat_add():
    if request.method=='POST':
        rel_path="/data/categories.csv"
        path=os.getcwd()+rel_path 
        with open(path,"r") as f:
            data=f.readlines()
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))

        for row in rows:
            if row[0]==request.form['catid']:
                df_cat=pd.read_csv(path)
                df_cat=df_cat.astype(str)
                df_cat.loc[df_cat['ID'] == request.form['catid'], 'CATEGORY'] = request.form['catname']
                df_cat.to_csv(path,index=False)
                return redirect('/adm_categories')

        line = request.form['catid'] + ',' + request.form['catname']
        
        with open(path,"a") as f:
            f.write(line)
            f.write("\n")
        return redirect('/adm_categories')

@app.route('/adm_cat_del', methods=['POST','GET'])
def adm_cat_del():
    if request.method=='POST':
        rel_path="/data/categories.csv"
        path=os.getcwd()+rel_path
        df_cat=pd.read_csv(path)
        df_cat=df_cat.astype(str)
        df_cat=df_cat[df_cat['ID'] != request.form['catid']]
        df_cat.to_csv(path,index=False)
        return redirect('/adm_categories')

@app.route('/adm_cat_view', methods=['POST','GET'])
def adm_cat_view_emp():
    if request.method=='POST':
        rel_path="/data/employees.csv"
        path=os.getcwd()+rel_path
        df_emp=pd.read_csv(path)
        df_emp=df_emp.astype(str)
        df_emp=df_emp[df_emp['Category'] == request.form['catid']]
        df_emp=df_emp.values.tolist()
        return adm_cat_but(df_emp)


@app.route('/adm_quiz')
def adm_quiz_but(qn_view=[],error=""):
    today=datetime.now().date()
    rel_path="/data/quiz.csv"
    path=os.getcwd()+rel_path 
    df_quiz=pd.read_csv(path)
    df_quiz['Open_By']=pd.to_datetime(df_quiz['Open_By'])
    df_quiz['Close_By']=pd.to_datetime(df_quiz['Close_By'])
    df_quiz.loc[df_quiz['Close_By']<today,'Status']='Closed'
    df_quiz.loc[(df_quiz['Open_By']<=today) & (df_quiz['Close_By']>=today),'Status']='Active'
    df_quiz.to_csv(path,index=False)

    rel_path="/data/quiz.csv"
    path=os.getcwd()+rel_path      
    with open(path,"r") as f:
        data=f.readlines()[1:]
    rows=[]
    for line in data:
        rows.append(line.strip('\n').split(','))
    if not rows:
        newid=1
    else:
        newid = int(rows[-1][0])+1
    
    return render_template('admin_Quiz.html', qz_data=rows,qn_data=qn_view,new_quizid=newid,error=error)

@app.route('/adm_quiz', methods=['POST','GET'])
def adm_add_quiz():
    if request.method=='POST':
        createdat = datetime.now().date()
        openby = datetime.strptime(request.form['openby'], '%Y-%m-%d').date()
        if (openby-createdat).days !=0:
            status='Not Opened Yet'
        else:
            status='Active'

        rel_path="/data/quiz.csv"
        qz_path=os.getcwd()+rel_path 
        with open(qz_path,"r") as f:
            data=f.readlines()[1:]
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))

        for row in rows:
            if row[0]==request.form['quizid']:
                df_quiz=pd.read_csv(qz_path)
                df_quiz=df_quiz.astype(str)
                df_quiz.loc[df_quiz['QuizID'] == request.form['quizid'], 'QuizName'] = request.form['quizname']
                df_quiz.loc[df_quiz['QuizID'] == request.form['quizid'], 'Duration'] = request.form['duration']
                df_quiz.loc[df_quiz['QuizID'] == request.form['quizid'], 'Created_At'] = str(createdat)
                df_quiz.loc[df_quiz['QuizID'] == request.form['quizid'], 'Open_By'] = request.form['openby']
                df_quiz.loc[df_quiz['QuizID'] == request.form['quizid'], 'Close_By'] = request.form['closeby']
                df_quiz.loc[df_quiz['QuizID'] == request.form['quizid'], 'Status'] =status
                df_quiz.to_csv(qz_path,index=False)
                return adm_quiz_but()

        qn_list=[]
        raw_list=request.form['textlist'][:-2].split(',-,')
        for each_qn in raw_list:
            qn_list.append(each_qn.split(','))
        cols=['QnNo','Question','OptionA','OptionB','OptionC','OptionD','Answer','Points']
        df_qn=pd.DataFrame(qn_list,columns=cols)
        filename=request.form['quizid']+'_'+'question.csv'
        qn_rel_path='/data/questions/'+filename
        qn_path=os.getcwd()+qn_rel_path      
        df_qn.to_csv(qn_path,index=False)

        result_filename=request.form['quizid']+'_'+'results.csv'
        result_rel_path=os.getcwd()+'/data/detailedResults/'+result_filename
        header=['QuizID','QuizName','EmpID','EmpName','Score','Percentage','SubmittedAt']
        df_res=pd.DataFrame(columns=header)
        df_res.to_csv(result_rel_path,index=False)
        
        df=pd.read_csv(qn_path)
        total=str(df['Points'].sum())

        line = request.form['quizid'] + ',' + request.form['quizname']+ ',' + request.form['duration'] + ',' + total + ',' + str(createdat) +','+request.form['openby'] + ',' + request.form['closeby'] + ',' + status
   
        with open(qz_path,"a") as f:
            f.write(line)
            f.write("\n")

        return adm_quiz_but()



@app.route('/adm_qz_del', methods=['POST','GET'])
def adm_qz_del_btn():
    if request.method=='POST':
        qz_rel_path="/data/quiz.csv"
        qz_path=os.getcwd()+qz_rel_path
        df_quiz=pd.read_csv(qz_path)
        df_quiz=df_quiz.astype(str)
        df_quiz=df_quiz[df_quiz['QuizID'] != request.form['quizid']]
        df_quiz.to_csv(qz_path,index=False)

        directory = os.getcwd()+'/data/questions/'
        for filename in os.listdir(directory):
            if filename.split('_')[0]==request.form['quizid']:
                os.remove(directory+filename)

        return redirect('/adm_quiz')


@app.route('/adm_qn_view', methods=['POST','GET'])
def adm_qz_view_qn():
    if request.method=='POST':
        rel_path="/data/quiz.csv"
        path=os.getcwd()+rel_path 
        with open(path,"r") as f:
            data=f.readlines()
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))

        for row in rows:
            if row[0]==request.form['quizid']:
                directory = os.getcwd()+'/data/questions/'
                for filename in os.listdir(directory):
                    if filename.split('_')[0]==request.form['quizid']:
                        df_questions=pd.read_csv(directory+filename)
                        df_questions=df_questions.values.tolist()
                        return adm_quiz_but(qn_view=df_questions)
        msg="Please Select the Quiz to show its details."
        return adm_quiz_but(error=msg)



@app.route('/adm_reports')
def adm_reports(catlist=['Quiz Report','Monthly Report','Yearly Report'],oplist=[],report=[]):
    rel_path="/data/reports.csv"
    path=os.getcwd()+rel_path
    df_rep=pd.read_csv(path)
    oplist=df_rep['QuizName'].values.tolist()
    return render_template('admin_reports.html',catlist=catlist,oplist=oplist,reports=report)

@app.route('/adm_reports', methods=['POST','GET'])
def adm_report_cat():
    if request.method=="POST":
        if request.form['sel_cat']=="Quiz Report":
            rel_path="/data/reports.csv"
            path=os.getcwd()+rel_path
            df_rep=pd.read_csv(path)
            rows=df_rep['QuizName'].values.tolist()
            return render_template('admin_reports.html',catlist=['Quiz Report'],oplist=rows)

        if request.form['sel_cat']=="Monthly Report":
            rows=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            return render_template('admin_reports.html',catlist=['Monthly Report'],oplist=rows)

        if request.form['sel_cat']=="Yearly Report":
            rel_path="/data/reports.csv"
            path=os.getcwd()+rel_path 
            df_rep=pd.read_csv(path)
            df_rep['year'] = pd.to_datetime(df_rep['ClosedAt']).dt.year
            rows=df_rep['year'].values.tolist()
            return render_template('admin_reports.html',catlist=['Yearly Report'],oplist=rows)

        return adm_reports()


@app.route('/adm_reports_view', methods=['POST','GET'])
def adm_report_view():
    if request.method=="POST":
        if request.form['sel_cat']=="Quiz Report":
            rel_path="/data/reports.csv"
            path=os.getcwd()+rel_path
            df_rep=pd.read_csv(path)
            df_rep=df_rep[df_rep['QuizName']==request.form['value']]
            rows=df_rep.values.tolist()
            return adm_reports(report=rows)

        if request.form['sel_cat']=="Monthly Report":
            rel_path="/data/reports.csv"
            path=os.getcwd()+rel_path
            df_rep=pd.read_csv(path)
            df_rep['months'] = pd.to_datetime(df_rep['ClosedAt']).dt.month
            date_dict={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
            for k,v in date_dict.items():
                if v==request.form['value']:
                    df_rep=df_rep[df_rep['months']==k]
            return adm_reports(report=df_rep.values.tolist())

        if request.form['sel_cat']=="Yearly Report":
            rel_path="/data/reports.csv"
            path=os.getcwd()+rel_path
            df_rep=pd.read_csv(path)
            df_rep['year'] = pd.to_datetime(df_rep['ClosedAt']).dt.year
            df_rep=df_rep[df_rep['year']==int(request.form['value'])]
            return adm_reports(report=df_rep.values.tolist())




@app.route('/adm_res_tab_home', methods=['POST','GET'])
def adm_res_tab_btn():
    if request.method=='POST':
        return render_template('admin_result_table.html')


@app.route('/adm_res_tab', methods=['POST','GET'])
def adm_res_tab():
    if request.method=='POST':
        directory = os.getcwd()+'/data/detailedResults/'
        for filename in os.listdir(directory):
            if filename.split('_')[0]==request.form['quizid']:
                df_res=pd.read_csv(directory+filename)
                return render_template('admin_result_table.html',data=df_res.sort_values(by=['Percentage'], ascending=False).values.tolist())     



@app.route('/adm_att_quiz_home')
def adm_attend_quiz_home():
    today=datetime.now().date()
    rel_path="/data/quiz.csv"
    path=os.getcwd()+rel_path 
    df_quiz=pd.read_csv(path)
    df_quiz['Open_By']=pd.to_datetime(df_quiz['Open_By'])
    df_quiz['Close_By']=pd.to_datetime(df_quiz['Close_By'])
    df_quiz.loc[df_quiz['Close_By']<today,'Status']='Closed'
    df_quiz.loc[(df_quiz['Open_By']<=today) & (df_quiz['Close_By']>=today),'Status']='Active'
    df_quiz.to_csv(path,index=False)
    df = df_quiz[df_quiz['Status']=='Active']
    rows=df.values.tolist()
    return render_template('admin_attend_home.html',qz_list=rows)
  

@app.route('/adm_att_quiz_btn', methods=['POST','GET'])
def adm_att_quiz_btn():
    if request.method=="POST":
        qz_data=[request.form['quizid'],request.form['quizname'],request.form['duration'],request.form['total']]

        directory = os.getcwd()+'/data/questions/'
        for filename in os.listdir(directory):
            if filename.split('_')[0]==request.form['quizid']:
                df_question = pd.read_csv(directory+filename)
                rows=df_question.values.tolist()
                print(rows)
                print(qz_data)
                return render_template('admin_attend_quiz.html',qz_data=qz_data,qn_list=rows)

@app.route('/adm_quiz_calc', methods=['POST','GET'])
def adm_quiz_res_calc():
    if request.method=="POST":

        qz_data=request.form['hiddentext1']
        ans_list=request.form['AnswerList'].split(',')
        d={}
        for i in range(0,len(ans_list),2):
            d[ans_list[i]]=ans_list[i+1]
        ans_list=list(d.values())
        qz_data=qz_data.strip("[").strip("]").replace("'","").split(",")

        directory = os.getcwd()+'/data/questions/'
        for filename in os.listdir(directory):
            if filename.split('_')[0]==qz_data[0]:
                df_question = pd.read_csv(directory+filename)
                df_question['attended']=ans_list
                df_question.loc[df_question['Answer']==df_question['attended'],'Marks']=df_question['Points']
                df_question.loc[df_question['Answer']!=df_question['attended'],'Marks']=0
                score=df_question['Marks'].sum()
                percentage=(df_question['Marks'].sum()/df_question['Points'].sum())*100

        emp_rel_path="/data/employees.csv"
        emp_path=os.getcwd()+emp_rel_path
        df_emp=pd.read_csv(emp_path)
        global logid
        emp_name=df_emp.loc[df_emp['EmpID'].astype(str)==str(logid)]['EmpName'].values[0]
        emp_id=logid

        line=str(qz_data[0])+','+str(qz_data[1])+','+str(emp_id)+','+str(emp_name)+','+str(score)+','+str(round(percentage,2))+','+str(datetime.now().date())

        res_dir=os.getcwd()+'/data/detailedResults/'
        for filename in os.listdir(res_dir):
            if filename.split('_')[0]==qz_data[0]:
                with open(res_dir+filename,"a") as f:
                    f.write(line)
                    f.write("\n")
                df_detRes=pd.read_csv(res_dir+filename)

        qz_rel_path="/data/quiz.csv"
        qz_path=os.getcwd()+qz_rel_path
        df_qz=pd.read_csv(qz_path)

        num_part=df_detRes['EmpID'].nunique()
        top_score=df_detRes['Score'].max()
        avg_score=df_detRes['Score'].mean()
        top_perf=df_detRes[df_detRes['Score']==top_score]['EmpName'].values[0]
        closed_at=df_qz[df_qz['QuizID'].astype(str)==qz_data[0]]['Close_By'].values[0]
        total_score=df_qz[df_qz['QuizID'].astype(str)==qz_data[0]]['Total'].values[0]

        rep_rel_path="/data/reports.csv"
        rep_path=os.getcwd()+rep_rel_path 
        with open(rep_path,"r") as f:
            data=f.readlines()
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))

        for row in rows:
            if row[0]==qz_data[0]:
                df_rep=pd.read_csv(rep_path)
                df_rep=df_rep.astype(str)
                df_rep.loc[df_rep['QuizID'] == qz_data[0], 'QuizName'] = qz_data[1]
                df_rep.loc[df_rep['QuizID'] == qz_data[0], 'ClosedAt'] = closed_at
                df_rep.loc[df_rep['QuizID'] == qz_data[0], 'Participants'] = num_part
                df_rep.loc[df_rep['QuizID'] == qz_data[0], 'TopPerformer'] = top_perf
                df_rep.loc[df_rep['QuizID'] == qz_data[0], 'TopScore'] = top_score
                df_rep.loc[df_rep['QuizID'] == qz_data[0], 'AvgScore'] = avg_score
                df_rep.to_csv(rep_path,index=False)
                return render_template('admin_dashboard.html')

        line=qz_data[0]+','+qz_data[1]+','+ closed_at +','+ str(num_part) +','+str(top_perf) +','+str(top_score) +','+str(round(avg_score,2))+','+str(total_score)
        
        with open(rep_path,"a") as f:
            f.write(line)
            f.write("\n")
        return render_template('admin_dashboard.html')
@app.route('/G_Report',methods=['POST','GET'])
def G_Report():
    return render_template('Saphire_report_page.html')

@app.route('/G_Add')
def G_add_home():
    return render_template('G_add.html')


@app.route('/G_Edit')
def G_edit_home():
	rel_path="/data/addgoals.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(','))
	return render_template('G_edit.html',data=rows)

@app.route('/G_Add',methods=['POST','GET'])
def add_goals():
	if request.method=='POST':
		rel_path="/data/addgoals.csv"
		path=os.getcwd()+rel_path
		line = request.form['empid'] + ',' + request.form['empname']+ ',' + request.form['client_q1'] + ','+request.form['client_q2'] +','+request.form['client_q3'] +','+request.form['client_q4'] +','+request.form['ts_q1'] +','+request.form['ts_q2'] +','+request.form['ts_q3'] +','+request.form['ts_q4'] +','+request.form['ti_q1'] +','+request.form['ti_q2'] +','+request.form['ti_q3'] +','+request.form['ti_q4'] +','+request.form['p_q1'] +','+request.form['p_q2'] +','+request.form['p_q3'] +','+request.form['p_q4'] +','+request.form['f_q1'] +','+request.form['f_q2'] +','+request.form['f_q3'] +','+request.form['f_q4'] +',' + request.form['year']+','+ request.form['StatusRead']
		with open(path,"a") as f:
			f.write(line)
			f.write("\n")
		print(line)
		return redirect('/G_Add')

@app.route('/G_adm_emp_del', methods=['POST','GET'])
def G_adm_emp_del_but():
    if request.method=='POST':
        rel_path="/data/addgoals.csv"
        path=os.getcwd()+rel_path
        df_emp=pd.read_csv(path)
        df_emp=df_emp.astype(str)
        df_emp=df_emp[df_emp['EmpID'] != request.form['empid']]
        df_emp.to_csv(path,index=False)
        return redirect('/G_Edit')

@app.route('/G_Edit',methods=['POST','GET'])
def edit_goals():
    if request.method=='POST':
        rel_path="/data/addgoals.csv"
        path=os.getcwd()+rel_path
        with open(path,"r") as f:
            data=f.readlines()
            rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))
        for row in rows:
            if row[0]==request.form['empid']:
                df_lp=pd.read_csv(path)
                df_lp=df_lp.astype(str)
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'EmpName'] = request.form['empname']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'C_Q1'] = request.form['client_q1']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'C_Q2'] = request.form['client_q2']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'C_Q3'] = request.form['client_q3']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'C_Q4'] = request.form['client_q4']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TS_Q1'] = request.form['ts_q1']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TS_Q2'] = request.form['ts_q2']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TS_Q3'] = request.form['ts_q3']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TS_Q4'] = request.form['ts_q4']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TI_Q1'] = request.form['ti_q1']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TI_Q2'] = request.form['ti_q2']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TI_Q3'] = request.form['ti_q3']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'TI_Q4'] = request.form['ti_q4']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'P_Q1'] = request.form['p_q1']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'P_Q2'] = request.form['p_q2']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'P_Q3'] = request.form['p_q3']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'P_Q4'] = request.form['p_q4']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'F_Q1'] = request.form['f_q1']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'F_Q2'] = request.form['f_q2']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'F_Q3'] = request.form['f_q3']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'F_Q4'] = request.form['f_q4']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'Year'] = request.form['year']
                df_lp.loc[df_lp['EmpID'] == request.form['empid'], 'Status'] = request.form['StatusRead']
                df_lp.to_csv(path,index=False)
                return redirect('/G_Edit')
        # line = request.form['empid'] + ',' + request.form['empname']+ ',' + request.form['client_q1'] +',' + request.form['client_q2'] +',' + request.form['client_q3'] +',' + request.form['client_q4'] +',' + request.form['ts_q1'] +',' + request.form['ts_q2'] +',' + request.form['ts_q3'] +',' + request.form['ts_q4'] +',' + request.form['ti_q1'] +',' + request.form['ti_q2'] +',' + request.form['ti_q3'] +',' + request.form['ti_q4'] +',' + request.form['p_q1'] +',' + request.form['p_q2'] +',' + request.form['p_q3'] +',' + request.form['p_q4'] + ',' + request.form['f_q1'] +',' + request.form['f_q2'] +',' + request.form['f_q3'] +',' + request.form['f_q4'] +',' + request.form['year'] +',' + request.form['StatusRead']
        # with open(path,"a") as f:
        #     f.write(line)
        #     f.write("\n")
        # return redirect('/G_Edit')

@app.route('/Add_LP')
def Lp_add_home():
    return render_template('Add_LP.html')

@app.route('/LP_report')
def Lp_report_home():
    return render_template('LP_report.html')

@app.route('/Edit_LP')
def Lp_edit_home():
	rel_path="/data/learnpgm.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(','))
	return render_template('Edit_LP.html',data=rows)

@app.route('/Add_LP',methods=['POST','GET'])
def add_LP():
	if request.method=='POST':
		rel_path="/data/learnpgm.csv"
		path=os.getcwd()+rel_path
		line = request.form['topic'] + ',' + request.form['dot']+ ',' + request.form['venue'] + ',' + request.form['trainer'] + ',' + request.form['status']
		with open(path,"a") as f:
			f.write(line)
			f.write("\n")
		print(line)
		return redirect('/Add_LP')

@app.route('/Edit_LP',methods=['POST','GET'])
def edit_LP():
	if request.method=='POST':
		rel_path="/data/learnpgm.csv"
		path=os.getcwd()+rel_path
		with open(path,"r") as f:
			data=f.readlines()[1:]
		rows=[]
		for line in data:
			rows.append(line.strip('\n').split(','))

		for row in rows:
			if row[0]==request.form['topic']:
				df_lp=pd.read_csv(path)
				df_lp=df_lp.astype(str)
				df_lp.loc[df_lp['Topic'] == request.form['topic'], 'Date Of Training'] = request.form['dot']
				df_lp.loc[df_lp['Topic'] == request.form['topic'], 'Venue'] = request.form['venue']
				df_lp.loc[df_lp['Topic'] == request.form['topic'], 'Trainer'] = request.form['trainer']
				df_lp.loc[df_lp['Topic'] == request.form['topic'], 'Status'] = request.form['status']
				df_lp.to_csv(path,index=False)
				return redirect('/Edit_LP')
				
		line = request.form['topic'] + ',' + request.form['dot']+ ',' + request.form['venue'] + ',' + request.form['trainer'] + ',' + request.form['status']
		with open(path,"a") as f:
			f.write(line)
			f.write("\n")
		return redirect('/Edit_LP')

@app.route('/LP_report',methods=['POST','GET'])
def LP_report():
	if request.method=='POST':
		rel_path="/data/learnpgm.csv"
		path=os.getcwd()+rel_path
		df=pd.read_csv(path)
		df=df[df['Date Of Training']==request.form['date']]
		rows=df.values.tolist()
		return render_template('LP_report.html', data=rows)

@app.route('/AddFeed')
def addindex():
	rel_path="/data/learnpgm.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(',')[0])
	return render_template('AddFeed.html',oplist =set(rows))

@app.route('/ViewFeed')
def addindexs():
	rel_path="/data/feedpgm.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(',')[0])
	return render_template('ViewFeed.html',oplist=set(rows))
	
@app.route('/ViewFeed',methods=['POST','GET'])
def viewfeed():
	if request.method=='POST':
		rel_path="/data/feedpgm.csv"
		path=os.getcwd()+rel_path
		with open(path,"r") as f:
			data=f.readlines()[1:]
		rows=[]
		for line in data:
			rows.append(line.strip('\n').split(','))

		for row in rows:
			if row[0]==request.form['topic']:
				df_lp=pd.read_csv(path)
				df_lp=df_lp.astype(str)
				df_fb=df_lp[df_lp['TOPIC']==request.form['topic']]
				fb=df_fb.values.tolist()
				oplist=[]
				for line in data:
					oplist.append(line.strip('\n').split(',')[0])
				return render_template('ViewFeed.html',oplist=set(oplist),fb=fb) 
				
		 		
				
		
	
@app.route('/AddFeed',methods=['POST','GET'])
def addfeed():
	if request.method=='POST':
		rel_path="/data/feedpgm.csv"
		path=os.getcwd()+rel_path
		line = request.form['topic'] + ',' + request.form['Feedback']
		with open(path,"a") as f:
			f.write(line)
			f.write("\n")
		print(line)
		return redirect('/AddFeed')
@app.route('/road_home')
def road():
    return render_template('roadmap.html')

@app.route('/road',methods=['POST','GET'])
def eff_road():
    if request.method=='POST':
        rel_path="/data/road.csv"
        path=os.getcwd()+rel_path
        line = request.form['year'] + ',' + request.form['feedback']

        print(line)
        with open(path,"a") as f:
            f.write(line)
            f.write("\n")
        return redirect('/road_home')


@app.route('/roadview',methods=['POST','GET'])
def rview(img=""):
    if request.method=='POST':
        rel_path="/data/road.csv"
        path=os.getcwd()+rel_path
        df=pd.read_csv(path)
        df=df[df['YEAR'].astype(str)==request.form['year']]
        print(df)
        rows=df.values.tolist()

        directory=os.getcwd()+"/static/images/"
        for file in os.listdir(directory):
            if file.split('_')[0]==request.form['year']:
                img="/static/images/"+str(file)

        return render_template('roadmap.html', data=rows,image=img)

@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'static/images/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]
        if (ext.lower() == ".jpg") or (ext.lower() == ".png"):
            print("File supported moving on...")
        else:
            render_template("Error.html", message="Files uploaded are not supported...")
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("roadmap.html", msg='s')


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


@app.route('/gallery')
def get_gallery():
    image_names = os.listdir('./images')
    print(image_names)
    return render_template("gallery.html", image_names=image_names)

@app.route('/initiative_home')
def initiative_home():
    return render_template('Basic_elements1.html')

@app.route('/Basic_elements1',methods=['POST','GET'])
def add_initiative():
    if request.method=='POST':
        if request.form['initiative']=='Peer Review':
            return render_template('Peer_Form.html')
        if request.form['initiative']=='Effective Communication':
            return render_template('effective communication.html')
        if request.form['initiative']=='Reusable Requirements':
            return render_template('ReuseReq_Form.html')

@app.route('/peerform')
def add_peer_home():
    return render_template('Peer_Form.html')


@app.route('/Peer_Form',methods=['POST','GET'])
def add_peer():
    if request.method=='POST':
        rel_path="/data/peerform.csv"
        path=os.getcwd()+rel_path
        line = request.form['name'] + ',' + str(request.form['date']) + ',' + request.form['orgname'] + ',' + request.form['feed']+',' + request.form['statusRadios']
        with open(path,"a") as f:
            f.write(line)
            f.write("\n")
        print(line)
        return add_peer_home()

@app.route('/Peer_table.html')
def peer_com_link():
	rel_path="/data/peerform.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(','))
	return render_template('Peer_table.html',data=rows)

@app.route('/edit_peer',methods=['POST','GET'])
def edit_peer():
    if request.method=='POST':
        rel_path="/data/peerform.csv"
        path=os.getcwd()+rel_path
        with open(path,"r") as f:
            data=f.readlines()[1:]
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))
        return render_template('Peer_table.html',data=rows)

@app.route('/eff_com_add',methods=['POST','GET'])
def eff_com_add():
    if request.method=='POST':
        rel_path="/data/effCom.csv"
        path=os.getcwd()+rel_path
        line = request.form['name'] + ',' + request.form['category'] + ',' + str(request.form['date']) + ',' + request.form['Organizer'] + ',' + request.form['venue']+',' + request.form['feedback']+',' + request.form['statusRadios']

        print(line)
        with open(path,"a") as f:
            f.write(line)
            f.write("\n")
        return render_template('effective communication.html')

@app.route('/effective_table.html')
def eff_com_link():
	rel_path="/data/effCom.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(','))
	return render_template('effective_table.html',data=rows)

@app.route('/PI_eview',methods=['POST','GET'])
def edit_eff():
    if request.method=='POST':
    	rel_path="/data/effCom.csv"
    	path=os.getcwd()+rel_path
    	with open(path,"r") as f:
    		data=f.readlines()[1:]
    	rows=[]
    	for line in data:
    		rows.append(line.strip('\n').split(','))
    	return render_template('effective_table.html',data=rows)


@app.route('/view_req',methods=['POST','GET'])
def view_req():
    if request.method=='POST':
        rel_path="/data/reusable.csv"
        path=os.getcwd()+rel_path
        with open(path,"r") as f:
            data=f.readlines()[1:]
        rows=[]
        for line in data:
            rows.append(line.strip('\n').split(','))
        return render_template('Re_req table.html',data=rows)

@app.route('/Re_req table.html')
def req_com_link():
	rel_path="/data/reusable.csv"
	path=os.getcwd()+rel_path
	with open(path,"r") as f:
		data=f.readlines()[1:]
	rows=[]
	for line in data:
		rows.append(line.strip('\n').split(','))
	return render_template('Re_req table.html',data=rows)


@app.route('/ReuseReq_Form',methods=['POST','GET'])
def add_req():
	if request.method=='POST':
		rel_path="/data/reusable.csv"
		path=os.getcwd()+rel_path
		line = request.form['projectname'] + ',' + request.form['pn']+ ',' + request.form['req'] + ',' + request.form['version']
		with open(path,"a") as f:
			f.write(line)
			f.write("\n")
		print(line)
		return render_template('ReuseReq_Form.html')





if __name__ =='__main__':
    logid='sdff'
    app.run(debug=True)
