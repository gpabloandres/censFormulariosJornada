# -*- coding: utf-8 -*-
import os
import sqlite3
import csv
import io
from datetime import datetime
from flask import Flask, request, g, redirect, url_for, Response, render_template

# --- Configuración de la aplicación y la base de datos ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'respuestas_aec.db')

# --- Funciones para gestionar la base de datos ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Se mantiene la tabla original por si se necesita en el futuro
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS respuestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                nombre TEXT,
                rol TEXT,
                comentario_introduccion TEXT,
                comentario_convivencia TEXT,
                comentario_derechos TEXT,
                comentario_obligaciones TEXT,
                comentario_sanciones TEXT,
                comentario_consejo TEXT,
                comentario_limites TEXT
            )
        ''')
        # Se mantiene la tabla de análisis de grupos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analisis_grupos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                docente TEXT,
                materia TEXT,
                curso TEXT,
                grupo TEXT,
                fortalezas TEXT,
                dificultades TEXT,
                estrategias TEXT,
                resultados TEXT,
                necesidades_apoyo TEXT
            )
        ''')
        # Se mantiene la tabla de módulos educativos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modulos_educativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                docente TEXT,
                materia TEXT,
                nivel TEXT,
                duracion TEXT,
                titulo_modulo TEXT,
                tema_modulo TEXT,
                tipo_modulo TEXT,
                objetivos TEXT,
                contenidos TEXT,
                actividades TEXT,
                evaluacion TEXT,
                recursos TEXT
            )
        ''')
        # Nueva tabla para el formulario de diagnóstico EPJA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostico_modulos_epja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                espacio_curricular TEXT,
                curso TEXT,
                nombre_docente TEXT,
                ha_iniciado TEXT,
                porcentaje_completado TEXT,
                razon_no_inicio TEXT,
                razon_no_inicio_otros TEXT,
                preparado_diseno TEXT,
                estimar_carga_horaria TEXT,
                metodologias_epja TEXT,
                formato_modulo TEXT,
                diseno_pedagogico TEXT,
                importancia_ejes_transversales TEXT,
                contenido_prioritario TEXT,
                apoyo_recursos TEXT,
                herramientas_tecnologicas TEXT
            )
        ''')
        db.commit()

# --- Rutas de la aplicación ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Recibe los datos del formulario de diagnóstico EPJA
    espacio_curricular = request.form.get('espacio_curricular')
    curso = request.form.get('curso')
    nombre_docente = request.form.get('nombre_docente')
    ha_iniciado = request.form.get('ha_iniciado')
    porcentaje_completado = request.form.get('porcentaje_completado')
    razon_no_inicio = request.form.get('razon_no_inicio')
    razon_no_inicio_otros = request.form.get('razon_no_inicio_otros')
    preparado_diseno = request.form.get('preparado')
    estimar_carga_horaria = request.form.get('estimar_carga_horaria')
    metodologias_epja = request.form.get('metodologias_epja')
    formato_modulo = request.form.get('formato_modulo')
    diseno_pedagogico = request.form.get('diseno_pedagogico')
    importancia_ejes_transversales = request.form.get('importancia_ejes')
    contenido_prioritario = request.form.get('contenido_prioritario')
    apoyo_recursos = ', '.join(request.form.getlist('apoyo_recursos'))
    herramientas_tecnologicas = request.form.get('herramientas_tecnologicas')

    # Guarda los datos en la nueva tabla
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO diagnostico_modulos_epja (
            fecha, espacio_curricular, curso, nombre_docente, ha_iniciado,
            porcentaje_completado, razon_no_inicio, razon_no_inicio_otros,
            preparado_diseno, estimar_carga_horaria, metodologias_epja,
            formato_modulo, diseno_pedagogico, importancia_ejes_transversales,
            contenido_prioritario, apoyo_recursos, herramientas_tecnologicas
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        espacio_curricular,
        curso,
        nombre_docente,
        ha_iniciado,
        porcentaje_completado,
        razon_no_inicio,
        razon_no_inicio_otros,
        preparado_diseno,
        estimar_carga_horaria,
        metodologias_epja,
        formato_modulo,
        diseno_pedagogico,
        importancia_ejes_transversales,
        contenido_prioritario,
        apoyo_recursos,
        herramientas_tecnologicas
    ))
    db.commit()
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return """
    <div style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
        <h1>¡Gracias por tu participación!</h1>
        <p>Tus respuestas han sido guardadas correctamente.</p>
        <a href='/'>Volver al formulario</a>
    </div>
    """

@app.route('/content_uploaded')
def content_uploaded():
    return """
    <div style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
        <h1>¡Contenido recibido!</h1>
        <p>El contenido del documento ha sido guardado.</p>
        <p>Ahora procederé a procesarlo.</p>
    </div>
    """

@app.route('/upload_content', methods=['POST'])
def upload_content():
    content = request.form.get('doc_content')
    with open('document_content.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    return redirect(url_for('content_uploaded'))

@app.route('/download')
def download_data():
    # Descarga los datos de la tabla original
    return download_table('respuestas', 'respuestas_aec.csv')

@app.route('/download_analisis')
def download_analisis():
    # Descarga los datos de la tabla de análisis de grupos
    return download_table('analisis_grupos', 'analisis_grupos.csv')

@app.route('/download_modulos')
def download_modulos():
    # Descarga los datos de la tabla de módulos
    return download_table('modulos_educativos', 'modulos_educativos.csv')

@app.route('/download_diagnostico')
def download_diagnostico():
    # Descarga los datos de la nueva tabla de diagnóstico
    return download_table('diagnostico_modulos_epja', 'diagnostico_epja.csv')

def download_table(table_name, filename):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    data = cursor.fetchall()
    
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    
    headers = [description[0] for description in cursor.description]
    writer.writerow(headers)
    writer.writerows(data)
    
    response = Response(csv_output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment;filename={filename}'
    return response

if __name__ == '__main__':
    init_db()
    app.run(port=5001, debug=True)