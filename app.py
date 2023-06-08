from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, LLMPredictor, ServiceContext
from langchain.chat_models import ChatOpenAI
import textwrap

# Configurar variables de entorno y API key de OpenAI
os.environ["OPENAI_API_KEY"] = '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'

app = Flask(__name__)

# Configuración de la carpeta de carga
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'POST':
        modelo = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'))

        # Indexar el contenido de los PDFs
        pdf = SimpleDirectoryReader('data').load_data()
        service_context = ServiceContext.from_defaults(llm_predictor=modelo)
        index = GPTVectorStoreIndex.from_documents(pdf, service_context=service_context)

        pregunta = request.form['question'] + " Responde en español"
        respuesta = index.as_query_engine().query(pregunta)
        respuestas_envueltas = textwrap.wrap(respuesta.response, width=100)
        return render_template('index.html', respuestas=respuestas_envueltas)
    else:
        return render_template('question.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Comprobar si el archivo está presente en la solicitud
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Si el usuario no selecciona un archivo, el navegador envía una cadena vacía sin nombre de archivo
        if file.filename == '':
            return redirect(request.url)
        # Si el archivo es válido, guardarlo en la carpeta de carga
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Redirigir a la página de inicio después de subir el archivo
            return redirect(url_for('home'))
    else:
        return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
