from django import forms

GRADO_CHOICES = (
    ("","----------------------------------------------------------------------"),
    ("Administración", "Grado en Administración y Dirección de Empresas"),
    ("Antropología", "Grado en Antropología Social y Cultural"),
    ("Arquitectura Técnica", "Grado en Arquitectura Técnica"),
    ("Bellas Artes", "Grado en Bellas Artes"),
    ("Biología", "Grado en Biología"),
    ("Ciencias Ambientales", "Grado en Ciencias Ambientales"),
    ("Conservación", "Grado en Conservación y Restauración de Bienes Culturales"),
    ("Contabilidad", "Grado en Contabilidad y Finanzas"),
    ("Derecho", "Grado en Derecho"),
    ("Diseño", "Grado en Diseño"),
    ("Economía", "Grado en Economía"),
    ("Enfermería", "Grado en Enfermería"),
    ("Enfermería (EUENSC)", "Grado en Enfermería (EUENSC)"),
    ("Español", "Grado en Español: Lengua y Literatura"),
    ("Estudios Clásicos", "Grado en Estudios Clásicos"),
    ("Estudios Francófonos", "Grado en Estudios Francófonos Aplicados"),
    ("Estudios Ingleses", "Grado en Estudios Ingleses"),
    ("Farmacia", "Grado en Farmacia"),
    ("Filosofía", "Grado en Filosofía"),
    ("Física", "Grado en Física"),
    ("Fisioterapia", "Grado en Fisioterapia"),
    ("Geografía", "Grado en Geografía y Ordenación del Territorio"),
    ("Historia", "Grado en Historia"),
    ("Historia del Arte", "Grado en Historia del Arte"),
    ("Ingeniería Agrícola", "Grado en Ingeniería Agrícola y del Medio Rural"),
    ("Ingeniería Civil", "Grado en Ingeniería Civil"),
    ("Ingeniería Electrónica", "Grado en Ingeniería Electrónica Industrial y Automática"),
    ("Ingeniería Informática", "Grado en Ingeniería Informática"),
    ("Ingeniería Mecánica", "Grado en Ingeniería Mecánica"),
    ("Ingeniería Química", "Grado en Ingeniería Química Industrial"),
    ("Logopedia", "Grado en Logopedia"),
    ("Maestro en Educación Infantil", "Grado en Maestro en Educación Infantil"),
    ("Maestro en Educación Primaria", "Grado en Maestro en Educación Primaria"),
    ("Matemáticas", "Grado en Matemáticas"),
    ("Medicina", "Grado en Medicina"),
    ("Náutica", "Grado en Náutica y Transporte Marítimo"),
    ("Nutrición", "Grado en Nutrición Humana y Dietética"),
    ("Pedagogía", "Grado en Pedagogía"),
    ("Periodismo", "Grado en Periodismo"),
    ("Psicología", "Grado en Psicología"),
    ("Química", "Grado en Química"),
    ("Relaciones Laborales", "Grado en Relaciones Laborales"),
    ("Sociología", "Grado en Sociología"),
    ("Tecnologías Marinas", "Grado en Tecnologías Marinas"),
    ("Trabajo Social", "Grado en Trabajo Social"),
    ("Turismo", "Grado en Turismo"),
)

CURSO_CHOICES = (
    ("", "---------"),
    ("2012/2013", "2012/2013"),
    ("2013/2014", "2013/2014"),
    ("2014/2015", "2014/2015"),
    ("2015/2016", "2015/2016"),
    ("2016/2017", "2016/2017"),
    ("2017/2018", "2017/2018"),
    ("2018/2019", "2018/2019"),
    ("2019/2020", "2019/2020"),
)

class UploadFileForm(forms.Form):
    grado = forms.ChoiceField(label='Grado', choices=GRADO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form'}))
    curso = forms.ChoiceField(label='Curso', choices=CURSO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form'}))
    f_matriculados = forms.FileField(label='Fichero con los alumnos matriculados')
    f_abandono = forms.FileField(label='Fichero con las asignaturas matriculadas')
    f_rp30 = forms.FileField(label='Fichero con los datos obtenidos del RP30 (Opcional)', required=False)
    
    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['grado'].widget.attrs['class'] = 'my-form'

class ShowDataForm(forms.Form):
    grado = forms.ChoiceField(label='Grado', choices=GRADO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form'}))
    curso = forms.ChoiceField(label='Curso', choices=CURSO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form'}))
    rp_30 = forms.BooleanField(label='RP30', required=False)
