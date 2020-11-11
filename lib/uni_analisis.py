import pandas as pd
import numpy as np
from scipy import stats
import stemgraphic
import math
import matplotlib.pyplot as plt
import re
import io
import base64

class Unidimensional:
    def __init__(self, var, lista, tipo):
        self.var = var
        self.lista = lista
        self.tipo = tipo
        self.valores = self.set_valores()
        if tipo != 'Co':
            self.indices = self.set_indices()
        self.frec_ab, self.frec_rel, self.porcentaje, self.marca = self.set_freqs()
        if tipo == 'D' or tipo == 'Co':
            self.frec_ab_ac, self.frec_rel_ac = self.set_freqs_ac()
        self.errores = []

    def set_valores(self):
        valores = [x for x in self.lista if x is not None and x != '']
        print(valores)
        if self.var == 'Especialidad':
            valores = self.val_especialidad(valores)
        if self.var == 'Edad':
            valores = [26 if i > 25 else i for i in valores]
        if self.var == 'Aciertos' or self.var == 'Fallos' or self.var == 'Total_prueba':
            valores = pd.array(valores, dtype=int)
        return valores

    def val_especialidad(self, valores):
        aceptadas = ['Modalidad de Ciencias', 'Ciencias y Tecnología', 'Ciencias de la Salud', 'Humanidades y Ciencias Sociales']
        for i in range(len(valores)):
            if re.search("^CF.", valores[i]):
                valores[i] ='FP'
            elif valores[i] not in aceptadas:
                valores[i] = 'Otro'
        return valores

    def set_indices(self):
        indices = pd.value_counts(self.valores).sort_index().keys().tolist()
        if self.var == 'Edad':
            indices = [str(i) for i in indices]
            indices = ['Mayores de 25' if i == '26' else i for i in indices]
        return indices

    def set_freqs(self):
        if self.tipo == 'Cu' or self.tipo == 'D':
            frec_ab = pd.value_counts(self.valores).sort_index().tolist()
            frec_re = (pd.value_counts(self.valores).sort_index() / len(self.valores)).tolist() 
            porcen = (100 * pd.value_counts(self.valores).sort_index() / len(self.valores)).tolist()
            marca = ''
            return frec_ab, frec_re, porcen, marca
        else:
            n = int(math.sqrt(len(self.valores))) # Número de intervalos
            inc = math.ceil((max(self.valores)-min(self.valores))/n) # Tamaño
            bins = list(range(int(min(self.valores)), math.ceil(max(self.valores))+inc, inc))
            ind = (f'({int(min(self.valores))}.0, {int(min(self.valores))+inc}.0]')
            marca = [((bins[i] + bins[i+1]) / 2) for i in range(len(bins)-1)]
            n_indices = pd.cut(self.valores, bins=bins, include_lowest=True).value_counts().keys().tolist()
            n_indices[0] = ind
            self.indices = n_indices
            frec_ab = pd.cut(self.valores, bins=bins, include_lowest=True).value_counts().tolist() 
            frec_re = [(val / len(self.valores)) for val in frec_ab]
            porcen =  [(100 * val / len(self.valores)) for val in frec_ab]
            return frec_ab, frec_re, porcen, marca
    
    def set_freqs_ac(self):
        frec_ab_ac = []
        frec_re_ac = []
        x, y = 0, 0
        for i in self.frec_ab:
            x += i
            frec_ab_ac.append(x)
        for j in self.frec_rel:
            y += j
            frec_re_ac.append(y)
        return frec_ab_ac, frec_re_ac

            
    def tabla_frecuencia(self):
        if self.tipo == 'Cu':
            lista_final = [({'Nombre':' ', 'Abs':'ni', 'Rel':'fi', 'Porcen':'Porcentaje'})]
            for i in range(len(self.indices)):    
                lista_final.append({'Nombre':self.indices[i], 'Abs':self.frec_ab[i], 'Rel':round(self.frec_rel[i], 2), 'Porcen':round(self.porcentaje[i], 2)})
            lista_final.append({"Nombre":'Total', 'Abs':sum(self.frec_ab), 'Rel':round(sum(self.frec_rel), 2), 'Porcen': 100})
        elif self.tipo == 'D':
            lista_final = [({'Nombre':' ', 'Abs':'ni', 'Abs_ac':'Ni', 'Rel':'fi', 'Rel_ac':'Fi', 'Porcen':'Porcentaje'})]
            for i in range(len(self.indices)):    
                lista_final.append({'Nombre':self.indices[i], 'Abs':self.frec_ab[i], 'Abs_ac':self.frec_ab_ac[i], 'Rel':round(self.frec_rel[i], 2), 
                'Rel_ac':round(self.frec_rel_ac[i], 2), 'Porcen':round(self.porcentaje[i], 2)})
            lista_final.append({"Nombre":'Total', 'Abs':sum(self.frec_ab), 'Abs_ac':sum(self.frec_ab), 'Rel':round(sum(self.frec_rel), 2), 'Rel_ac':1.0, 
            'Porcen': 100})
        else:
            print(self.indices)
            lista_final = [({'Nombre':' ', 'Marca':'Xi', 'Abs':'ni', 'Rel':'fi', 'Abs_ac':'Ni', 'Rel_ac':'Fi', 'Porcen':'Porcentaje'})]
            for i in range(len(self.indices)):
                lista_final.append({'Nombre':self.indices[i], 'Marca':self.marca[i] ,'Abs':self.frec_ab[i], 'Rel':round(self.frec_rel[i], 2), 
                'Abs_ac':self.frec_ab_ac[i], 'Rel_ac':round(self.frec_rel_ac[i], 2), 'Porcen':round(self.porcentaje[i], 2)})
            lista_final.append({"Nombre":'Total', 'Marca':'', 'Abs':sum(self.frec_ab), 'Rel':round(sum(self.frec_rel), 2), 'Abs_ac': self.frec_ab_ac[-1], 
            'Rel_ac':round(self.frec_rel_ac[-1], 2), 'Porcen':100})

        return lista_final

    def graficos(self, lista_graf):
        plt.style.use('seaborn-whitegrid')
        plt.switch_backend('SVG')
        plt.cla()
        lista_graf = self.graf_errors(lista_graf)
        tam_graf = len(lista_graf)
        # Pasar imagen a la vista
        figure_graf = io.BytesIO()
        if tam_graf == 1:
            fig  = plt.figure(figsize=(10, 8))
        if tam_graf > 1:
            fig = plt.figure(figsize=(10, 14))
        if tam_graf > 2:
            fig = plt.figure(figsize=(10, 20))
        if tam_graf > 3:
            fig = plt.figure(figsize=(10, 28))
        cont = 1

        if  'pie' in lista_graf:
            lista_explode = [0.2] * len(self.indices)
            ax_sec = fig.add_subplot(tam_graf, 1, cont)
            ax_sec.pie(self.frec_ab, explode=lista_explode, labels=self.indices, autopct='%1.1f%%', startangle=180)
            ax_sec.axis('equal')
            ax_sec.set_title(f'Diagrama de sectores: {self.var}')
            cont += 1

        if 'bar' in lista_graf:
            colors_graf = 'grbmcyk'
            lista_colores = []
            j = 0
            for i in range(len(self.indices)):
                if j >= len(colors_graf):
                    j = 0
                lista_colores.append(colors_graf[j])
                j += 1

            ax_bar = fig.add_subplot(tam_graf, 1, cont)
            ax_bar.bar(self.indices, self.frec_ab, width=0.8, color=lista_colores)
            ax_bar.set_ylabel('Número de Alumnos')
            ax_bar.set_title(f'Diagrama de Barras: {self.var}')
            ax_bar.set_xticklabels(self.indices, rotation=45, horizontalalignment='right')
            for index, value in zip(self.indices, self.frec_ab):
                ax_bar.text(index, value, str(value), color='black', ha='center')              
            cont+=1

        if 'poli' in lista_graf:
            ax_poli = fig.add_subplot(tam_graf, 1, cont)
            ax_poli.plot(np.arange(len(self.indices)), self.frec_ab)
            ax_poli.set_ylabel('Número de Alumnos')
            ax_poli.set_title(f'Polígono de Frecuencias: {self.var}')
            ax_poli.set_xticks(np.arange(len(self.indices)))
            ax_poli.set_xticklabels(self.indices, rotation=45, horizontalalignment='right')
            cont += 1

        if 'histo' in lista_graf:
            ax_hist = fig.add_subplot(tam_graf, 1, cont)
            plt.hist(self.valores, bins=25, facecolor='g', alpha=0.8)
            ax_hist.set_ylabel('Número de Alumnos')
            ax_hist.set_title(f'Histograma: {self.var}')
            cont += 1

        if 'caja' in lista_graf:
            ax_box = fig.add_subplot(tam_graf, 1, cont)
            ax_box.set_title(f'Diagrama de caja y patilla: {self.var}')
            ax_box.set_ylabel(self.var)
            ax_box.boxplot(self.valores)
            cont += 1

        if 'tallo' in lista_graf:                
            ax_tallo = fig.add_subplot(tam_graf, 1, cont)
            ax_tallo.set_title(f'Diagrama de tallo y hoja: {self.var}')
            ax_tallo.set_ylabel(self.var)
            if self.var == 'Aciertos' or self.var == 'Fallos' or self.var == 'Total_prueba':
                stemgraphic.stem_graphic(self.valores, scale=10, ax=ax_tallo)
            else:
                stemgraphic.stem_graphic(self.valores, ax=ax_tallo)
            cont += 1

        plt.tight_layout(h_pad = 5.0)
        plt.savefig(figure_graf, format="png")
        graf_final = base64.b64encode(figure_graf.getvalue()).decode('utf-8').replace('\n','')
        return(graf_final)

    def graf_errors(self, lista):
        if 'bar' in lista and self.tipo == 'Co':
            lista.remove('bar')
            self.errores.append('Diagrama de barras: No acepta variables continuas') 
        if 'pie' in lista and self.tipo == 'Co':
            lista.remove('pie')
            self.errores.append('Diagrama de sectores: No acepta variables continuas')
        if 'histo' in lista and self.tipo == 'Cu':
            lista.remove('histo')
            self.errores.append('Histograma: No se puede representar una variable cualitativa')
        if 'histo' in lista and self.tipo == 'D':
            lista.remove('histo')
            self.errores.append('Histograma: No acepta variables discretas')
        if 'poli' in lista and self.tipo == 'Cu':
            lista.remove('poli')
            self.errores.append('Polígono de frecuencias: No se puede representar una variable cualitativa')
        if 'caja' in lista and self.tipo == 'Cu':
            lista.remove('caja')
            self.errores.append('Diagrama de Caja y Patilla: No se puede representar una variable cualitativa')
        if 'caja' in lista and self.tipo == 'D':
            lista.remove('caja')
            self.errores.append('Diagrama de Caja y Patilla: No acepta variables discretas')
        if 'tallo' in lista and self.tipo == 'Cu':
            lista.remove('tallo')
            self.errores.append('Diagrama Tallo-Hoja: No se puede representar una variable cualitativa')
        if 'tallo' in lista and self.tipo == 'D':
            lista.remove('tallo')
            self.errores.append('Diagrama Tallo-Hoja: No acepta variables discreta')
        return lista

    def estadisticos(self, lista):
        if self.tipo == 'Cu':
            self.errores.append('Las variables cualitativas no aceptan estadísticos.')
            return'err'
        else:
            valores = pd.array(self.valores, dtype=float)
            lista_final = []
            if 'media' in lista:
                lista_final.append({'Nombre':'Media (x̅)', 'Valor':round(np.mean(valores), 2)}) 
            if 'mediana' in lista:
                lista_final.append({'Nombre':'Mediana (M)', 'Valor':np.median(valores)})
            if 'moda' in lista:
                moda = stats.mode(valores)
                lista_final.append({'Nombre':'Moda (Mo)', 'Valor':str(moda[0]).strip("[]")})
            if 'varianza' in lista: 
                lista_final.append({'Nombre':'Varianza', 'Valor':round(np.var(valores), 2)})
            if 'c_varianza' in lista:
                m = np.mean(valores)
                cuavar = sum((xi - m) ** 2 for xi in valores) / (len(valores) - 1)
                lista_final.append({'Nombre':'Cuasi-varianza', 'Valor':round(cuavar, 2)})
            if 'desviacion' in lista:
                lista_final.append({'Nombre':'Desviación Típica', 'Valor':round(np.std(valores), 2)})
            if 'c_desviacion' in lista:
                m = np.mean(valores)
                cuades = math.sqrt(sum((xi - m) ** 2 for xi in valores) / (len(valores) - 1))
                lista_final.append({'Nombre':'Cuasi-desviación Típica', 'Valor':round(cuades, 2)})
            if 'cuartil' in lista:
                lista_final.append({'Nombre':'Cuartiles', 'Valor':(f'Q1: {round(np.quantile(valores, 0.25), 2)},  Q2: {round(np.quantile(valores, 0.5), 2)},  Q3: {round(np.quantile(valores, 0.75), 2)}')})
            if 'percentil' in lista:
                lista_final.append({'Nombre':'Percentiles', 'Valor':(f'P10: {round(np.percentile(valores, 10), 2)},  P50: {round(np.percentile(valores, 50), 2)},  P90: {round(np.percentile(valores, 90), 2)}')})
            if 'asimetria' in lista:
                lista_final.append({'Nombre':'Coeficiente de Asimetría', 'Valor':round(stats.skew(valores), 2)})
            if 'kurtosis' in lista:
                lista_final.append({'Nombre':'Coeficiente de Kurtosis', 'Valor':round(stats.kurtosis(valores), 2)})

            return lista_final