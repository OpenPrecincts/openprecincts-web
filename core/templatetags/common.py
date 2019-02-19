from django import template

register = template.Library()


@register.inclusion_tag('base_form.html')
def render_form(form):
    return {'form': form}


@register.inclusion_tag('_task_status.html')
def state_status_item(task_status, label):
    return {'task_status': task_status, 'label': label}
