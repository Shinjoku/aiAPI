# -*- coding: utf-8 -*-

from app import app

if __name__ == '__main__':
    # Running app in debug mode
    app.run(debug=True)
    # app.run(host = '172.24.32.43', port=8080, debug=True)