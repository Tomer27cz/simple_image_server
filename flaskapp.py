from flask import Flask, render_template, request, redirect, session
import config
import sys
import json
from time import gmtime, strftime, time
from typing import TypedDict, Union, TYPE_CHECKING

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
@app.context_processor
def inject_globals():
    return dict(logo_url=config.LOGO_URL, favicon_url=config.FAVICON_URL, main_color=config.MAIN_COLOR, main_color_dark=config.MAIN_COLOR_DARK)

# header('Content-Type: image/jpeg');
# header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
# header("Cache-Control: post-check=0, pre-check=0", false);
# header("Pragma: no-cache");

if TYPE_CHECKING:
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
        usage_data: list[dict]

    class Analytics(TypedDict):
        image: list[AnalyticsData]
        link: list[AnalyticsData]

# Data
def get_data() -> dict:
    try:
        with open(f'{config.PATH}db/data.json', 'r') as file:
            data = json.load(file)
    except Exception as e:
        log(e, log_type='error')
        raise e
    return data

# Analytics
def get_analytics() -> dict:
    try:
        with open(f'{config.PATH}db/analytics.json', 'r') as file:
            data = json.load(file)
    except Exception as e:
        log(e, log_type='error')
        raise e
    return data

# Get Data
def get_image() -> str:
    return get_data()['image_url']
def get_link() -> str:
    return get_data()['link_url']

# Get Analytics
def get_current_count() -> tuple:
    analytics: Analytics = get_analytics()
    image_count = analytics['image'][-1]['redirected'] if analytics['image'] else 0
    link_count = analytics['link'][-1]['redirected'] if analytics['link'] else 0
    return image_count, link_count
def get_total_count() -> tuple:
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
            },
            'usage_data': []
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
            },
            'usage_data': []
        })

    try:
        with open(f'{config.PATH}db/data.json', 'w') as file:
            json.dump(data, file, indent=4)
        with open(f'{config.PATH}db/analytics.json', 'w') as file:
            json.dump(analytics, file, indent=4)
    except Exception as e:
        log(e, log_type='error')
        raise e

# Update Analytics
def update_analytics(url_type: Union['image', 'link'], request_data) -> None:
    analytics = get_analytics()
    if url_type == 'image':
        analytics['image'][-1]['redirected'] += 1
    if url_type == 'link':
        analytics['link'][-1]['redirected'] += 1
        usage_data = {
            'url': request_data.url,
            'user_agent': {
                'string': request_data.user_agent.string,
                'platform': request_data.user_agent.platform,
                'browser': request_data.user_agent.browser,
                'version': request_data.user_agent.version,
                'language': request_data.user_agent.language
            },
            'environment': {
                'HTTP_ACCEPT': request_data.environ.get('HTTP_ACCEPT', None),
                'HTTP_ACCEPT_ENCODING': request_data.environ.get('HTTP_ACCEPT_ENCODING', None),
                'HTTP_ACCEPT_LANGUAGE': request_data.environ.get('HTTP_ACCEPT_LANGUAGE', None),
                'HTTP_CONNECTION': request_data.environ.get('HTTP_CONNECTION', None),
                'HTTP_COOKIE': request_data.environ.get('HTTP_COOKIE', None),
                'HTTP_HOST': request_data.environ.get('HTTP_HOST', None),
                'HTTP_SEC_CH_UA': request_data.environ.get('HTTP_SEC_CH_UA', None),
                'HTTP_SEC_CH_UA_MOBILE': request_data.environ.get('HTTP_SEC_CH_UA_MOBILE', None),
                'HTTP_SEC_CH_UA_PLATFORM': request_data.environ.get('HTTP_SEC_CH_UA_PLATFORM', None),
                'HTTP_SEC_FETCH_DEST': request_data.environ.get('HTTP_SEC_FETCH_DEST', None),
                'HTTP_SEC_FETCH_MODE': request_data.environ.get('HTTP_SEC_FETCH_MODE', None),
                'HTTP_SEC_FETCH_SITE': request_data.environ.get('HTTP_SEC_FETCH_SITE', None),
                'HTTP_SEC_FETCH_USER': request_data.environ.get('HTTP_SEC_FETCH_USER', None),
                'HTTP_UPGRADE_INSECURE_REQUESTS': request_data.environ.get('HTTP_UPGRADE_INSECURE_REQUESTS', None),
                'HTTP_USER_AGENT': request_data.environ.get('HTTP_USER_AGENT', None),
                'QUERY_STRING': request_data.environ.get('QUERY_STRING', None),
                'REMOTE_ADDR': request_data.environ.get('REMOTE_ADDR', None),
                'REMOTE_PORT': request_data.environ.get('REMOTE_PORT', None),
                'REQUEST_METHOD': request_data.environ.get('REQUEST_METHOD', None)
            },
            'cookies': request_data.cookies,
            'blueprint': request_data.blueprint,
            'view_args': request_data.view_args,
            'remote_addr': request_data.remote_addr,
            'x_forwarded_for': request_data.headers.get('X-Forwarded-For', request_data.remote_addr),
            'authorization': request_data.headers.get('Authorization', None),
            'ip_info': request_data.headers.get('X-IP-Info', None),
            'path': request_data.path,
            'speed': request_data.headers.get('X-Speed', None),
            'date': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            'timestamp': int(time()),
            'method': request_data.method,
            'scheme': request_data.scheme,
            'host': request_data.host,
            'base_url': request_data.base_url
        }
        analytics['link'][-1]['usage_data'] += [usage_data]

    try:
        with open(f'{config.PATH}db/analytics.json', 'w') as file:
            json.dump(analytics, file, indent=4)
    except Exception as e:
        log(e, log_type='error')
        raise e

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
    log(request.url, log_type='ip', ip=request.remote_addr)
    if 'username' in session.keys():
        username = session['username']
    else:
        username = None
    try:
        count = get_total_count()
        web_url = config.WEB_URL
        data = get_data()
        image_url = data['image_url']
        link_url = data['link_url']
    except Exception as e:
        log(e, log_type='error')
        return render_template('base/500.html', error=e, ), 500

    return render_template('tabs/home.html', username=username, count=count, web_url=web_url, image_url=image_url, link_url=link_url)

# Email Banner
@app.route('/caritas2014')
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
        total = get_total_count()
    except Exception as e:
        log(e, log_type='error')
        return render_template('base/500.html', error=e), 500

    return render_template('tabs/redirect.html', image_url=image_url, link_url=link_url, message=message, username=username, web_url=config.WEB_URL, count=count, total=total)

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
        return render_template('base/500.html', error=e), 500

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
        return render_template('base/500.html', error=e), 500

    return render_template('tabs/analytics.html', data=analytics, username=username, total=total, struct_to_time=struct_to_time, reversed=reversed)


# Redirects
@app.route('/image')
def image():
    try:
        image_url = get_image()
        update_analytics(url_type='image', request_data=request)
    except Exception as e:
        return render_template('base/500.html', error=e), 500

    resp = redirect(image_url)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Cache-Control'] = 'post-check=0, pre-check=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/link')
def link():
    try:
        link_url = get_link()
        update_analytics(url_type='link', request_data=request)
    except Exception as e:
        return render_template('base/500.html', error=e), 500
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


# Page Not Found
@app.errorhandler(404)
def page_not_found(e):
    log(request.url, log_type='ip', ip=request.remote_addr)
    return render_template('base/404.html', error=e), 404

# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    log(request.url, log_type='ip', ip=request.remote_addr)
    return render_template('base/500.html', error=e), 500


if __name__ == '__main__':
    app.run(debug=True)