1.在urls.py中,例如:path('<str:name><path:path>', ProjectSourceView.as_view(), name='source'),其中str与path都叫作Path converters.

**默认有一下五种Path converters:** https://docs.djangoproject.com/en/2.0/topics/http/urls/#path-converters

*   str - Matches any non-empty string, excluding the path separator, '/'. This is the default if a converter isn’t included in the expression.
*   slug - Matches any slug string consisting of ASCII letters or numbers, plus the hyphen and underscore characters. For example, building-your-1st-django-site.
*   path - Matches any non-empty string, including the path separator, '/'. This allows you to match against a complete URL path rather than just a segment of a URL path as with str.
*   int - Matches zero or any positive integer. Returns an int.
*   uuid - Matches a formatted UUID. To prevent multiple URLs from mapping to the same page, dashes must be included and letters must be lowercase. For example, *  075194d3-6885-417e-a8a8-6c931e272f00. Returns a UUID instance.

如果上述的Path converters还不能满足需求,还可以定制的Path converters:https://docs.djangoproject.com/en/2.0/topics/http/urls/#registering-custom-path-converters

