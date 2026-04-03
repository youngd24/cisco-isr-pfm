from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
        <body>
            <h1>INITECH Web Portal</h1>
            <p>PC LOAD LETTER</p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
