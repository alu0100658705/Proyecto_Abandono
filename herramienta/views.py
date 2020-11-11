from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UnidimensionalForm, BidimensionalForm
from datos_alumnos.models import Grado, Grado_rp30
from lib.uni_analisis import Unidimensional as U
from lib.bi_analisis import Bidimensional as B
from lib.bi_analisis import var_cualitativas, var_discretas, var_continuas

rp_30_vars = ['Aciertos', 'Fallos', 'Total_prueba']

def uni_view(request):
    context = {}
    form = UnidimensionalForm(request.GET)
    context['form'] = form
    if request.method == 'GET':
        if form.is_valid():
            # Obtener: lista con valores
            grado = form.cleaned_data['grado']
            curso = form.cleaned_data['curso']
            var = form.cleaned_data['variables']
            tipo = get_tipo(var)
            var_lista = select_model(grado, curso, var)
            a_ud = U(var, var_lista, tipo)
            # Tabla de frecuencia:
            tabla = form.cleaned_data['tabla_frec']
            if tabla == True:
                context['t_tabla'] = tipo
                context['cabecera'] = "Tabla de frecuencia: " + var
                context['filas'] = a_ud.tabla_frecuencia()
            # Gráficos
            lista_graf = get_graf(form)
            if lista_graf:
                context['show_graf'] = True
                context['graf'] = a_ud.graficos(lista_graf)
            # Descriptivos
            lista_descrip = get_estadisticos(form)
            if lista_descrip:
                results = a_ud.estadisticos(lista_descrip)
                if results != 'err':
                    context['filas_'] = results
                    context['cabecera_'] = "Estadísticos Descriptivos"
            # Errores
            if a_ud.errores:
                a_ud.errores.insert(0, 'ERRORES:')
                context['errores'] = a_ud.errores
    else:
        form = UnidimensionalForm()
    return render(request, 'unidimensional.html', context)


def bi_view(request):
    context = {}
    form = BidimensionalForm(request.GET)
    context['form'] = form
    if request.method == 'GET':
        if form.is_valid():
            grado = form.cleaned_data['grado']
            curso = form.cleaned_data['curso']
            var_1 = form.cleaned_data['variables_1']
            var_2 = form.cleaned_data['variables_2']
            lista_1 = select_model(grado, curso, var_1)
            lista_2 = select_model(grado, curso, var_2)
            tipo_1 = get_tipo(var_1)
            tipo_2 = get_tipo(var_2)
            a_bd = B(var_1, var_2, lista_1, lista_2, tipo_1, tipo_2)
            if not a_bd.errores:
                # Tabla de contingencia
                tabla = form.cleaned_data['tabla_cont']
                if tabla == True:
                    context['cabecera'] = "Tablas de Frecuencias Bidimensionales: " + var_1 + " y " + var_2
                    context['filas'] = a_bd.tabla_contingencia()
                # Test de independencia
                test_ind = form.cleaned_data['independencia']
                if test_ind == True:
                    context['show_indp'] = True
                    context['test_indp'] = a_bd.test_independencia()
                # Medidas de asociación
                lista_asociacion = get_asociacion(form)
                if lista_asociacion:
                    context['c_asoc'] = "Medidas de asociación"
                    context['f_asoc'] = a_bd.medidas_asociacion(lista_asociacion)
                # Gráficos
                lista_graf = get_graf_bi(form)
                if lista_graf:
                    result = a_bd.graficos(lista_graf)
                    if result != 'err':
                        context['show_graf'] = True
                        context['graf'] = result
                # Regresión Lineal
                lista_lineal = get_lineal(form)
                if lista_lineal:
                    result = a_bd.regr_lineal(lista_lineal)
                    if result != 'err':
                        context['r_lineal'] = 'Análisis: Regresión Lineal'
                        context['d_lineal'] = result
                # Regresión Logística
                lista_logist = get_logistic(form)
                if lista_logist:
                    result = a_bd.regr_logistic(lista_logist)
                    if result != 'err':
                        context['r_logistic'] = 'Análisis: Regresión Logística'
                        context['d_logistic'] = result
            # Errores
            if a_bd.errores:
                a_bd.errores.insert(0, 'ERRORES:')
                context['errores'] = a_bd.errores
    else:
        form = BidimensionalForm()
    return render(request, 'bidimensional.html', context)

