# Simple Redirect Server

---

###### Developed for [Oblastní charita Pardubice](https://pardubice.charita.cz)

### Configuration

Create a file called `config.py` in the main directory and fill it out

```python
# config.py
# Absolute path to the directory where the application is located
PATH = '' # has to end with /

# List of users who can access the web interface
AUTHORIZED_USERS = [{'username': 'user', 'password': '1234'}, {'username': 'user2', 'password': '4321'}]

# Secret key for Flask
SECRET_KEY = 'secret'

# Your web server's IP address / domain name
WEB_URL = 'https://example.com'

# Logo
LOGO_URL = 'https://example.con/logo.png'
FAVICON_URL = 'https://example.com/logo.svg'

# Color
MAIN_COLOR = '#b91919' # Main color
MAIN_COLOR_DARK = '#961414' # Main color dark (hover)
```