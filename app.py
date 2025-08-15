# --- Archivo: app.py ---

import os
from flask import Flask, render_template, request, jsonify
import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Modo no interactivo para el servidor
import matplotlib.pyplot as plt
import time

# 1. Configuración inicial de la aplicación Flask
app = Flask(_name_)

# Crear el directorio 'static' si no existe
if not os.path.exists('static'):
    os.makedirs('static')

# 2. Función principal para la página web
@app.route('/')
def index():
    # Renderiza (muestra) el archivo HTML que crearemos después
    return render_template('index.html')

# 3. Ruta que manejará el cálculo de la derivada
@app.route('/derivar', methods=['POST'])
def derivar():
    try:
        # Obtener la función enviada desde la página web
        datos = request.get_json()
        funcion_str = datos['funcion']

        # Símbolo para la variable (usualmente 'x')
        x = sp.symbols('x')

        # Convertir el texto a una expresión matemática que SymPy pueda entender
        # Se hacen reemplazos para que sea más intuitivo (ej: ^ se convierte en **)
        funcion_str_sympy = funcion_str.replace('^', '**')
        expr = sp.sympify(funcion_str_sympy)

        # ¡La magia! Calcular la derivada
        derivada = sp.diff(expr, x)

        # --- Generación de Pasos (Simplificado) ---
        # NOTA: Generar pasos detallados como un humano es extremadamente complejo.
        # Esto es una aproximación que muestra la regla principal utilizada.
        pasos = []
        pasos.append(f"Función Original: $$f(x) = {sp.latex(expr)}$$")
        pasos.append(f"Se pide encontrar la derivada: $$\\frac{d}{dx} \\left( {sp.latex(expr)} \\right)$$")
        
        # Lógica simple para mostrar la regla principal
        if expr.is_Add:
            pasos.append("Aplicando la regla de la suma: $$(u+v)' = u' + v'$$")
        elif expr.is_Mul:
             pasos.append("Aplicando la regla del producto: $$(uv)' = u'v + uv'$$")
        elif expr.is_Pow:
             pasos.append("Aplicando la regla de la potencia o regla de la cadena.")
        elif expr.func == sp.sin or expr.func == sp.cos or expr.func == sp.tan:
             pasos.append("Aplicando la regla de derivación para funciones trigonométricas.")

        pasos.append(f"El resultado de la derivada es: $$f'(x) = {sp.latex(derivada)}$$")

        # --- Generación de la Gráfica ---
        # Convertir la expresión de la derivada a una función numérica para graficar
        derivada_func = sp.lambdify(x, derivada, 'numpy')

        # Crear los valores de x para el gráfico
        x_vals = np.linspace(-10, 10, 400)
        y_vals = derivada_func(x_vals)

        # Crear la gráfica
        plt.figure(figsize=(8, 6))
        plt.plot(x_vals, y_vals, label=f"$f'(x) = {sp.latex(derivada)}$")
        plt.title("Gráfica de la Función Derivada")
        plt.xlabel("x")
        plt.ylabel("f'(x)")
        plt.grid(True)
        plt.legend()
        plt.ylim(-20, 20) # Limitar el eje y para mejor visualización

        # Guardar la gráfica como una imagen en la carpeta 'static'
        # Se usa un timestamp para que el nombre del archivo sea único cada vez
        timestamp = int(time.time())
        ruta_grafica = f'static/plot_{timestamp}.png'
        plt.savefig(ruta_grafica)
        plt.close() # Cerrar la figura para liberar memoria

        # 4. Devolver los resultados a la página web
        return jsonify({
            'success': True,
            'resultado': sp.latex(derivada), # Usamos formato LaTeX para que se vea bonito
            'pasos': "\n".join(pasos),
            'grafica_url': ruta_grafica
        })

    except Exception as e:
        # Si ocurre un error (ej: función mal escrita), se informa al usuario
        return jsonify({
            'success': False,
            'error': f'Error al procesar la función. Asegúrate de que esté bien escrita. (Detalle: {str(e)})'
        })

# 5. Iniciar el servidor web
if _name_ == '_main_':
    app.run(debug=True)
