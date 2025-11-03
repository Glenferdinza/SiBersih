from django import template

register = template.Library()

@register.filter(name='filter_status')
def filter_status(queryset, status):
    """Filter voucher requests by status"""
    if not queryset:
        return queryset
    return [item for item in queryset if item.status == status]
