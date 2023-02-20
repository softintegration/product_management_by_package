# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

IGNORED_DESTINATION_PACKAGE_TYPES = ('mrp_operation','outgoing')


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    managed_by_package = fields.Boolean(string='Managed by package', compute='_compute_managed_by_package')
    package_id_required = fields.Boolean(compute='_compute_package_id_required', store=False)
    result_package_id_required = fields.Boolean(compute='_compute_result_package_id_required', store=False)

    @api.depends('product_id')
    def _compute_managed_by_package(self):
        for each in self:
            each.managed_by_package = each.product_id.managed_by_package

    @api.depends('managed_by_package', 'picking_id.picking_type_code')
    def _compute_package_id_required(self):
        for each in self:
            each.package_id_required = each.managed_by_package and each.picking_id.picking_type_code in (
            'internal', 'outgoing')

    @api.depends('managed_by_package')
    def _compute_result_package_id_required(self):
        for each in self:
            each.result_package_id_required = each.managed_by_package and each.picking_type_id.code not in IGNORED_DESTINATION_PACKAGE_TYPES

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        self._check_packages()
        return res

    def _check_packages(self):
        for each in self.filtered(lambda ml: not self._deleted_line(ml)):
            if each and each.package_id_required and not each.package_id:
                raise ValidationError(_("Source package is required for product %s!") % each.product_id.display_name)
            if each and each.result_package_id_required and not each.result_package_id:
                raise ValidationError(
                    _("Destination package is required for product %s!") % each.product_id.display_name)

    @api.model
    def _deleted_line(self, move_line):
        """ Detect he removed move line records during this transaction or concurrent one"""
        return not self.env.cache.contains(move_line, self) and not move_line.exists()
