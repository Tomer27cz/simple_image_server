from flask import Flask, render_template, request, redirect, session
import config
import sys
import json
from time import gmtime, strftime, time
from typing import TypedDict, Union

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# header('Content-Type: image/jpeg');
# header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
# header("Cache-Control: post-check=0, pre-check=0", false);
# header("Pragma: no-cache");

class Data(TypedDict):
    image_url: str
    link_url: str

class AnalyticsDataDataTimestamp(TypedDict):
    start: int
    end: Union[int, None]

class AnalyticsDataData(TypedDict):
    author: str
    timestamp: AnalyticsDataDataTimestamp

class AnalyticsData(TypedDict):
    url: str
    redirected: int
    data: AnalyticsDataData

class Analytics(TypedDict):
    image: list[AnalyticsData]
    link: list[AnalyticsData]



# Data
def get_data() -> Data:
    try:
        with open(f'{config.PATH}db/data.json', 'r') as file:
            data = json.load(file)
    except Exception as e:
        log(e, log_type='error')
        raise f'Error: {e}'
    return data

# Analytics
def get_analytics() -> Analytics:
    try:
        with open(f'{config.PATH}db/analytics.json', 'r') as file:
            data = json.load(file)
    except Exception as e:
        log(e, log_type='error')
        raise f'Error: {e}'
    return data

# Get Data
def get_image() -> str:
    return get_data()['image_url']
def get_link() -> str:
    return get_data()['link_url']

# Get Analytics
def get_current_count() -> tuple[int, int]:
    analytics: Analytics = get_analytics()
    image_count = analytics['image'][-1]['redirected'] if analytics['image'] else 0
    link_count = analytics['link'][-1]['redirected'] if analytics['link'] else 0
    return image_count, link_count
def get_total_count() -> tuple[int, int]:
    analytics: Analytics = get_analytics()
    image_count = sum([i['redirected'] for i in analytics['image']])
    link_count = sum([i['redirected'] for i in analytics['link']])
    return image_count, link_count

# Update Data
def update_data(author: str, image_url=None, link_url=None) -> None:
    data: Data = get_data()
    analytics: Analytics = get_analytics()

    if image_url:
        data['image_url'] = image_url
        analytics['image'][-1]['data']['timestamp']['end'] = int(time())
        analytics['image'].append({
            'url': image_url,
            'redirected': 0,
            'data': {
                'author': author,
                'timestamp': {
                    'start': int(time()),
                    'end': None
                }
            }
        })
    if link_url:
        data['link_url'] = link_url
        analytics['link'][-1]['data']['timestamp']['end'] = int(time())
        analytics['link'].append({
            'url': link_url,
            'redirected': 0,
            'data': {
                'author': author,
                'timestamp': {
                    'start': int(time()),
                    'end': None
                }
            }
        })

    try:
        with open(f'{config.PATH}db/data.json', 'w') as file:
            json.dump(data, file, indent=4)
        with open(f'{config.PATH}db/analytics.json', 'w') as file:
            json.dump(analytics, file, indent=4)
    except Exception as e:
        log(e, log_type='error')
        raise f'Error: {e}'

# Update Analytics
def update_analytics(url_type: Union['image', 'link']) -> None:
    analytics = get_analytics()
    if url_type == 'image':
        analytics['image'][-1]['redirected'] += 1
    if url_type == 'link':
        analytics['link'][-1]['redirected'] += 1

    try:
        with open(f'{config.PATH}db/analytics.json', 'w') as file:
            json.dump(analytics, file, indent=4)
    except Exception as e:
        log(e, log_type='error')
        raise f'Error: {e}'

# Other
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
            return 'Now'

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

# Home
@app.route('/')
def index():
    if 'username' in session.keys():
        username = session['username']
    else:
        username = None
    return render_template('tabs/home.html', username=username)

# Email Banner
@app.route('/redirect', methods=['POST', 'GET'])
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
                update_data(author=username, image_url=f)
                message = f'Image URL: {f} - Saved Successfully!'
                log(f'{session["username"]} changed image url to {request.form["image_url"]}')
            except Exception as e:
                log(e, log_type='error')
                return f'Error: {e}'
        if 'link_url' in request.form:
            log(f'{session["username"]} is trying change link url to {request.form["link_url"]}')
            f = request.form['link_url']
            try:
                update_data(author=username, link_url=f)
                message = f'Link URL: {f} - Saved Successfully!'
                log(f'{session["username"]} changed link url to {request.form["link_url"]}')
            except Exception as e:
                log(e, log_type='error')
                return f'Error: {e}'

    try:
        image_url = get_image()
        link_url = get_link()
        count = get_current_count()
    except Exception as e:
        log(e, log_type='error')
        return e

    return render_template('tabs/redirect.html', image_url=image_url, link_url=link_url, message=message, username=username, web_url=config.WEB_URL, count=count)

# Log
@app.route('/log')
def show_log():
    log(request.url, log_type='ip', ip=request.remote_addr)
    if 'username' not in session.keys():
        return redirect('/login')
    username = session['username']

    try:
        with open(f'{config.PATH}log.txt', 'r', encoding='utf-8') as file:
            log_data = file.readlines()
    except Exception as e:
        log(e, log_type='error')
        return f'Error: {e}'

    return render_template('tabs/log.html', log_data=log_data, username=username)

# Analytics
@app.route('/analytics')
def show_analytics():
    log(request.url, log_type='ip', ip=request.remote_addr)
    if 'username' not in session.keys():
        return redirect('/login')
    username = session['username']

    try:
        with open(f'{config.PATH}db/analytics.json', 'r') as file:
            analytics = json.load(file)
            total = get_total_count()
    except Exception as e:
        log(e, log_type='error')
        return f'Error: {e}'

    return render_template('tabs/analytics.html', data=analytics, username=username, total=total, struct_to_time=struct_to_time, reversed=reversed)


# Redirects
@app.route('/image')
def image():
    try:
        image_url = get_image()
        update_analytics(url_type='image')
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
        link_url = get_link()
        update_analytics(url_type='link')
    except Exception as e:
        return str(e)

    return redirect(link_url)


# Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    log(request.url, log_type='ip', ip=request.remote_addr)
    if 'username' in session.keys():
        return redirect('/')

    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            for user in config.AUTHORIZED_USERS:
                if username == user['username'] and password == user['password']:
                    session['username'] = username
                    log(f'({username}) logged in successfully', log_type='web', ip=request.remote_addr)
                    return redirect('/')
            log(f'({username}) tried to login with wrong password: ({password})', log_type='web', ip=request.remote_addr)
            return render_template('tabs/login.html', message='Incorrect username or password')
        log(f'({request.remote_addr}) tried to login without username or password', log_type='web', ip=request.remote_addr)
        return render_template('tabs/login.html', message='Please enter username and password')
    return render_template('tabs/login.html')

@app.route('/logout')
def logout():
    log(request.url, log_type='ip', ip=request.remote_addr)
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)