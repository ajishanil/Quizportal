# data = pd.read_csv("filename.csv")
# with open('foo.csv', 'a') as f:
#              df.to_csv(f, header=False)
        
# import json
# filename="C:\\Users\\demo project\\APPdevelopment\\templates\\" + df['QzName'][0] + '.json'

# df.to_json(r"C:\Users\demo project\APPdevelopment\templates\test.json",orient='records')
# pd.read_json(r"C:\Users\demo project\APPdevelopment\templates\test.json")
# pd.concat([df,pd.DataFrame([['Python',1,'dfg','dfgh','dfgh','dfghj','xcvbn','poiuyt']],columns=df.columns)],ignore_index=True)

# df=df[df['QzName']=='SQL']
# cols=df.columns[1:]
# path="C:/Users/rebelpc/Desktop/demo project/APPdevelopment/templates/" 
# filename=df['QzName'][0] + '.json'
# with open(path+filename,'w+') as f:
#     df[cols].to_json(path+filename,orient='records')



from flask import Flask,render_template,request,redirect
import os
app=Flask(__name__)

@app.route('/')
def home():
    return render_template('test.html')


if __name__ =='__main__':
    app.run(debug=True,port=5003)