==================
FutuQuant 文档指南
==================

FutuQuant使用Sphinx进行文档编写。

Requirements
------------

- pandoc: `pandoc安装 <http://pandoc.org/installing.html>`_
- Sphinx
- sphinx_rtd_theme

.. code:: bash
	pip install Sphinx sphinx_rtd_theme
	
Usage
-----

- make html: 编译文档并在{project}/docs/build下生成html

- make htmlview: 本地查看文档

- make clean: 清空build目录下文件

- make watch: 使用该命令可以根据源文件的变化自动编译文档


