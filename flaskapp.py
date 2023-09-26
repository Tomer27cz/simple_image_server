from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('static/img.png', mimetype='image/png')

@app.route('/caritas2014', methods=['POST', 'GET'])
def change_image():
    if request.method == 'POST':
        f = request.files['img']
        f.save('static/img.png')
        return 'Image uploaded successfully'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)