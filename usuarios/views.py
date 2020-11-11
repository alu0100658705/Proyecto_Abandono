from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from .forms import VarForm
from datos_alumnos.forms import UploadFileForm
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponse
from django.urls import reverse
import csv, io
import pandas as pd 
from lib.user_analisis import Analisis as A

@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
	request.session['data_frame'] = None
	data_frame = request.session.get('data_frame','')
	return render(
		request,
		'account/login.html',
		context = {'data_frame':data_frame},
	)

class UserPageView(TemplateView):
	template_name = 'user_space.html'

class AnalisisView(FormView):
	template_name = 'analisis.html'
	form_class = VarForm
	
	def get_context_data(self, *args, **kwargs):
		context = super(AnalisisView, self).get_context_data(*args, **kwargs)
		Analisis = A(self.request.session["data_frame"])
		lista_final = Analisis.get_variables()
		context['lista_variables'] = lista_final[0]
		return context

	def get_form_kwargs(self):
		kwargs = super(AnalisisView, self).get_form_kwargs()
		Analisis = A(self.request.session["data_frame"])
		lista_variables = Analisis.get_variables()
		kwargs['custom_variables'] = lista_variables[1]
		return kwargs

	def form_valid(self, form, **kwargs):
		context = self.get_context_data(**kwargs)
		var = form.cleaned_data['variables']
		Analisis = A(self.request.session["data_frame"])
		context['mostrar'] = True
		context['variable'] = var
		context['resultados'] = Analisis.analizar_variable(var)
		context['graf'] = Analisis.obtener_graf(var)
		return render(self.request, 'analisis.html', context)
	

def cargar_datos(request): 
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			grado = form.cleaned_data['grado']
			curso = form.cleaned_data['curso']
			csv_file1 = request.FILES['f_matriculados']
			csv_file2 = request.FILES['f_abandono']
			if not form.cleaned_data['f_rp30']:
				df =  read_csv(csv_file1, csv_file2)
				RP30 = None
			else: 
				csv_file3 = request.FILES['f_rp30']
				df =  read_csv(csv_file1, csv_file2, csv_file3)
				RP30 = 'active'
			# Variables de sesión
			request.session['data_frame'] = df.to_json()
			request.session['rows_df'] = str(len(df))
			request.session['cols_df'] = str(len(df.columns))
			request.session['size_df'] = str(df.size)
			request.session['variables_validas'] = ["val1", "val2"]
			request.session['grado'] = grado
			request.session['curso'] = curso
			return redirect('/user_space/')
	else:
		form = UploadFileForm()
	return render(request, 'crear_dataframe.html', {'form': form})


def var_view(request):
	context = {}
	form = VarForm(request.GET)
	context['form'] = form
	if request.method == 'GET':
		if form.is_valid():
			print("hola")
	else:
		form = VarForm()
	return render(request, 'analisis.html', context)


def get_key(val, diccionario): 
	for key, value in diccionario.items(): 
		 if val == value: 
			 return key 

