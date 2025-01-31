from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_duration = fields.Integer(string='Duración del Descuento')
    discount_duration_type = fields.Selection([
        ('day', 'Día'),
        ('week', 'Semana'),
        ('month', 'Mes'),
        ('year', 'Año')
    ], string='Tipo de Duración del Descuento', default='year')
    discount_percentage = fields.Float(string='Porcentaje de Descuento')
    discount_active = fields.Boolean(string='Descuento Activo')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            discount_duration=IrDefault.get('res.config.settings', 'discount_duration'),
            discount_duration_type=IrDefault.get('res.config.settings', 'discount_duration_type'),
            discount_percentage=IrDefault.get('res.config.settings', 'discount_percentage'),
            discount_active=IrDefault.get('res.config.settings', 'discount_active'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'discount_duration', self.discount_duration)
        IrDefault.set('res.config.settings', 'discount_duration_type', self.discount_duration_type)
        IrDefault.set('res.config.settings', 'discount_percentage', self.discount_percentage)
        IrDefault.set('res.config.settings', 'discount_active', self.discount_active)
