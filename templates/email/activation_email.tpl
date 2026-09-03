{% extends "mail_templated/base.tpl" %}

{% block subject %}
Hello {{ user }} This is Your Reset Password Email

{% endblock %}

{% block html %}
    <a href="http://127.0.0.1:8000/accounts/api/v1/activation/confirm/{{ token }}/">
        Activate your account
    </a>
{% endblock %}