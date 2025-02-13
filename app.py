from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcom to R&R Puynch system"

if __name__ == "__main__":
    app.run(debug=True)