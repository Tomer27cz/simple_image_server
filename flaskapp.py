from flask import Flask, render_template, request, redirect, session
import config
import sys
from time import gmtime, strftime, time

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# header('Content-Type: image/jpeg');
# header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
# header("Cache-Control: post-check=0, pre-check=0", false);
# header("Pragma: no-cache");

def get_current_image():
    try:
        with open(f'{config.PATH}static/url.txt', 'r') as file:
            image_url = file.read()
    except Exception as e:
        log(e, log_type='error')
        raise f'Error: {e}'
    return image_url

def get_current_link():
    try:
        with open(f'{config.PATH}static/link.txt', 'r') as file:
            link_url = file.read()
    except Exception as e:
        log(e, log_type='error')
        raise f'Error: {e}'
    return link_url

def struct_to_time(struct_time, first='date') -> str:
    """
    Converts struct_time to time string
    :param struct_time: int == struct_time
    :param first: ('date', 'time') == (01/01/1970 00:00:00, 00:00:00 01/01/1970)
    :return: str
    """
    if type(struct_time) != int:
        try:
            struct_time = int(struct_time)
        except (ValueError, TypeError):
            return struct_time

    if first == 'date':
        return strftime("%d/%m/%Y %H:%M:%S", gmtime(struct_time))

    if first == 'time':
        return strftime("%H:%M:%S %d/%m/%Y", gmtime(struct_time))

    return strftime("%H:%M:%S %d/%m/%Y", gmtime(struct_time))

def log(text_data, log_type='text', ip=None) -> None:
    now_time_str = struct_to_time(time())

    if log_type == 'text':
        message = f"{now_time_str} |  {text_data}"
    elif log_type == 'ip':
        message = f"{now_time_str} | {ip} | Requested: {text_data}"
    elif log_type == 'web':
        message = f"{now_time_str} | {ip} | {text_data}"
    elif log_type == 'error':
        message = f"{now_time_str} | ERROR | {text_data}"
    else:
        raise ValueError('Wrong log_type')

    if log_type == 'error':
        print(message, file=sys.stderr)
    else:
        print(message)

    with open(f"{config.PATH}log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

@app.route('/')
def index():
    return image()

@app.route('/image')
def image():
    try:
        image_url = get_current_image()
    except Exception as e:
        return str(e)

    resp = redirect(image_url)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Cache-Control'] = 'post-check=0, pre-check=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/link')
def link():
    try:
        link_url = get_current_link()
    except Exception as e:
        return str(e)

    return redirect(link_url)

@app.route('/caritas2014', methods=['POST', 'GET'])
def change_image():
    log(request.url, log_type='ip', ip=request.remote_addr)
    if 'username' not in session.keys():
        return redirect('/login')
    username = session['username']

    message = None
    if request.method == 'POST':
        if 'image_url' in request.form:
            log(f'{session["username"]} is trying change image url to {request.form["image_url"]}')
            f = request.form['image_url']
            try:
                with open(f'{config.PATH}static/url.txt', 'w') as file:
                    file.write(f)
                message = f'Image URL: {f} - Saved Successfully!'
                log(f'{session["username"]} changed image url to {request.form["image_url"]}')
            except Exception as e:
                log(e, log_type='error')
                return f'Error: {e}'
        if 'link_url' in request.form:
            log(f'{session["username"]} is trying change link url to {request.form["link_url"]}')
            f = request.form['link_url']
            try:
                with open(f'{config.PATH}static/link.txt', 'w') as file:
                    file.write(f)
                message = f'Link URL: {f} - Saved Successfully!'
                log(f'{session["username"]} changed link url to {request.form["link_url"]}')
            except Exception as e:
                log(e, log_type='error')
                return f'Error: {e}'

    try:
        image_url = get_current_image()
        link_url = get_current_link()
    except Exception as e:
        log(e, log_type='error')
        return e

    return render_template('index.html', image_url=image_url, link_url=link_url, message=message, username=username)

@app.route('/log')
def show_log():
    log(request.url, log_type='ip', ip=request.remote_addr)
    if 'username' not in session.keys():
        return redirect('/login')

    try:
        with open(f'{config.PATH}log.txt', 'r', encoding='utf-8') as file:
            log_data = file.readlines()
    except Exception as e:
        log(e, log_type='error')
        return f'Error: {e}'

    return render_template('log.html', log_data=log_data)

@app.route('/logout')
def logout():
    log(request.url, log_type='ip', ip=request.remote_addr)
    session.clear()
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    log(request.url, log_type='ip', ip=request.remote_addr)
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            for user in config.AUTHORIZED_USERS:
                if username == user['username'] and password == user['password']:
                    session['username'] = username
                    log(f'({username}) logged in successfully', log_type='web', ip=request.remote_addr)
                    return redirect('/caritas2014')
            log(f'({username}) tried to login with wrong password: ({password})', log_type='web', ip=request.remote_addr)
            return render_template('login.html', message='Incorrect username or password')
        log(f'({request.remote_addr}) tried to login without username or password', log_type='web', ip=request.remote_addr)
        return render_template('login.html', message='Please enter username and password')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)