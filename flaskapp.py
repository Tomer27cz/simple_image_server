from flask import Flask, render_template, request, redirect
import config

app = Flask(__name__)

# header('Content-Type: image/jpeg');
# header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
# header("Cache-Control: post-check=0, pre-check=0", false);
# header("Pragma: no-cache");

@app.route('/')
def index():
    return image()

@app.route('/image')
def image():
    try:
        with open(f'{config.PATH}/url.txt', 'r') as file:
            image_url = file.read()
    except Exception as e:
        return f'Error: {e}'

    resp = redirect(image_url)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Cache-Control'] = 'post-check=0, pre-check=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/link')
def link():
    try:
        with open(f'{config.PATH}static/link.txt', 'r') as file:
            link_url = file.read()
    except Exception as e:
        return f'Error: {e}'

    return redirect(link_url)

@app.route('/caritas2014', methods=['POST', 'GET'])
def change_image():
    if request.method == 'POST':
        if 'image_url' in request.form:
            f = request.form['image_url']
            try:
                with open(f'{config.PATH}static/url.txt', 'w') as file:
                    file.write(f)
                return f'Image URL: {f} - Saved Successfully!'
            except Exception as e:
                return f'Error: {e}'
        if 'link_url' in request.form:
            f = request.form['link_url']
            try:
                with open(f'{config.PATH}static/link.txt', 'w') as file:
                    file.write(f)
                return f'Link URL: {f} - Saved Successfully!'
            except Exception as e:
                return f'Error: {e}'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)