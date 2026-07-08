from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import json

app = Flask(__name__)

PASTA_DOWNLOADS = "temp"
ARQUIVO_HISTORICO = "historico.json"

os.makedirs(PASTA_DOWNLOADS, exist_ok=True)


def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r") as f:
            return json.load(f)
    return []


def salvar_historico(lista):
    with open(ARQUIVO_HISTORICO, "w") as f:
        json.dump(lista, f)


@app.route("/", methods=["GET", "POST"])
def index():
    downloads = carregar_historico()

    if request.method == "POST":
        url = request.form["url"]

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(PASTA_DOWNLOADS, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get("title", "audio")
            thumb = info.get("thumbnail")  # <-- Adicionado
            arquivo = ydl.prepare_filename(info)
            arquivo_mp3 = os.path.splitext(arquivo)[0] + ".mp3"

        downloads.insert(0, {
            "titulo": titulo,
            "arquivo": arquivo_mp3,
            "thumb": thumb
        })

        downloads = downloads[:5]
        salvar_historico(downloads)

        return send_file(arquivo_mp3, as_attachment=True)

    return render_template("index.html", downloads=downloads)


@app.route("/download/<path:arquivo>")
def download(arquivo):
    return send_file(arquivo, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)