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
import json
import re
import io
import base64

class Analisis:
    def __init__(self, json_fich):
        self.datos = json.loads(json_fich) 
        self.v_abandono = 'Abandono'
        self.l_abandono = self.datos.get(self.v_abandono, '')


    def crear_dataframe(self, v2, l2):
        df = pd.DataFrame({v2: l2, self.v_abandono: self.l_abandono})
        df[self.v_abandono] = pd.get_dummies(df[self.v_abandono], drop_first=True)
        df = df.dropna() 
        return df

    def get_variables(self):
        lista_final = []
        lista_variables = []
        del self.datos['Abandono']
        for clave in self.datos.keys():
            l_clave = self.datos.get(clave, '')
            df = self.crear_dataframe(clave, l_clave)
            resp = self.set_validez(df, clave)
            if resp != None:
                lista_variables.append(clave)
                lista_final.append({'Nombre':clave, 'P_valor': f'{resp[0]}: ({round(resp[1], 5)})'})
        return lista_final, lista_variables

    def set_validez(self, df, n_clave):
        if len(df) < 10:
            return None
        else:
            Xtrain = df[[n_clave]] 
            ytrain = df[[self.v_abandono]]
            modelo = sm.Logit(ytrain, Xtrain).fit(method='newton')
            print(modelo.summary())
            p_valor = modelo.pvalues.to_list()
            if p_valor[0] < 0.05:
                return ['Si', p_valor[0]]
            else:
                return ['No', p_valor[0]]

    def analizar_variable(self, variable):
        lista_dict = []
        l_variable = self.datos.get(variable, "")
        df = self.crear_dataframe(variable, l_variable)
        Xtrain = df[[variable]] 
        ytrain = df[[self.v_abandono]]
        modelo = sm.Logit(ytrain, Xtrain).fit(method='newton')
        resultados_predict = modelo.predict(Xtrain)
        var_valores = df[variable].to_list()
        pred_values = resultados_predict.to_list()
        for i in range(0, len(var_valores)):
            lista_dict.append({'Var': var_valores[i], 'Probabilidad': round(pred_values[i], 5)})
        lista_final = sorted(lista_dict, key=lambda k: k['Probabilidad'], reverse=True) 
        return lista_final

    def obtener_graf(self, variable):
        plt.style.use('seaborn-whitegrid')
        plt.switch_backend('SVG')
        plt.cla()
        figure_graf = io.BytesIO()
        fig  = plt.figure(figsize=(10, 10))

        # Caja/Patilla
        ax_box = fig.add_subplot(2, 1, 1)
        n_df = pd.DataFrame({variable: self.datos.get(variable, ""), self.v_abandono: self.l_abandono})
        n_df = n_df.dropna()
        ax_box.set_xlabel(self.v_abandono)
        ax_box.set_ylabel(variable)
        ax_box.set_title(f"Diagra de Caja y Patilla para el abandono y {variable}")
        sns.boxplot(y=variable, x=self.v_abandono, data=n_df, ax=ax_box)

        # Sigmoide
        ax_sigmoide = fig.add_subplot(2, 1, 2)
        n_df = self.crear_dataframe(variable, self.datos.get(variable, ""))
        y = n_df[self.v_abandono].to_numpy()
        X = np.array(n_df[variable]).reshape(-1, 1)
        ax_sigmoide.scatter(X, y, alpha=0.4)
        lr = LogisticRegression()
        lr.fit(X, y)
        ax_sigmoide.plot(np.sort(X, axis=0), lr.predict_proba(np.sort(X, axis=0))[:,1], color='r', label='sigmoide')
        ax_sigmoide.legend(loc=2)
        ax_sigmoide.set_xlabel(variable)
        ax_sigmoide.set_ylabel('Probabilidad')

        plt.tight_layout(h_pad = 5.0)
        plt.savefig(figure_graf, format="png", transparent=True)
        graf_final = base64.b64encode(figure_graf.getvalue()).decode('utf-8').replace('\n','')
        return graf_final
