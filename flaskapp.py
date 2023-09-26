from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    try:
        with open('static/url.txt', 'r') as file:
            image_url = file.read()
    except Exception as e:
        return f'Error: {e}'
    return redirect(image_url)

@app.route('/caritas2014', methods=['POST', 'GET'])
def change_image():
    if request.method == 'POST':
        f = request.form['url']
        try:
            with open('static/url.txt', 'w') as file:
                file.write(f)
            return f'URL: {f} - Saved Successfully!'
        except Exception as e:
            return f'Error: {e}'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)