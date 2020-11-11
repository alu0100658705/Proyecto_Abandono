from django.template.defaulttags import register
import json 

@register.filter
def get_item(json_var): 
    obj = json.loads(json_var)  
    return obj

@register.filter(name='times') 
def times(number):
    return range(number)

@register.filter
def get_sub_dict(diccionario, clave):
    obj = json.loads(diccionario)
    return obj.get(clave)
    
@register.filter
def get_value(diccionario, i):
    return diccionario.get(str(i))

    