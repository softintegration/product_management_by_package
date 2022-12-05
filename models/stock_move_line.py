# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    managed_by_package = fields.Boolean(string='Managed by package', compute='_compute_managed_by_package')
    package_id_required = fields.Boolean(compute='_compute_package_id_required',store=True)
    result_package_id_required = fields.Boolean(compute='_compute_result_package_id_required',store=True)

    @api.depends('product_id')
    def _compute_managed_by_package(self):
        for each in self:
            each.managed_by_package = each.product_id.managed_by_package

    @api.depends('managed_by_package', 'picking_id.picking_type_code')
    def _compute_package_id_required(self):
        for each in self:
            each.package_id_required = each.managed_by_package and each.picking_id.picking_type_code in ('internal', 'outgoing')

    @api.depends('managed_by_package')
    def _compute_result_package_id_required(self):
        for each in self:
            each.result_package_id_required = each.managed_by_package

