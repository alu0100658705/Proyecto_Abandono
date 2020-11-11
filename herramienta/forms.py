from django import forms

GRADO_CHOICES = (
    ("Ingeniería Informática", "Grado en Ingeniería Informática"),
)

CURSO_CHOICES = (
    ("2017/2018", "2017/2018"),
)

VARIABLES_CHOICES = (
    ("Sexo", "Sexo"),
    ("Edad", "Edad"),
    ("Procedencia", "Procedencia"),
    ("Trabajo", "Trabajo"),
    ("Beca", "Becado"),
    ("Convocatoria", "Convocatoria de Preinscripción"),
    ("Preferencia", "Preferencia"),
    ("Modalidad", "Modalidad"),
    ("Especialidad", "Especialidad"),
    ("Nota_Bach_Ciclo", "Nota de Bachiller/Ciclo"),
    ("Nota_Prueba", "Nota Ebau: Prueba"),
    ("Nota_Especifica", "Nota Ebau: Específica"),
    ("Nota_Admision", "Nota de admisión"),
    ("Abandono", "Abandono"),
    ("Aciertos","RP30: Aciertos"),
    ("Fallos","RP: Fallos"),
    ("Total_prueba","RP30: Total"),
    ("asignaturas_matriculadas_primer_año", "Asignaturas matriculados en el primer año"),
    ("asignaturas_presentadas_primer_año", "Asignaturas presentados en el primer año"),
    ("asignaturas_aprobadas_primer_año", "Asignaturas aprobados el primer año"),
    ("asignaturas_matriculadas_segundo_año", "Asignaturas matriculados segundo año"),
    ("asignaturas_presentadas_segundo_año", "Asignaturas presentados el segundo año"),
    ("asignaturas_aprobadas_segundo_año", "Asignaturas aprobados el segundo año"),
    ("media_primer_año", "Media primer año"),
    ("media_segundo_año", "Media segundo año"),
)


class UnidimensionalForm(forms.Form):
    tabla_frec = forms.BooleanField(required=False)
    # Gráfico:
    d_barras = forms.BooleanField(required=False)
    d_sectores = forms.BooleanField(required=False)
    poligono = forms.BooleanField(required=False)
    histograma = forms.BooleanField(required=False)
    d_tallo = forms.BooleanField(required=False)
    d_caja = forms.BooleanField(required=False)
    # Estadíatico:
    e_media = forms.BooleanField(required=False)
    e_mediana = forms.BooleanField(required=False)
    e_moda = forms.BooleanField(required=False)
    e_varianza = forms.BooleanField(required=False)
    e_cuasivar = forms.BooleanField(required=False)
    e_desviacion = forms.BooleanField(required=False)
    e_cuasidesviacion = forms.BooleanField(required=False)
    e_cuartiles = forms.BooleanField(required=False)
    e_percentiles = forms.BooleanField(required=False)
    e_asimetria = forms.BooleanField(required=False)
    e_kurtosis = forms.BooleanField(required=False)
    # Variables:
    variables = forms.ChoiceField(choices=VARIABLES_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'width:340px', 'style': 'color:black'}))
    # Base de Datos
    grado = forms.ChoiceField(label='Grado', choices=GRADO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'color:black', 'style': 'width:340px' }))
    curso = forms.ChoiceField(label='Curso', choices=CURSO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'width:130px'}))

class BidimensionalForm(forms.Form):
    # Grado y Curso
    grado = forms.ChoiceField(label='Grado', choices=GRADO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'color:black', 'style': 'width:340px' }))
    curso = forms.ChoiceField(label='Curso', choices=CURSO_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'width:130px'}))
    # Variables
    variables_1 = forms.ChoiceField(choices=VARIABLES_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'width:340px', 'style': 'color:black'}))
    variables_2 = forms.ChoiceField(choices=VARIABLES_CHOICES, widget=forms.Select(
        attrs={'class': 'my-form', 'style': 'width:340px', 'style': 'color:black'}))
    # Análisis de Datos Categóricos
    tabla_cont = forms.BooleanField(required=False)
    independencia = forms.BooleanField(required=False)
    c_phi = forms.BooleanField(required=False)
    c_contingencia = forms.BooleanField(required=False)
    c_cramer = forms.BooleanField(required=False)
    tau_kendall = forms.BooleanField(required=False)
    # Gráficos Bidimensional
    adosados = forms.BooleanField(required=False)
    apilados = forms.BooleanField(required=False)
    mosaicos = forms.BooleanField(required=False)
    caja_patilla = forms.BooleanField(required=False)
    d_lineal = forms.BooleanField(required=False)
    d_sigmoide = forms.BooleanField(required=False)
    # Modelo de Predicción Lineal
    c_correlacion = forms.BooleanField(required=False)
    c_determinacion = forms.BooleanField(required=False)
    anova = forms.BooleanField(required=False)
    contrastes = forms.BooleanField(required=False)
    kolmogorov = forms.BooleanField(required=False)
    residuos = forms.BooleanField(required=False)
    durbin = forms.BooleanField(required=False)     
    estimacion = forms.BooleanField(required=False)
    prediccion = forms.CharField(required=False, max_length=6, widget=forms.TextInput(attrs={'size':10}))
    # Modelo de Predicción Logística
    contrastes_logistico = forms.BooleanField(required=False)
    test_verosimilitud = forms.BooleanField(required=False)
    c_mcfadden = forms.BooleanField(required=False)
    estimacion_log = forms.BooleanField(required=False)
    prediccion_log = forms.CharField(required=False, max_length=6, widget=forms.TextInput(attrs={'size':10}))
    signifi = forms.BooleanField(required=False)
    durbin_log = forms.BooleanField(required=False)