from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if order:
            self.env['crm.lead'].create({
                'name': order.name,
                'partner_id': order.partner_id.id,
                'description': '\n'.join([line.name for line in order.order_line]),
            })
        return order