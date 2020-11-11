from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm, ShowDataForm
from .models import Grado, Grado_rp30
import csv, io

def upload_file(request): 
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            grado = form.cleaned_data['grado']
            curso = form.cleaned_data['curso']
            csv_file1 = request.FILES['f_matriculados']
            csv_file2 = request.FILES['f_abandono']
            if not form.cleaned_data['f_rp30']:
                datos =  read_csv(csv_file1, csv_file2)
                RP30 = None
            else: 
                csv_file3 = request.FILES['f_rp30']
                datos =  read_csv(csv_file1, csv_file2, csv_file3)
                RP30 = 'active'
            create_table(grado, curso, datos[0], datos[1], RP30)
            return HttpResponse('<h2>Archivos subidos con éxito.</h2>')
    else:
        form = UploadFileForm()
    return render(request, 'subir_datos.html', {'form': form})


def get_key(val, diccionario): 
    for key, value in diccionario.items(): 
         if val == value: 
             return key 

def read_csv(f1, f2, f3=None):
    Alumnos = []
    data_matriculados = f1.read().decode('UTF-8')
    data_abandono = f2.read().decode('UTF-8')
    io_matriculados = io.StringIO(data_matriculados)
    io_abandono = io.StringIO(data_abandono)
    cols_alumnos = dict(enumerate(next(csv.reader(io_matriculados))))
    cols_abandono = dict(enumerate(next(csv.reader(io_abandono))))

    if f3 != None:
        data_rp30 = f3.read().decode('UTF-8')
        io_rp30 = io.StringIO(data_rp30)
        cols_rp30 = dict(enumerate(next(csv.reader(io_rp30))))
        lista_rp30 = [row for row in csv.reader(io_rp30)]

    lista_datos = [row for row in csv.reader(io_matriculados)]
    lista_abandono = [row for row in csv.reader(io_abandono)]

    lista_dni = list(dict.fromkeys([str(lista[get_key('Dni', cols_alumnos)]) for lista in lista_datos]))
    lista_cursos = list(dict.fromkeys([lista[get_key('Curso acta', cols_alumnos)] for lista in lista_datos]))
    lista_asignaturas = list(dict.fromkeys([lista[get_key('Asignatura', cols_alumnos)+1] for lista in lista_datos]))
    
    lista_cursos.sort()
    exp_1 = 'MAT_' + str(int(lista_cursos[0][2:].replace('-','')) + 101) + '_SN'
    exp_2 = 'MAT_' + str(int(lista_cursos[0][2:].replace('-','')) + 202) + '_SN'

    tam = len(lista_datos)
    i = 0
    for dni in lista_dni:
        dict_alu = {'Sexo': lista_datos[i][get_key('Sexo', cols_alumnos)],
                    'Edad': lista_datos[i][get_key('Edad año ingreso al estudio', cols_alumnos)],
                    'Procedencia': lista_datos[i][get_key('Isla procedencia', cols_alumnos)],
                    'Becado': lista_datos[i][get_key('Becario', cols_alumnos)],
                    'Convocatoria': lista_datos[i][get_key('Conv. Preinsc.', cols_alumnos)],
                    'Modalidad': lista_datos[i][get_key('Modalidad', cols_alumnos)],
                    'Especialidad': lista_datos[i][get_key('Especialidad', cols_alumnos)+1]
                    }
        # Trabajo:
        dict_alu['Trabajo'] = 'No' if lista_datos[i][get_key('Ocpación alumno', cols_alumnos)] == 'No aplica' or lista_datos[i][get_key('Ocpación alumno', cols_alumnos)] == 'No consta' else 'Si'
        # Preferencia
        dict_alu['Preferencia'] = int(lista_datos[i][get_key('Preferencia', cols_alumnos)]) if lista_datos[i][get_key('Preferencia', cols_alumnos)] != '' else None
        # Nota Bach/Ciclo
        dict_alu['Nota_Bach'] = float(lista_datos[i][get_key('Nota Bach / Ciclo', cols_alumnos)].replace(',','.')) if lista_datos[i][get_key('Nota Bach / Ciclo', cols_alumnos)] != '' else None
        # Nota Prueba (Ebau)
        dict_alu['Nota_prueba'] = float(lista_datos[i][get_key('Nota prueba', cols_alumnos)].replace(',','.')) if lista_datos[i][get_key('Nota prueba', cols_alumnos)] != '' else None 
        # Nota específica (Ebau)
        dict_alu['Nota_esp'] = float(lista_datos[i][get_key('Nota Específica', cols_alumnos)].replace(',','.')) if lista_datos[i][get_key('Nota Específica', cols_alumnos)] != '' else None
        # Nota admisión
        dict_alu['Admision'] = float(lista_datos[i][get_key('Nota admisión', cols_alumnos)].replace(',','.')) if lista_datos[i][get_key('Nota admisión', cols_alumnos)] != '' else None 

        for sublist in lista_abandono:
            if sublist[get_key('Dni', cols_abandono)] == dni:
                if sublist[get_key(exp_1, cols_abandono)] == 'N' and sublist[get_key(exp_2, cols_abandono)] == 'N':
                    dict_alu['Abandono'] = 'Si'
                else:
                    dict_alu['Abandono'] = 'No'

        if f3 != None:
            dict_alu['aciertos'] = None
            dict_alu['errores'] = None
            dict_alu['total'] = None
            for sublist in lista_rp30:
                if sublist[get_key('DNI', cols_rp30)] == dni:
                    dict_alu['aciertos'] = int(sublist[get_key('ACIERTOS', cols_rp30)]) if sublist[get_key('ACIERTOS', cols_rp30)] != '' else None
                    dict_alu['errores'] = int(sublist[get_key('ERRORES', cols_rp30)]) if sublist[get_key('ERRORES', cols_rp30)] != '' else None
                    dict_alu['total'] = int(sublist[get_key('TOTAL PRUEBA', cols_rp30)]) if sublist[get_key('TOTAL PRUEBA', cols_rp30)] != '' else None
                   
        contador = 0
        lista_curso1 = []
        lista_curso2 = []
        while dni == lista_datos[i][get_key('Dni', cols_alumnos)]:
            curso = lista_datos[i][get_key('Curso acta', cols_alumnos)]
            asignaturas_matriculadas = 0
            asignaturas_presentadas = 0
            asignaturas_aprobadas = 0

            while curso == lista_datos[i][get_key('Curso acta', cols_alumnos)] and dni == lista_datos[i][get_key('Dni', cols_alumnos)]:
                asignaturas_matriculadas += 1
                n_asignatura = lista_datos[i][get_key('Asignatura', cols_alumnos)+1]
                notas = []
                while lista_datos[i][get_key('Asignatura', cols_alumnos)+1] == n_asignatura:
                    if lista_datos[i][get_key('Calificación', cols_alumnos)] != 'NP':        
                        notas.append(float(lista_datos[i][get_key('Calif. Numérica', cols_alumnos)].replace(',','.')))
                    i += 1
                    if i == tam: break
                if notas: 
                    asignaturas_presentadas += 1
                    if max(notas) >= 5.0:
                        asignaturas_aprobadas += 1
                    lista_curso1.append([n_asignatura, max(notas)]) if curso == lista_cursos[0] else lista_curso2.append([n_asignatura, max(notas)])        
                else:
                    lista_curso1.append([n_asignatura, None]) if curso == lista_cursos[0] else lista_curso2.append([n_asignatura, None])
                if i == tam: break
            contador += 1
            if contador == 1:
                dict_alu['asignaturas_matriculadas_primero'] = asignaturas_matriculadas
                dict_alu['asignaturas_presentadas_primero'] = asignaturas_presentadas
                dict_alu['asignaturas_aprobadas_primero'] = asignaturas_aprobadas
            else:
                dict_alu['asignaturas_matriculadas_segundo'] = asignaturas_matriculadas
                dict_alu['asignaturas_presentadas_segundo'] = asignaturas_presentadas
                dict_alu['asignaturas_aprobadas_segundo'] = asignaturas_aprobadas
            if i == tam: break             
                
        if contador == 1:
            dict_alu['asignaturas_matriculadas_segundo'] = None
            dict_alu['asignaturas_presentadas_segundo'] = None
            dict_alu['asignaturas_aprobadas_segundo'] = None

        dict_alu['notas'] = []
        for asignatura in lista_asignaturas:
            nota_f = []
            for asig_c1 in lista_curso1:
                if asig_c1[0] == asignatura:
                    if asig_c1[1] != None:
                        nota_f.append(asig_c1[1])
            for asig_c2 in lista_curso2:
                if asig_c2[0] == asignatura:
                    if asig_c2[1] != None:
                        nota_f.append(asig_c2[1])
            if nota_f:
                if len(nota_f) == 2: 
                    dict_alu['notas'].append(nota_f[-1])
                else:
                    dict_alu['notas'].append(nota_f[0])
            else:
                dict_alu['notas'].append(None)

        media_notas = []
        for nota in lista_curso1:
            if nota[1] != None:
                media_notas.append(nota[1])
        if len(media_notas) != 0:
            media = sum(map(float,media_notas))/float(len(media_notas))
            dict_alu['Nota_media_1'] = round(media, 2)
        else:
            dict_alu['Nota_media_1'] = None

        media_notas.clear()
        for nota in lista_curso2:
            if nota[1] != None:
                media_notas.append(nota[1])
        if len(media_notas) != 0:
            media = sum(map(float,media_notas))/float(len(media_notas))
            dict_alu['Nota_media_2'] = round(media, 2)
        else:
            dict_alu['Nota_media_2'] = None
        
        Alumnos.append(dict_alu)

    return Alumnos, lista_asignaturas

