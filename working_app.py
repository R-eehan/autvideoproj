import requests
from flask import (Flask,render_template,request, redirect, url_for)
DEBUG = True
PORT = 8888
HOST = '0.0.0.0'

application = Flask(__name__)

AUTOMATE_URL = "https://api.browserstack.com/automate/sessions/"
APP_AUTOMATE_URL = "https://api-cloud.browserstack.com/app-automate/sessions/"

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


@application.route('/upload.html', methods=['POST'])
def upload_route_summary():
	if request.method == 'POST':
		if request.files['file'].filename == '':       # Syntax to check for the value of the file uploaded
			error = 'Please select a file to proceed'
			return render_template('upload.html', error=error)  # Do not forget to change HTML code accordingly.
		f = request.files['file']  # Create variable for uploaded file
		fstring = f.read()   # store the file contents as a string
		uploaded_content = fstring.decode("UTF-8")  # EXTREMELY important in Python 3.5 and above
		data = uploaded_content.rstrip()
		global session_ids
		session_ids = data.splitlines()[1:]

		if request.form.get('app_automate') == 'on':
			return redirect(url_for('app_automate'))
		else:
			return redirect(url_for('automate'))

@application.route('/automate-results')
def video_url():
	video_url_exists = []
	for session_id in session_ids:
		session_id_response_data = requests.get(f"{AUTOMATE_URL}{session_id}.json",
			auth=(username, password), timeout=5).json()
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

@application.route('/app-automate-results')
def app_automate():
	video_url_exists = []
	for session_id in session_ids:
		session_id_response_data = requests.get(f"{APP_AUTOMATE_URL}{session_id}.json", auth=(username, password), timeout=10).json()
		rendering_data = session_id_response_data['automation_session']
		session_duration = rendering_data.get('duration')
		session_status = rendering_data.get('status')
		session_reason = rendering_data.get('reason')
		device = rendering_data.get('device')
		op_sys = rendering_data.get('os')
		op_sys_version = rendering_data.get('os_version')
		appium_logs = rendering_data.get('appium_logs_url')
		browser_version = rendering_data.get('browser_version')
		device_logs = rendering_data.get('device_logs_url')
		video_url = rendering_data.get('video_url')
		app_data = session_id_response_data['automation_session']['app_details']
		app_url = app_data.get('app_url')
		app_name = app_data.get('app_name')
		upload_time = app_data.get('uploaded_at')

		with requests.get(video_url, stream=True, timeout=5) as video_url_response_data:
			if video_url_response_data.headers['Content-Type'] == 'video/mp4; charset=utf-8':
				print('video for sessionID ' + session_id + ' exists')
				temp_dict = {
							'session_id': session_id, 'os': op_sys, 'os_version': op_sys_version,
							'app_name': app_name, 'app_url': app_url, 'upload_time': upload_time,
				            'browser_version': browser_version,'video_exist': True,
				             'device': device, 'status': session_status, 'reason': session_reason,
				             'duration': session_duration, 'appium_logs': appium_logs, 'device_logs': device_logs
				             }
				video_url_exists.append(temp_dict)
			else:
				print('video for sessionID ' + session_id + ' does not exist')
				temp_dict = {
					'session_id': session_id, 'os': op_sys, 'os_version': op_sys_version,
					'app_name': app_name, 'app_url': app_url, 'upload_time': upload_time,
				    'browser_version': browser_version,'video_exist': False,
				    'device': device,'status': session_status, 'reason': session_reason,
				    'duration': session_duration, 'appium_logs': appium_logs, 'device_logs': device_logs
							}
				video_url_exists.append(temp_dict)
	print(video_url_exists)
	return render_template("app_automate.html", output=video_url_exists)

if __name__ == '__main__':
	application.run(debug=DEBUG, host=HOST, port=PORT, threaded=True)
