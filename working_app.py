import requests
#from joblib import Parallel, delayed
from flask import (Flask,render_template,request, redirect, url_for)
DEBUG = True
PORT = 8888
HOST = '0.0.0.0'

application = Flask(__name__)

session_ids = None
username = None
password = None

@application.route('/', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		global username
		global password
		username = request.form['username']
		password = request.form['password']
		with requests.get('https://api.browserstack.com/automate/plan.json', auth=(username, password), timeout= (5,5)) as check:
			if check.headers['Status'] == '200 OK':
				return redirect(url_for('upload_file'))
			else:
				error = "Unauthorized to proceed."
	return render_template("login.html", error=error)


@application.route('/upload')
def upload_file():
	return render_template('upload.html')


@application.route('/upload.html', methods=['GET', 'POST'])
def upload_route_summary():
	if request.method == 'POST':
		f = request.files['file']  # Create variable for uploaded file
		# print(f)
		# print(type(f))
		fstring = f.read()   # store the file contents as a string

		data = str(fstring.rstrip())
		global session_ids
		session_ids = data.splitlines()[1:]

		return redirect(url_for('video_url'))

@application.route('/result')
def video_url():
	video_url_exists = []
	for session_id in session_ids:
		session_id_response_data = requests.get(
			'https://api.browserstack.com/automate/sessions/' + session_id + '.json',
			auth=(username, password), timeout=5).json()
		# print(session_id_response_data)
		rendering_data = session_id_response_data['automation_session']
		session_duration = rendering_data.get('duration')
		session_status = rendering_data.get('status')
		session_reason = rendering_data.get('reason')
		device = rendering_data.get('device')
		op_sys = None
		op_sys_version = None
		appium_logs = None
		browser = None
		browser_version = None
		if device is not None:
			# print('Device exists')
			op_sys = rendering_data.get('os')
			op_sys_version = rendering_data.get('os_version')
			appium_logs = rendering_data.get('appium_logs_url')
		else:
			op_sys = rendering_data.get('os')
			op_sys_version = rendering_data.get('os_version')
			browser = rendering_data.get('browser')
			browser_version = rendering_data.get('browser_version')
		har_logs = rendering_data.get('har_logs_url')
		if requests.get(har_logs).headers['Content-Type'] == 'application/json':
			network_logs = True
		else:
			network_logs = False
		video_url = rendering_data.get('video_url')
		# print(video_url)
		with requests.get(video_url, stream=True, timeout=5) as video_url_response_data:
			if video_url_response_data.headers['Content-Type'] == 'video/mp4; charset=utf-8':
				print('video for sessionID ' + session_id + ' exists')
				temp_dict = {
							'session_id': session_id, 'os': op_sys, 'os_version': op_sys_version,
				             'browser': browser, 'browser_version': browser_version,'video_exist': True,
				             'device': device, 'status': session_status, 'reason': session_reason,
				             'duration': session_duration, 'appium_logs': appium_logs, 'network_logs_exist': network_logs
				             }
				video_url_exists.append(temp_dict)
			else:
				print('video for sessionID ' + session_id + ' does not exist')
				temp_dict = {
					'session_id': session_id, 'os': op_sys, 'os_version': op_sys_version,
				    'browser': browser, 'browser_version': browser_version,'video_exist': False,
				    'device': device,'status': session_status, 'reason': session_reason,
				    'duration': session_duration, 'appium_logs': appium_logs, 'network_logs_exist': network_logs
							}
				video_url_exists.append(temp_dict)
	print(video_url_exists)
	return render_template("index.html", output=video_url_exists)


if __name__ == '__main__':
	application.run(debug=DEBUG, host=HOST, port=PORT, threaded=True)
