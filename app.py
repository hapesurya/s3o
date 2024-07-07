# versi 2.1
# sudah berhasil download banyak URL, dalam file zip, dengan nama folder kosong.
# Belum berhasil: menampilkan flash message berhasil dan gagal pada frontend.

import io
import logging
import zipfile
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from requests_html import HTMLSession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management with flash

def fetch_content(url: str, css_selector: str) -> Tuple[str, List[str]]:
    """
    Fetch the content and links from a URL using the specified CSS selector.
    """
    session = HTMLSession()
    try:
        response = session.get(url)
        content_element = response.html.find(css_selector, first=True)
        if content_element:
            content = content_element.text
            content_links = list(content_element.absolute_links)
            return content, content_links
        else:
            logger.warning(f"No content found for {url} with selector {css_selector}")
            return "", []
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}")
        return "", []

def save_content_to_zip(url: str, content: str, content_links: List[str], zip_file: zipfile.ZipFile) -> None:
    """
    Save the content and links to a ZIP file.
    """
    safe_url = url.replace('/', '_').replace(':', '_').replace('?', '_').replace('&', '_')
    file_name = f"{safe_url}.txt"
    file_data = f"{content}\n\nLinks found in content:\n{','.join(content_links)}"
    zip_file.writestr(file_name, file_data)

@app.route("/converttxt", methods=["GET", "POST"])
def converttxt_route():
    """
    Flask route handler for fetching content from multiple URLs and returning a ZIP file.
    """
    if request.method == "POST":
        urls = request.form.get('urls').strip().split(',')
        css_selector = request.form.get("css_selector", "").strip()
        output_folder = request.form.get("output_folder", "").strip() or "JAGOSEO" #if empty, we use value JAGOSEO

        zip_data = io.BytesIO()
        successful_fetches = False

        with zipfile.ZipFile(zip_data, mode="w") as zip_file:
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(fetch_content, url.strip(), css_selector): url for url in urls}
                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        content, content_links = future.result()
                        if content:
                            save_content_to_zip(url, content, content_links, zip_file)
                            flash(f"Content fetched successfully from {url}", 'success')
                            successful_fetches = True
                        else:
                            flash(f"No content found for {url} with selector {css_selector}", 'warning')
                    except Exception as e:
                        logger.error(f"Error processing {url}: {e}")
                        flash(f"Error processing {url}: {e}", 'danger')
        
        if successful_fetches:
            zip_data.seek(0)
            flash(f"Content fetched successfully from {url}", 'success')
            return send_file(
                zip_data,
                mimetype="application/zip",
                as_attachment=True,
                download_name=f"{output_folder}.zip"
            )
        else:
            flash("No content was fetched successfully. ZIP file not created.", 'danger')
            return render_template('copywebsite/converttxt.html')
    else:
        return render_template('copywebsite/converttxt.html')

if __name__ == "__main__":
    app.run(debug=True)
