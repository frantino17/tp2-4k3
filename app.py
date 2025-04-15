from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import numpy as np
import random
import math
import io
import base64

app = Flask(__name__)

def generar_datos(distribucion, parametros, n):
    if distribucion == 'uniforme':
        a, b = parametros
        return [a + (b - a) * random.random() for _ in range(n)]
    
    elif distribucion == 'exponencial':
        lambd = parametros[0]
        return [-math.log(1 - random.random())/lambd for _ in range(n)]
    
    elif distribucion == 'normal':
        mu, sigma = parametros
        datos = []
        for _ in range((n + 1) // 2):
            u1 = random.random()
            u2 = random.random()
            z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            z1 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
            datos.append(z0 * sigma + mu)
            datos.append(z1 * sigma + mu)
        return datos[:n]

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    error = None
    tabla_frecuencias = None
    datos = None
    distribucion_actual = None

    if request.method == 'POST':
        try:
            # Obtener parámetros del formulario
            distribucion = request.form['distribucion']
            n = int(request.form['n'])
            intervalos = int(request.form['intervalos'])
            
            # Validaciones
            if n <= 0 or n > 1000000:
                raise ValueError("El tamaño de muestra debe estar entre 1 y 1.000.000")
            
            if intervalos not in [10, 15, 20, 30]:
                raise ValueError("Número de intervalos no válido")

            # Parámetros específicos por distribución
            if distribucion == 'uniforme':
                a = float(request.form['a'])
                b = float(request.form['b'])
                if a >= b:
                    raise ValueError("a debe ser menor que b")
                parametros = (a, b)
                
            elif distribucion == 'exponencial':
                lambd = float(request.form['lambda'])
                if lambd <= 0:
                    raise ValueError("Lambda debe ser mayor que 0")
                parametros = (lambd,)
                
            elif distribucion == 'normal':
                mu = float(request.form['mu'])
                sigma = float(request.form['sigma'])
                if sigma <= 0:
                    raise ValueError("Sigma debe ser mayor que 0")
                parametros = (mu, sigma)
                
            else:
                raise ValueError("Distribución no válida")

            # Generar datos
            datos = generar_datos(distribucion, parametros, n)
            
            # Calcular histograma
            counts, bins = np.histogram(datos, bins=intervalos)
            
            # Crear tabla de frecuencias
            tabla = []
            for i in range(len(counts)):
                tabla.append({
                    'intervalo': f"{bins[i]:.4f} - {bins[i+1]:.4f}",
                    'frecuencia': counts[i],
                    'frecuencia_relativa': f"{counts[i]/n:.4f}"
                })
            tabla_frecuencias = tabla
            
            # Crear gráfico
            plt.figure(figsize=(10, 6))
            plt.hist(datos, bins=intervalos, edgecolor='black', alpha=0.7)
            plt.title(f'Histograma ({distribucion.capitalize()})')
            plt.xlabel('Valores')
            plt.ylabel('Frecuencia')
            plt.grid(True)
            
            # Convertir a imagen
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            plot_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            distribucion_actual = distribucion

        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template('index.html', 
                         plot_url=plot_url,
                         error=error,
                         tabla=tabla_frecuencias,
                         datos=datos[:100] if datos else None,
                         distribucion_actual=distribucion_actual)

if __name__ == '__main__':
    app.run(debug=True)
