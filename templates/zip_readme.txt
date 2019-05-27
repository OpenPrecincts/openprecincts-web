This file was obtained via OpenPrecincts.org and is licensed in the public domain.

{% for file in files %}{{ file.filename }}
    - {{ file.cycle }}
    - {{ file.created_by.first_name }} {{ file.created_by.last_name }}
{% if file.notes %} - {{ file.notes }} {% endif %}
{% if file.source_url %} - {{ file.url }} {% endif %}
{% endfor %}
