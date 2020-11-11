import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.mosaicplot import mosaic
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols, logit
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import matthews_corrcoef, log_loss
from sklearn.feature_selection import f_classif
import statsmodels.api as sm
import math
import re
import io
import base64

var_cualitativas = ['Sexo', 'Procedencia', 'Trabajo', 'Beca', 'Convocatoria', 'Modalidad', 'Especialidad', 'Abandono']
var_dicotomica = ['Sexo', 'Trabajo', 'Beca', 'Abandono']
var_discretas = ['Edad', 'Preferencia']
var_continuas = ['asignaturas_matriculadas_primer_año', 'asignaturas_presentadas_primer_año', 'asignaturas_aprobadas_primer_año', 
'asignaturas_matriculadas_segundo_año', 'asignaturas_presentadas_segundo_año', 'asignaturas_aprobadas_segundo_año', 'Nota_Admision', 
'Nota_Especifica', 'Nota_Prueba', 'Nota_Bach_Ciclo', 'media_primer_año', 'media_segundo_año', 'Aciertos', 'Fallos', 'Total_prueba']
segundo_curso = ['asignaturas_matriculadas_segundo_año', 'asignaturas_presentadas_segundo_año', 'asignaturas_aprobadas_segundo_año', "media_segundo_año"]

class Bidimensional:
    def __init__(self, v1, v2, l1, l2, t1, t2):
        self.v1 = v1
        self.v2 = v2
        self.l1 = l1
        self.l2 = l2
        self.list1 = self.set_valores(v1, l1)
        self.list2 = self.set_valores(v2, l2)
        self.t1 = t1
        self.t2 = t2
        self.df = self.set_df()
        self.df_freq = pd.crosstab(self.df.var1, self.df.var2)
        self.fix_df_freq(v1, 1)
        self.fix_df_freq(v2, 2)
        self.errores = []
        self.check_comp()
        

    def set_valores(self, var, lista):
        lista = [None if i == '' else i for i in lista]
        if var == 'Especialidad':
            return self.valor_especialidad(lista)
        if re.search("^creditos_matriculados", var):
            return self.valores_matriculados(lista)
        if var == 'Edad':
            lista = [26 if i > 25 else i for i in lista]
        return lista

    def valores_matriculados(self, lista):
        for i in range(len(lista)):
            if lista[i] != None:
                if lista[i] < 30:
                    lista[i] = 6
                elif lista[i] > 60:
                    lista[i] = 66
        return lista

    def valor_especialidad(self, lista):
        acptd = ['Modalidad de Ciencias', 'Ciencias y Tecnología', 'Ciencias de la Salud', 
        'Humanidades y Ciencias Sociales']
        for i in range(len(lista)):
            if lista[i] == None:
                lista[i] = None
            elif re.search("^CF.", lista[i]):
                lista[i] = 'FP'
            elif lista[i] not in acptd:
                lista[i] = 'Otro'
        return lista

    def set_df(self):
        df = pd.DataFrame({'var1': self.list1, 'var2': self.list2})
        df = df.dropna()
        if self.t1 == 'Co':
           df = self.format_Co(df, 1)
        if self.t2 == 'Co':
            df = self.format_Co(df, 2)
        return df

    def format_Co(self, df, num):
        var = 'var' + str(num) 
        l_df = df[var].to_list()
        bins, l_labels = self.set_bins_labels(l_df)
        df[var] = pd.cut(l_df, bins=bins, labels=l_labels, include_lowest=True)
        return df

    def set_bins_labels(self, l_df):
        n = int(math.sqrt(len(l_df)))
        inc = math.ceil((max(l_df)-min(l_df))/n)
        bins = list(range(int(min(l_df)), math.ceil(max(l_df))+inc, inc))
        l_labels = ['(%d, %d]'%(bins[i], bins[i+1]) for i in range(len(bins)-1)]
        return bins, l_labels

    def fix_df_freq(self, v, num): 
        if v == 'Edad':
            self.set_edad(num)
        elif re.search("^creditos_matriculados", v):
            self.set_matriculados(num)

    def set_edad(self, num):
        var = 'var' + str(num)
        l_df = self.df[var].to_list()
        if 26 in l_df:
            if num == 2:
                self.df_freq = self.df_freq.rename({26: 'Mayor de 25'}, axis=1)
            else:
                self.df_freq = self.df_freq.rename({26: 'Mayor de 25'}, axis=0)             

    def set_matriculados(self, num):
        var = 'var' + str(num)
        l_df = self.df[var].to_list()
        if 6 in l_df:
            if num == 2:
                self.df_freq = self.df_freq.rename({6: 'Menos de 30'}, axis=1)
            else:
                self.df_freq = self.df_freq.rename({6: 'Menos de 30'}, axis=0)
        if 66 in l_df:
            if num == 2:
                self.df_freq = self.df_freq.rename({66: 'Más de 60'}, axis=1)
            else:
                self.df_freq = self.df_freq.rename({66: 'Más de 60'}, axis=0)

    def check_comp(self):
        if (self.v1=='Abandono' or self.v2=='Abandono') and (self.v1 in segundo_curso or self.v2 in segundo_curso):
            self.errores.append('No existe información del segundo curso para el abandono.')

    def tabla_contingencia(self):
        lista_final = []
        lista_cabeza = [self.v2]
        for i in range(len(self.df_freq.columns)):
            lista_cabeza.append(str(self.df_freq.columns[i]))
        lista_cabeza.append('Total')
        lista_final.append(lista_cabeza)

        lista_columna = [self.v1]
        lista_final.append(lista_columna)

        for i in range(len(self.df_freq.index)):
            lista_val = [self.df_freq.index[i]]
            total = 0
            for j in range(len(self.df_freq.columns)):
                lista_val.append(self.df_freq.loc[self.df_freq.index[i], self.df_freq.columns[j]])
                total += self.df_freq.loc[self.df_freq.index[i], self.df_freq.columns[j]]
            lista_val.append(total)
            lista_final.append(lista_val)
     
        lista_pie = ['Total']
        for i in range(1, len(lista_val)):
            total = 0
            for j in range(2, len(lista_final)):
                total += lista_final[j][i]
            lista_pie.append(total)
        lista_final.append(lista_pie)
        return lista_final

    def test_independencia(self):
        x = stats.chi2_contingency(self.df_freq, correction=True)
        return {'est':round(x[0], 2), 'p_v':round(x[1], 5), 'g_l':x[2]}

    def medidas_asociacion(self, lista):
        lista_final = []
        chi2 = stats.chi2_contingency(self.df_freq, correction=True)[0]
        n = len(self.df)
        if  'phi' in lista:
           lista_final.append(self.phi_test())
        if 'contingencia' in lista:
            lista_final.append({'Nombre':'Coeficiente C de contingencia', 'Valor':round(math.sqrt(chi2 / (chi2+n)), 4)})
        if 'cramer' in lista:
            lista_final.append({'Nombre':'Coeficiente V de Cramer', 'Valor': round(math.sqrt(chi2 / (n*(min(self.df_freq.shape)-1))), 4)})
        if 'kendall' in lista:
            tau = stats.kendalltau(self.df.var1, self.df.var2)
            lista_final.append({'Nombre':'Tau de Kendall', 't_valor': f'tau: {round(tau[0], 4)}', 'p_valor': f'p_value: {round(tau[1], 4)}'})       
        return lista_final

    def phi_test(self):
        x = len(self.df_freq.columns)
        y = len(self.df_freq.index)
        if x != 2 or y != 2:
            return {'Nombre':'Coeficiente de Φ', 'Valor':'<h6 style="color:Red;">ERROR: Variable no dicotómica</h6>'}
        else:
            a = self.df_freq.loc[self.df_freq.index[0], self.df_freq.columns[0]]
            b = self.df_freq.loc[self.df_freq.index[0], self.df_freq.columns[1]]
            c = self.df_freq.loc[self.df_freq.index[1], self.df_freq.columns[0]]
            d = self.df_freq.loc[self.df_freq.index[1], self.df_freq.columns[1]]
            return {'Nombre':'Coeficiente de Φ', 'Valor':round((a*d-b*c)/(math.sqrt((a+b)*(c+d)*(a+c)*(b+d))), 4)}

    def graficos(self, lista_graf):
        plt.style.use('seaborn-whitegrid')
        plt.switch_backend('SVG')
        plt.cla()
        lista_graf = self.graf_errors(lista_graf)
        if not lista_graf:
            self.errores.append('Gráficos: No se pueden representar.')
            return 'err'
        # Pasar imagen a la vista
        figure_graf = io.BytesIO()
        tam_graf = len(lista_graf)
        if tam_graf == 1:
            fig  = plt.figure(figsize=(10, 8))
        if tam_graf > 1:
            fig = plt.figure(figsize=(10, 14))
        if tam_graf > 2:
            fig = plt.figure(figsize=(10, 20))
        cont = 1
        title = f'Alumnos en función de {self.v1} y {self.v2}'

        if 'adosados' in lista_graf: 
            ax_adosado = fig.add_subplot(tam_graf, 1, cont)
            self.df_freq.plot.bar(ax=ax_adosado, alpha=0.75)
            ax_adosado.set_ylabel('Alumnos')
            ax_adosado.set_xlabel(self.v1)
            plt.setp(ax_adosado.get_xticklabels(), rotation=0, horizontalalignment='center')
            ax_adosado.set_title(title)
            ax_adosado.legend(loc='best', title=self.v2, fontsize='small')
        
            rects = ax_adosado.patches  
            for rect in rects:
                height = rect.get_height()
                ax_adosado.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom')
            cont += 1
    
        if 'apilados' in lista_graf:
            ax_apilado = fig.add_subplot(tam_graf, 1, cont)
            self.df_freq.plot.barh(stacked=True, ax=ax_apilado, alpha=0.75)
            ax_apilado.set_ylabel(self.v1)
            ax_apilado.set_xlabel('Alumnos')
            ax_apilado.set_title(title)

            ax_apilado.legend(ncol=len(ax_adosado.get_xlabel()), loc='best', title=self.v2, fontsize='small')
            cont += 1

        if 'mosaicos' in lista_graf:
            ax_mosaico = fig.add_subplot(tam_graf, 1, cont)
            if self.v1 == 'Aciertos' or self.v1 == 'Fallos' or self.v1 == 'Total_prueba':
                mosaic(self.df_freq.stack(), ax=ax_mosaico, title=title)
            else:
                mosaic(self.df, ['var1', 'var2'], ax=ax_mosaico, title=title)
            ax_mosaico.set_xlabel(self.v1)
            ax_mosaico.set_ylabel(self.v2)
            cont += 1
        
        if 'caja_patilla' in lista_graf:
            ax_box = fig.add_subplot(tam_graf, 1, cont)
            n_df = pd.DataFrame({self.v1: self.l1, self.v2: self.l2})
            n_df = n_df.dropna()
            ax_box.set_xlabel(self.v2)
            ax_box.set_ylabel(self.v1)
            ax_box.set_title(title)
            sns.boxplot(y=self.v1, x=self.v2, data=n_df, ax=ax_box)
            cont += 1

        if 'd_lineal' in lista_graf:
            ax_lineal = fig.add_subplot(tam_graf, 1, cont)
            n_df = pd.DataFrame({self.v1: self.l1, self.v2: self.l2})
            n_df = n_df.dropna()
            sns.regplot(x=self.v1, y=self.v2, data=n_df, ax=ax_lineal)
            ax_lineal.set_title(title)
            cont += 1
        
        if 'd_sigmoide' in lista_graf:
            ax_sigmoide = fig.add_subplot(tam_graf, 1, cont)
            n_df = pd.DataFrame({self.v1: self.l1, self.v2: self.l2})
            n_df = n_df.dropna()
            n_df[self.v2] = pd.get_dummies(n_df[self.v2], drop_first=True)
            y = n_df[self.v2].to_numpy()
            X = np.array(n_df[self.v1]).reshape(-1, 1)
            ax_sigmoide.scatter(X, y, alpha=0.4)
            lr = LogisticRegression()
            lr.fit(X, y)
            ax_sigmoide.plot(np.sort(X, axis=0), lr.predict_proba(np.sort(X, axis=0))[:,1], color='r', label='sigmoide')
            ax_sigmoide.legend(loc=2)
            ax_sigmoide.set_xlabel(self.v1)
            ax_sigmoide.set_ylabel('Probabilidad')
            
        plt.tight_layout(h_pad = 5.0)
        plt.savefig(figure_graf, format="png")
        graf_final = base64.b64encode(figure_graf.getvalue()).decode('utf-8').replace('\n','')
        return(graf_final)

    def graf_errors(self, lista):
        if 'caja_patilla' in lista and (self.t1=='Cu'and self.t2=='Cu'):
            lista.remove('caja_patilla')
            self.errores.append('Diagrama de caja y patilla: Una variable debe ser cualitativa y la otra cuantitativa.') 
        if 'caja_patilla' in lista and ((self.t1 == 'Co' or self.t1 == 'D') and (self.t2 == 'Co' or self.t2 == 'D')):
            lista.remove('caja_patilla')
            self.errores.append('Diagrama de caja y patilla: Una variable debe ser cualitativa y la otra cuantitativa.')
        if 'mosaicos' in lista and (self.t1 == 'Co' or self.t2 == 'Co'):
            lista.remove('mosaicos')
            self.errores.append('Diagrama de mosaicos: Las variables no pueden ser continuas.')
        if 'd_lineal' in lista and ((self.t1 != 'Co' and self.t1 != 'D') or self.t2 != 'Co'):
            lista.remove('d_lineal')
            self.errores.append(f"Gráfico de Dispersión (Ajuste Lineal): La variable X debe ser cuantitativa y la variable respuesta debe ser continua.")
        if 'd_sigmoide' in lista and (self.v1 not in var_continuas or self.v2 not in var_dicotomica):
            lista.remove('d_sigmoide')
            self.errores.append(f"Gráfico de Dispersión (Ajuste Sigmoide). La primera variable debe ser continua y la segunda variable debe ser dicotómica.")    
        return lista

    def regr_lineal(self, lista):
        if (self.t1 != 'Co' and self.t1 != 'D') or self.t2 != 'Co':
            self.errores.append('Regresión Lineal: La variable X debe ser cuantitativa y la variable respuesta debe ser continua.')
            return 'err'
        
        lista_final = []
        df = pd.DataFrame({self.v1: self.l1, self.v2: self.l2})
        df = df.dropna()
        X = df[self.v1]
        Y = df[self.v2]
        X = sm.add_constant(X)
        modelo = sm.OLS(Y, X).fit()
        slope = modelo.params[1]
        intercept = modelo.params[0]
        print(modelo.params)
        lista_final.append({'Nombre': 'Número de observaciones', 'Valor':len(df.index)})
        if 'correlacion' in lista:
            lista_final.append({'Nombre':'Coeficiente de Correlación', 'Valor':round(math.sqrt(modelo.rsquared), 4)})
        if 'determinacion' in lista:
            lista_final.append({'Nombre':'Coeficiente de Determinación', 'Valor':round(modelo.rsquared, 4)})
        if 'anova' in lista:
            model_lm = ols(f"{self.v2} ~  {self.v1}", df).fit()
            anova_results = anova_lm(model_lm)
            print(anova_results)
            total_df = anova_results.iloc[0]["df"] + anova_results.iloc[1]["df"]
            total_sum_sq = round(anova_results.iloc[0]["sum_sq"] + anova_results.iloc[1]["sum_sq"], 5)
            lista_final.append({'Nombre':'Anova', 'Var': self.v1, 'df': anova_results.iloc[0]["df"], 'sum_sq': round(anova_results.iloc[0]["sum_sq"], 5), 'mean_sq': round(anova_results.iloc[0]["mean_sq"], 5), 
            'F': round(anova_results.iloc[0]["F"], 2), 'PR': round(anova_results.iloc[0]["PR(>F)"], 5), 'Var_': 'Residual', 'df_': anova_results.iloc[1]["df"],
            'sum_sq_': round(anova_results.iloc[1]["sum_sq"], 5), 'mean_sq_': round(anova_results.iloc[1]["mean_sq"], 5), 'F_': round(anova_results.iloc[1]["F"], 5), 'PR_': round(anova_results.iloc[1]["F"], 5),
            'total_df': total_df, 'total_sum': total_sum_sq})
        if 'estimacion' in lista:
            lista_final.append({'Nombre':'Estimación sobre β1 y β0', 'slope':f'Slope (β1): {round(slope, 4)}', 'intercept':f'Intercept (β0): {round(intercept, 4)}'})
        if 'contraste' in lista:
            print(modelo.summary())
            lista_final.append({'Nombre': 'Contrastes', 'Var': self.v1, 'coef':round(intercept, 5), 'coef_': round(slope, 5),'std_err': round(modelo.bse[0],5), 'std_err_': round(modelo.bse[1],5),
            't':round(modelo.tvalues[0], 5), 't_':round(modelo.tvalues[1], 5), 'p':round(modelo.pvalues[0], 5), 'p_':round(modelo.pvalues[1], 5) })
        if 'prediccion' in lista:
            if self.is_float(lista[-1]):
                n_df = pd.DataFrame({self.v1: [float(lista[-1])]})
                X_new = n_df[self.v1]
                X_new = sm.add_constant(X_new)
                X_new.insert(0, "const", [1], True) 
                y_pred = modelo.predict(X_new)
                lista_final.append({'Nombre':f'Predicción para: x={lista[-1]}', 'Valor': f'y= <b>{round(y_pred[0], 2)}</b>'})
            else:
                self.errores.append('Regresión Lineal: El valor a predecir debe ser numérico')
        return lista_final
    
    def regr_logistic(self, lista):
        if self.t1 != 'Co' or self.v2 not in var_dicotomica:
            self.errores.append('Regresión Logística: La variable "X" debe ser continua y la variable "Respuesta" debe ser dicotómica.')
            return 'err'
        
        lista_final = []
        df = pd.DataFrame({self.v1: self.l1, self.v2: self.l2})
        df = df.dropna()
        df[self.v2] = pd.get_dummies(df[self.v2], drop_first=True)
        # Modelo
        modelo = logit(f"{self.v2} ~  {self.v1}", df).fit()
        intercept = modelo.params[0]
        slope = modelo.params[1]
        print(modelo.summary())
        lista_final.append({'Nombre': 'Número de observaciones', 'Valor': len(df.index)})        
        if 'estimacion' in lista:
            lista_final.append({'Nombre':'Estimación', 'slope':f'Slope (β1): {round(slope, 4)}', 'intercept':f'Intercept (β0): {round(intercept, 4)}'})
        if 'contraste' in lista:
            lista_final.append({'Nombre': 'Contrastes', 'Var': self.v1, 'coef':round(intercept, 5), 'coef_': round(slope, 5),'std_err': round(modelo.bse[0],5), 'std_err_': round(modelo.bse[1],5),
            'z':round(modelo.tvalues[0], 5), 'z_':round(modelo.tvalues[1], 5), 'p':round(modelo.pvalues[0], 5), 'p_':round(modelo.pvalues[1], 5) })
        if 'verosimilitud' in lista: 
            lista_final.append({'Nombre':'Verosimilitud', 'llf':round(modelo.llf, 4), 'llnull': round(modelo.llnull, 4), 'llr': round(modelo.llr, 4), 
            'llr_pvalue': round(modelo.llr_pvalue, 4) })
        if 'mcfadden' in lista:
            r2 = 1 - modelo.prsquared 
            lista_final.append({'Nombre':'mcfadden', 'V1':round(r2, 5)})
        if 'prediccion' in lista:
            if self.is_float(lista[-1]):
                new_y_sk = pd.DataFrame({self.v1: [float(lista[-1])]})
                resultado = modelo.predict(new_y_sk)
                lista_final.append({'Nombre':f'Predicción para: x={lista[-1]}', 'Valor': f'Probabilidad:  <b>{round(resultado[0], 5)}</b>'})
            else:
                self.errores.append('Regresión Logística: El valor a predecir debe ser numérico')
        return lista_final

    def is_float(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False