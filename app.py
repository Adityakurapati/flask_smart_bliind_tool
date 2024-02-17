from flask import Flask
app =  Flask(__name__)
@app.route('/')
def hello():
        return 'hello'


if __name__ "__main__":
        aapp.run(debug=False,host='0.0.0.0')