def read_csv(f1, f2, f3=None):
	Variables = ['Nota Bach_Ciclo', 'Nota prueba', 'Nota Específica', 'Nota admisión']
	Cabecera = []
	Alumnos = []

	data_matriculados = f1.read().decode('UTF-8')
	data_abandono = f2.read().decode('UTF-8')
	io_matriculados = io.StringIO(data_matriculados)
	io_abandono = io.StringIO(data_abandono)
	cols_alumnos = dict(enumerate(next(csv.reader(io_matriculados))))
	cols_abandono = dict(enumerate(next(csv.reader(io_abandono))))
	lista_datos = [row for row in csv.reader(io_matriculados)]
	lista_abandono = [row for row in csv.reader(io_abandono)]

	for var in cols_alumnos.values():
		if var in Variables:
			Cabecera.append(var)
	
	if f3 != None:
		data_rp30 = f3.read().decode('UTF-8')
		io_rp30 = io.StringIO(data_rp30)
		cols_rp30 = dict(enumerate(next(csv.reader(io_rp30))))
		lista_rp30 = [row for row in csv.reader(io_rp30)]

	
	lista_dni = list(dict.fromkeys([str(lista[get_key('Dni', cols_alumnos)]) for lista in lista_datos]))
	lista_cursos = list(dict.fromkeys([lista[get_key('Curso acta', cols_alumnos)] for lista in lista_datos]))
	lista_cursos.sort()
	exp_1 = 'MAT_' + str(int(lista_cursos[0][2:].replace('-','')) + 101) + '_SN'
	exp_2 = 'MAT_' + str(int(lista_cursos[0][2:].replace('-','')) + 202) + '_SN'
	
	if 'Asignatura' in cols_alumnos.values():
		lista_base = []
		for  lista in lista_datos:
			if lista[get_key('Curso acta', cols_alumnos)] == lista_cursos[0]:
				lista_base.append(lista[get_key('Asignatura', cols_alumnos)+1])
		lista_asignaturas = list(dict.fromkeys(lista_base))
		lista_asignaturas.sort()    

	tam = len(lista_datos)
	i = 0
	for dni in lista_dni:
		alumno = []
		# Abandono
		for sublist in lista_abandono:
			if sublist[get_key('Dni', cols_abandono)] == dni:
				abandono = 'Si' if sublist[get_key(exp_1, cols_abandono)] == 'N' and sublist[get_key(exp_2, cols_abandono)] == 'N' else 'No' 
		alumno.append(abandono)
		# Notas: bach/ciclo, prueba, específica, admisión
		for var in Cabecera:
			alumno.append(float(lista_datos[i][get_key(var, cols_alumnos)].replace(',','.')) if lista_datos[i][get_key(var, cols_alumnos)] != '' else None)
		# RP30
		if f3 != None:
			aciertos = None
			errores = None
			total = None
			for sublist in lista_rp30:
				if sublist[get_key('DNI', cols_rp30)] == dni:
					aciertos = int(sublist[get_key('ACIERTOS', cols_rp30)]) if sublist[get_key('ACIERTOS', cols_rp30)] != '' else None
					errores = int(sublist[get_key('ERRORES', cols_rp30)]) if sublist[get_key('ERRORES', cols_rp30)] != '' else None
					if aciertos == None and errores == None:
						total = None
					else:
						total = int(sublist[get_key('TOTAL PRUEBA', cols_rp30)]) if sublist[get_key('TOTAL PRUEBA', cols_rp30)] != '' else None
			alumno.append(total)
		# Si existe campo: Asignatura
		if 'Asignatura' in cols_alumnos.values():           
			primer_curso = []
			while dni == lista_datos[i][get_key('Dni', cols_alumnos)]:
				curso = lista_datos[i][get_key('Curso acta', cols_alumnos)]
				while curso ==  lista_datos[i][get_key('Curso acta', cols_alumnos)] and dni == lista_datos[i][get_key('Dni', cols_alumnos)]:
					nombre_asignatura = lista_datos[i][get_key('Asignatura', cols_alumnos)+1]
					notas = []
					while lista_datos[i][get_key('Asignatura', cols_alumnos)+1] == nombre_asignatura:
						if lista_datos[i][get_key('Calificación', cols_alumnos)] != 'NP':        
							notas.append(float(lista_datos[i][get_key('Calif. Numérica', cols_alumnos)].replace(',','.')))
						i += 1          
						if i == tam: break
					if curso == lista_cursos[0]:
						if notas:
							primer_curso.append([nombre_asignatura, max(notas)])                                 
						else:
							primer_curso.append([nombre_asignatura, None])
					if i == tam: break
				if i == tam: break             
			# Nota media
			media_notas = []
			for nota in primer_curso:
				if nota[1] != None:
					media_notas.append(nota[1])
			if len(media_notas) != 0:
				media = sum(map(float,media_notas))/float(len(media_notas))
				alumno.append(round(media, 2))
			else:
				alumno.append(None)
			# Notas asignaturas
			for asignatura in lista_asignaturas:
				existe = False
				for asig in primer_curso:
					if asig[0] == asignatura:
						existe = True
						alumno.append(asig[1])
				if not existe:
					alumno.append(None)
			
		Alumnos.append(alumno)

	# Crear Cabecera:
	Cabecera.insert(0, 'Abandono')
	if f3 != None:
		Cabecera.append('RP30: Total')
	Cabecera.append('Nota media 1º año')
	for asignatura in lista_asignaturas:
		Cabecera.append(asignatura)
	
	# Crear dataframe
	df = pd.DataFrame(Alumnos, columns = Cabecera)
	return df