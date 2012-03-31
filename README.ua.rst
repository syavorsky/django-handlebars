=================
django-handlebars
=================
Немає задуму благороднішого, аніж викласти сотню-другу кілобайт HTML-у для анонімуса. То ж ніщо не повинно стримувати вебмайстра у його благородному пориві. Звичайно, у доброго газди вже є `Django <https://www.djangoproject.com/>`_, що мегабайтами лиє добро в інтернети на заздрість усім ворогам. Досягаємо на білий світ `Handlebars <http://handlebarsjs.com/>`_ і напильник. До пари би ще здалося ``python-spidermonkey`` і ``pyinotify``, аби ``manage.py compilehandlebars`` збирав усе до купи і радував, а як немає, то й не біда.

Отож, повтиравши руки і притягнувши консоль ближче, рушаймо:

1. Досягаємо. ``pip install django-handlebars`` або ``python setup.py install``

2. Прикручуємо. Додаємо ``django_handlebars`` до ``settings.INSTALLED_APPS``

3. Підточуємо. Об’являємо в ``settings.py`` змінні ``HANDLEBARS_*`` по зразку `django_handlebars.appsettings <https://github.com/yavorskiy/django-handlebars/blob/master/django_handlebars/appsettings.py>`_

4. Перевіряємо. ``./manage.py test django_handlebars``

5. Радуймося і співаймо.


Користаємося благами
====================
День треба починати з доброї кави, а темплейти {% load %} ::

  {% load handlebars_tags %}
  <html>
  <head>
    {% handlebars_scripts %}
  </head>
  <body></body> 
  </html>

На сторінці з’явиться пара тегів ``script``. Перший -- ``handlebars.js``, або ``handlebars.runtime.js``, якщо темплейти вже скомпільовані і ``settings.HANDLEBARS_COMPILED = True``. Інший — ``handlebars.django.js``, котрий додасть метод ``Handlebars.tpl()`` для завантаження і читання темплейтів. 

Компілюємо теплейти в браузері.
-------------------------------
Так простіше і швидше, підійде для початку. Темплейти компілюються щоразу заново і лишній десяток кілобайт парсера додається бонусом до кожної сторінки. Переконавшись, що ``*.html`` темплейт доступний зі статичного URL-а, пишемо::
	
  var data = {title: "The title", body: "whatever"}

  Handlebars.tpl("your/template/spec", {
      success: function(renderer){
          console.log("Rendered template:", renderer(data));
      },
      error: function(xhr, err){
          console.warn("Ooops, can't load template", err);
      }
  });

що завантажить темплейт з ``http://domain.com/ + settings.HANDLEBARS_TPL_URL + path/to/template + .html``. Повторний виклик поверне темплейт з кешу (не того, котрий готівка, заначка в безпеці).

Якщо доступний `jQuery <https://github.com/jquery/jquery>`_, то ``Handlebars.tpl()`` поверне jQuery.Deferred::

  var df = Handlebars.tpl("your/template/spec");

  df.done(function(renderer){
      console.log("Rendered template:", renderer(data));
  }).fail(function(xhr, err){
      console.warn("Ooops, can't load template", err);
  });

Якщо ж немає, то все загрузиться дідівським XHR-ом, скромно і без музики.

Компілюємо на сервері (коли пан має час і натхнення).
----------------------------------------------------
Якщо відмінити пиво і потратити ввечері годинку-другу на читання доків та інсталяцію всіх модулів, то світле майбутнє стане значно ближчим. Код залишається тим же, але темплейти будуть завантажуватись з ``http://domain.com/ + settings.HANDLEBARS_TPL_CMPURL + path/to/template + .js``

Бабу з возу. Шануйте коней.
--------------------------
В обох випадках маємо HTTP-запит, котрого можна позбутись::

  {% handlebars_template "your/template/spec" %}

Тег додасть на сторінку ``<script>Handlebars.tpl("your/template/spec", tpl)</script>``, де tpl -- скомпільований, або сирий темплейт.

Компілюємо
--------------
::
  ./manage.py compilehandlebars --help

  --clean               Remove all previously compiled templates
  --watch               Watch for changes within appsettings.TPL_DIR and compile
  --raw                 Do not format output
  --quiet               Run with no output

License (Не перекладається)
---------------------------
Copyright 2012 Sergii Iavorskyi, Licensed new-style BSD. Contains `Handlebars.js <https://github.com/wycats/handlebars.js>`_ copyright 2011 Yehuda Katz. See LICENSE file for more information.





