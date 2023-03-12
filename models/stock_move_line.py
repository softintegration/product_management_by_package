# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare

IGNORED_DESTINATION_PACKAGE_TYPES = ('mrp_operation', 'outgoing')


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
            each.result_package_id_required = each.managed_by_package and each.picking_type_id.code \
                                              and each.picking_type_id.code not in IGNORED_DESTINATION_PACKAGE_TYPES

    def _action_done(self):
        # this must be done before the super call to avoid falling in the issue «Record does not exist or has been deleted»
        # because the super _action_done can remove move lines in self
        self._check_packages()
        return super(StockMoveLine, self)._action_done()

    def _check_packages(self):
        for each in self:
            if each and each.package_id_required and not each.package_id:
                raise ValidationError(_("Source package is required for product %s!") % each.product_id.display_name)
            if each and not each._move_line_will_be_removed() and each.result_package_id_required and not each.result_package_id:
                raise ValidationError(
                    _("Destination package is required for product %s!") % each.product_id.display_name)

    def _move_line_will_be_removed(self):
        self.ensure_one()
        # we have used the same logic used by the stock.move.line._action_done to select move lines to be removed
        return float_compare(self.qty_done, 0, precision_rounding=self.product_uom_id.rounding) == 0 and not self.is_inventory


