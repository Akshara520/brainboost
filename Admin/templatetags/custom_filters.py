from django import template

register = template.Library()


# Purpose: This filter returns the choice (1 to 5) based on the given index.
@register.filter
def get_choice(mcq, index):
    choices = [mcq.choice1, mcq.choice2, mcq.choice3, mcq.choice4, mcq.choice5]
    try:
        return choices[int(index) - 1]
    except (IndexError, ValueError):
        return ''
