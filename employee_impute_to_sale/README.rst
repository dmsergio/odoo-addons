..  image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

Impute Employee Costs To Sale Orders
====================================

Módulo que permite crear líneas a un pedido de venta para poder imputar las horas realizadas por un empleado o una máquina,

Además, en la ficha del producto, se han creado unos campos para especificar el precio de venta para clientes normales y clientes VIP. Dichos campos se podrán visualizar en  una pestaña nueva llamada **Precios de Venta**, siempre y cuando su categoría interna sea alguna de las siguientes:

* **LABORES**: se mostrará dos campos nuevos, llamados **Precio de venta** y **Precio VIP**.
* **OPERARIOS**: a parte de los dos campos anteriores, se mostrarán **Precio Nocturno**, **Precio Festivo**, **Precio Nocturno/Festivo**, **Precio Nocturno VIP**, **Precio Festivo VIP** y **Precio Nocturno/Festivo**.

Usage
=====

En la ficha del empleado, se podrá seleccionar su producto relacionado (únicamente se mostrarán aquellos productos que su categoria interna corresponsa a OPERARIOS), y además a su derecha se mostrará un butón llamado **Imputar gastos**. En el wizard mostrado tras pulsar en el botón, se podrá introducir la información necesaria para crear la línea en el pedido de venta seleccionado-

Bug Tracker
===========

Credits
=======

Contributors
------------

* Sergio Díaz <sdimar@yahoo.com>
* Jesús Ndong <>

Maintainer
----------
