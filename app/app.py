from flask import Flask, render_template

app = Flask(__name__)

@app.route("/<name>")
def find_page(name):
    return render_template(f"{name}.html")


if __name__ == "__main__":
    app.run(debug=True)