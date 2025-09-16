from django.core.validators import RegexValidator


phone_regex = RegexValidator(regex=r'^\(\d{2,}\) \d{4,5}\-\d{4}$',
                                message="Phone number must be entered in the format:" + \
                                        "'(99) 99999-9999'. Up to 15 digits allowed.")
