from flask import Flask, request, render_template, url_for

app = Flask(__name__, static_url_path='')

@app.route("/")
def index():
    return render_template('index.html') 

app.run(debug=True)
