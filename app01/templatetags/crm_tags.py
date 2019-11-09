from django import template
register = template.Library()
@register.simple_tag
def render_enroll_contral(enroll_obj):
    return enroll_obj.enrolled_class.contract.template.\
        format(branch=enroll_obj.enrolled_class.branch,name=enroll_obj.customer.name)
