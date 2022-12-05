# -*- coding: utf-8 -*- 


{
    'name': 'Manage product by packages',
    'author': 'Soft-integration',
    'application': False,
    'installable': True,
    'auto_install': False,
    'qweb': [],
    'description': False,
    'images': [],
    'version': '1.0.1',
    'category': 'Product',
    'demo': [],
    'depends': ['stock'],
    'data': [
        'views/product_views.xml',
        'views/stock_move_views.xml'
    ],
    'license': 'LGPL-3',
}
