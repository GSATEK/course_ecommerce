from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    external_order_status = fields.Selection([
        ('cambio', 'Cambio de curso'),
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso)'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('error', 'Error'),
        ('reembolsado', 'Reembolsado')
    ], string='Estado de la Orden Externa')

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

    def _add_students_to_courses(self):
        if self.invoice_status == 'invoiced':
            for line in self.order_line:
                if line.product_id:
                    curse = self.env['curse'].sudo().search([('product_id', '=', line.product_id.name)])
                    if curse:
                        existing_student = self.env['curse.student'].sudo().search([
                            ('res_partner', '=', self.partner_id.id),
                            ('curse_id', '=', curse.id)
                        ])
                        if not existing_student:
                            self.env['curse.student'].create({
                                'res_partner': self.partner_id.id,
                                'registration_date': fields.Date.today(),
                                'curse_id': curse.id,
                            })