def create_table(grado, curso, lista, lista_asignaturas, RP30):
    """
    b_grado = Grado.objects.raw('SELECT alumno_id FROM datos_alumnos_grado')
    b_grado_rp30 = Grado.objects.raw('SELECT alumno_id FROM datos_alumnos_grado_rp30')
    alumnos_id_grado =  max(b_grado) if len(b_grado) > 0 else 0 
    alumnos_id_grado_rp = max(b_grado_rp30) if len(b_grado_rp30) > 0 else 0
    id_act = max(alumnos_id_grado, alumnos_id_grado_rp)
    """
    if RP30 is None:
        for alumno in lista:
            created = Grado.objects.create(
                Grado = grado,
                Ingreso = curso,
                Sexo = alumno['Sexo'],
                Edad = alumno['Edad'], 
                Procedencia = alumno['Procedencia'],
                Trabajo = alumno['Trabajo'],
                Beca = alumno['Becado'],
                Convocatoria = alumno['Convocatoria'],
                Preferencia = alumno['Preferencia'],
                Modalidad = alumno['Modalidad'],
                Especialidad = alumno['Especialidad'],
                Nota_Bach_Ciclo = alumno['Nota_Bach'],
                Nota_Prueba = alumno['Nota_prueba'],
                Nota_Especifica = alumno['Nota_esp'],
                Nota_Admision = alumno['Admision'],
                Abandono = alumno['Abandono'],
                asignaturas_matriculadas_primer_año = alumno['asignaturas_matriculadas_primero'],
                asignaturas_presentadas_primer_año = alumno['asignaturas_presentadas_primero'],
                asignaturas_aprobadas_primer_año = alumno['asignaturas_aprobadas_primero'],
                asignaturas_matriculadas_segundo_año = alumno['asignaturas_matriculadas_segundo'],
                asignaturas_presentadas_segundo_año = alumno['asignaturas_presentadas_segundo'],
                asignaturas_aprobadas_segundo_año = alumno['asignaturas_aprobadas_segundo'],
                media_primer_año = alumno['Nota_media_1'],
                media_segundo_año = alumno['Nota_media_2'],
                asignaturas = lista_asignaturas,
                notas = alumno['notas'],
            )

    else:
        for alumno in lista:
            created = Grado_rp30.objects.create(
                Grado = grado,
                Ingreso = curso,
                Sexo = alumno['Sexo'],
                Edad = alumno['Edad'], 
                Procedencia = alumno['Procedencia'],
                Trabajo = alumno['Trabajo'],
                Beca = alumno['Becado'],
                Convocatoria = alumno['Convocatoria'],
                Preferencia = alumno['Preferencia'],
                Modalidad = alumno['Modalidad'],
                Especialidad = alumno['Especialidad'],
                Nota_Bach_Ciclo = alumno['Nota_Bach'],
                Nota_Prueba = alumno['Nota_prueba'],
                Nota_Especifica = alumno['Nota_esp'],
                Nota_Admision = alumno['Admision'],
                Abandono = alumno['Abandono'],
                asignaturas_matriculadas_primer_año = alumno['asignaturas_matriculadas_primero'],
                asignaturas_presentadas_primer_año = alumno['asignaturas_presentadas_primero'],
                asignaturas_aprobadas_primer_año = alumno['asignaturas_aprobadas_primero'],
                asignaturas_matriculadas_segundo_año = alumno['asignaturas_matriculadas_segundo'],
                asignaturas_presentadas_segundo_año = alumno['asignaturas_presentadas_segundo'],
                asignaturas_aprobadas_segundo_año = alumno['asignaturas_aprobadas_segundo'],
                media_primer_año = alumno['Nota_media_1'],
                media_segundo_año = alumno['Nota_media_2'],
                Aciertos = alumno['aciertos'],
                Fallos = alumno['errores'],
                Total_prueba = alumno['total'],
                asignaturas = lista_asignaturas,
                notas = alumno['notas'],
            )

def show_data(request):
    context = {}
    form = ShowDataForm(request.GET)
    context['form'] = form
    if request.method == 'GET':
        if form.is_valid():
            grado = form.cleaned_data['grado']
            curso = form.cleaned_data['curso']
            rp_30 = form.cleaned_data['rp_30']
            if rp_30 == True:
                alumnos = Grado_rp30.objects.raw('SELECT * FROM datos_alumnos_grado_rp30 WHERE "Ingreso" = %s AND "Grado" = %s', [curso, grado])
                context['rp_30'] = 'On'
            else:
                alumnos = Grado.objects.raw('SELECT * FROM datos_alumnos_grado WHERE "Ingreso" = %s AND "Grado" = %s', [curso, grado])
                context['rp_30'] = 'Off'
            context['alumnos'] = alumnos
            context['mensaje'] = 'No se encontraron registros'
    else:
        form = ShowDataForm()
    return render(request, 'mostrar_datos.html', context)