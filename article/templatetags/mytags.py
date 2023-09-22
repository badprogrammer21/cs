from django import template

register = template.Library()

def bold(text):
    return text.replace('**','<h1 data-splitting>',1).replace('**','</h1>',1)

register.filter('bold', bold)