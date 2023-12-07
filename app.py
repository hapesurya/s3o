import os
import time
from flask import Flask, render_template, request
from requests_html import HTMLSession
from requests.exceptions import RequestException
import markdownify

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    return render_template('copywebsite/index.html')

@app.route('/converttxt', methods=['GET','POST'])
def converttxt():
    if request.method == 'POST':
        list_urls = request.form.get('urls').split('\n')
        css_sel = request.form.get('css_selector')
        folder_baru = request.form.get('folder_baru')
        user_home = os.path.expanduser('~')
        downloads_folder = os.path.join(user_home, 'Downloads')

        session = HTMLSession()

        def save_content_to_file(url, content, content_links):
            cwd = os.path.join(downloads_folder, folder_baru)
            os.makedirs(cwd, exist_ok=True)

            # Modify the line below to use the value in the "url" variable for the file name
            file_name = url.replace('/', '_').replace(':', '_').replace('?', '_') + '.txt'

            with open(os.path.join(cwd, file_name), 'w') as file:
                file.write(str(content) + '\n daftar links di dalam content: \n' + str(content_links))

        results = []

        for i in list_urls:
            print(i)
            status = "Sedang dalam proses"
            retries = 3  # Number of retries
            for attempt in range(retries):
                try:
                    r = session.get(i)
                    content = r.html.find(css_sel, first=True).text
                    content_links = r.html.find(css_sel, first=True).links
                    save_content_to_file(i, content, content_links)
                    status = f"File berhasil disimpan di Folder {downloads_folder}/{folder_baru}"
                    break  # Break the retry loop if successful
                except RequestException as e:
                    print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(5)  # Wait for 5 seconds before retrying
                    else:
                        status = "Gagal. Lewati URL ini"
                        print(f"Max retries reached for {i}. Skipping this URL.")

            time.sleep(5)
            results.append({'url':i, 'status':status})
        
        return render_template('copywebsite/converttxt.html', results=results)
    else:
        return render_template('copywebsite/converttxt.html')

@app.route('/convertmd', methods=['GET','POST'])
def convertmd():
    if request.method == 'POST':
        list_urls = request.form.get('urls').split('\n')
        css_sel = request.form.get('css_selector')
        folder_baru = request.form.get('folder_baru')
        user_home = os.path.expanduser('~')
        downloads_folder = os.path.join(user_home, 'Downloads')

        session = HTMLSession()

        def save_content_to_file(url, content):
            cwd = os.path.join(downloads_folder, folder_baru)
            os.makedirs(cwd, exist_ok=True)

            # Modify the line below to use the value in the "url" variable for the file name
            file_name = url.replace('/', '_').replace(':', '_').replace('?', '_') + '.md'

            with open(os.path.join(cwd, file_name), 'w') as file:
                file.write(str(content))

        results = []

        for i in list_urls:
            print(i)
            status = "Sedang dalam proses"
            retries = 3  # Number of retries
            for attempt in range(retries):
                try:
                    r = session.get(i)
                    content = r.html.find(css_sel, first=True).html
                    html2md = markdownify.markdownify(content, heading_style="ATX")
                    save_content_to_file(i, html2md)
                    status = f"File berhasil disimpan di Folder {downloads_folder}/{folder_baru}"
                    break  # Break the retry loop if successful
                except RequestException as e:
                    print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(5)  # Wait for 5 seconds before retrying
                    else:
                        status = "Gagal. Lewati URL ini"
                        print(f"Max retries reached for {i}. Skipping this URL.")

            time.sleep(5)
            results.append({'url':i, 'status':status})
        
        return render_template('copywebsite/convertmd.html', results=results)
    else:
        return render_template('copywebsite/convertmd.html')

if __name__ == '__main__':
    app.run(debug=True)
