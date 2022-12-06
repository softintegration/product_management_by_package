# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        self._check_packages()
        return res

    def _check_packages(self):
        for each in self:
            if each.package_id_required and not each.package_id:
                raise ValidationError(_("Source package is required for product %s!")%each.product_id.display_name)
            if each.result_package_id_required and not each.result_package_id:
                raise ValidationError(_("Destination package is required for product %s!")%each.product_id.display_name)