def select_model(grado, curso, var):
    if var in rp_30_vars:
        alumnos = list(Grado_rp30.objects.values_list(var, flat=True).filter(Grado=grado, Ingreso=curso))
    else:
        alumnos = list(Grado.objects.values_list(var, flat=True).filter(Grado=grado, Ingreso=curso))
    return alumnos
    
def get_tipo(var):
    if var in var_cualitativas:
        return 'Cu'
    elif var in var_discretas:
        return 'D'
    else:
        return 'Co'

def get_graf(form):
    lista_graf = []
    if form.cleaned_data['d_barras'] == True:
        lista_graf.append('bar')
    if form.cleaned_data['d_sectores'] == True:
        lista_graf.append('pie')
    if form.cleaned_data['poligono'] == True:
        lista_graf.append('poli')
    if form.cleaned_data['histograma'] == True:
        lista_graf.append('histo')
    if form.cleaned_data['d_caja'] == True:
        lista_graf.append('caja')
    if form.cleaned_data['d_tallo'] == True:
        lista_graf.append('tallo')
    return lista_graf

def get_estadisticos(form):
    lista_est = []
    if form.cleaned_data['e_media'] == True:
        lista_est.append('media')
    if form.cleaned_data['e_mediana'] == True:
        lista_est.append('mediana')
    if form.cleaned_data['e_moda'] == True:
        lista_est.append('moda')
    if form.cleaned_data['e_varianza'] == True:
        lista_est.append('varianza')
    if form.cleaned_data['e_cuasivar'] == True:
        lista_est.append('c_varianza')
    if form.cleaned_data['e_desviacion'] == True:
        lista_est.append('desviacion')
    if form.cleaned_data['e_cuasidesviacion'] == True:
        lista_est.append('c_desviacion')
    if form.cleaned_data['e_cuartiles'] == True:
        lista_est.append('cuartil')
    if form.cleaned_data['e_percentiles'] == True:
        lista_est.append('percentil')
    if form.cleaned_data['e_asimetria'] == True:
        lista_est.append('asimetria')
    if form.cleaned_data['e_kurtosis'] == True:
        lista_est.append('kurtosis')
    return lista_est

def get_asociacion(form):
    lista_asociacion = []
    if form.cleaned_data['c_phi'] == True:
        lista_asociacion.append('phi')
    if form.cleaned_data['c_contingencia'] == True:
        lista_asociacion.append('contingencia')
    if form.cleaned_data['c_cramer'] == True:
        lista_asociacion.append('cramer')
    if form.cleaned_data['tau_kendall'] == True:
        lista_asociacion.append('kendall')
    return lista_asociacion

def get_graf_bi(form):
    lista_graf = []
    if form.cleaned_data['adosados'] == True:
        lista_graf.append('adosados')
    if form.cleaned_data['apilados'] == True:
        lista_graf.append('apilados')
    if form.cleaned_data['mosaicos'] == True:
        lista_graf.append('mosaicos')
    if form.cleaned_data['caja_patilla'] == True:
        lista_graf.append('caja_patilla')
    if form.cleaned_data['d_lineal'] == True:
        lista_graf.append('d_lineal')
    if form.cleaned_data['d_sigmoide'] == True:
        lista_graf.append('d_sigmoide')
    return lista_graf

def get_lineal(form):
    lista_opt = []
    if form.cleaned_data['c_correlacion'] == True:
        lista_opt.append('correlacion')
    if form.cleaned_data['c_determinacion'] == True:
        lista_opt.append('determinacion')
    if form.cleaned_data['anova'] == True:
        lista_opt.append('anova')
    if form.cleaned_data['contrastes'] == True:
        lista_opt.append('contraste')
    if form.cleaned_data['estimacion'] == True:
        lista_opt.append('estimacion')
    v_predic = form.cleaned_data['prediccion']
    if v_predic:
        lista_opt.append('prediccion')
        lista_opt.append(v_predic)
    return lista_opt

def get_logistic(form):
    lista_opt = []
    if form.cleaned_data['contrastes_logistico'] == True:
        lista_opt.append('contraste')
    if form.cleaned_data['test_verosimilitud'] == True:
        lista_opt.append('verosimilitud')
    if form.cleaned_data['c_mcfadden'] == True:
        lista_opt.append('mcfadden')
    if form.cleaned_data['estimacion_log'] == True:
        lista_opt.append('estimacion')
    v_predic = form.cleaned_data['prediccion_log']
    if v_predic:
        lista_opt.append('prediccion')
        lista_opt.append(v_predic)
    return lista_opt