#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/stef/tasks/tlsauth/env/")
sys.path.insert(0, "/home/stef/tasks/tlsauth/flask_tlsauth/demo")

activate_this = '/home/stef/tasks/tlsauth/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from webapp import app as application
#application.run(debug=True)
