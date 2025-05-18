from flask import Flask, render_template, request, send_file, redirect
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__, template_folder='../templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    termo = request.form.get('termo', '').strip()
    if termo:
        url = f'https://baixafilmetorrent.com/filmes-torrent/?s={termo}'
    else:
        url = 'https://baixafilmetorrent.com/filmes-torrent/'

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    filmes = []
    for bloco in soup.select('.home-post .item'):
        a_img = bloco.find('a', href=True)
        img = a_img.find('img') if a_img else None
        if not a_img or not img:
            continue
        link = a_img['href']
        poster = img.get('src')
        titulo = img.get('alt') or bloco.select_one('.title a').get_text(strip=True)
        filmes.append({'titulo': titulo, 'link': link, 'imagem': poster})
    return render_template('index.html', filmes=filmes, termo=termo)

@app.route('/baixar')
def baixar():
    link = request.args.get('link')
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # procura magnet: ou .torrent
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('magnet:'):
            return redirect(href)
        if href.endswith('.torrent'):
            torrent_url = href
            break
    else:
        return 'Link magnet ou .torrent não encontrado.', 404

    torr_resp = requests.get(torrent_url, stream=True)
    filename = os.path.basename(torrent_url)
    path = os.path.join('/tmp', filename)
    with open(path, 'wb') as f:
        for chunk in torr_resp.iter_content(1024):
            f.write(chunk)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)









