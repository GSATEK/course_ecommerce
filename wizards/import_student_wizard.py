from odoo import models, fields, api
import base64
import xlrd
from datetime import datetime

class ImportStudentWizard(models.TransientModel):
    _name = 'import.student.wizard'
    _description = 'Wizard for importing students'

    file = fields.Binary(string='Archivo', required=True)
    filename = fields.Char(string='Nombre de Archivo')
    from_row = fields.Integer(string='Desde fila', required=True, default=0)
    to_row = fields.Integer(string='Hasta Fila', required=True)

    def import_students(self):
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        for row in range(self.from_row, min(self.to_row + 1, sheet.nrows)):
            student_name = sheet.cell(row, 0).value
            registration_date = sheet.cell(row, 1).value
            specialty = sheet.cell(row, 2).value
            course_name = sheet.cell(row, 3).value
            order_status = sheet.cell(row, 5).value

            registration_date = datetime.strptime(registration_date, '%d.%m.%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S') if registration_date else None

            student = self.env['res.partner'].search([('name', '=', student_name)], limit=1)
            if not student:
                student = self.env['res.partner'].create({'name': student_name})
                self.env.cr.commit()

            course = self.env['curse'].search([('product_id.name', '=', course_name)], limit=1)
            if course:
                existing_enrollment = self.env['curse.student'].search([
                    ('res_partner', '=', student.id),
                    ('curse_ids', 'in', course.id)
                ], limit=1)
                if not existing_enrollment:
                    curse_student = self.env['curse.student'].search([('res_partner', '=', student.id)], limit=1)
                    if curse_student:
                        curse_student.write({
                            'curse_ids': [(4, course.id)],
                            'registration_date': registration_date,
                            'specialty': specialty,
                        })
                    else:
                        self.env['curse.student'].create({
                            'res_partner': student.id,
                            'registration_date': registration_date,
                            'specialty': specialty,
                            'curse_ids': [(4, course.id)],
                        })

                    order_vals = {
                        'partner_id': student.id,
                        'external_order_status': order_status,
                        'order_line': [(0, 0, {
                            'product_id': course.product_id.id,
                            'name': course.product_id.name,
                            'product_uom_qty': 1,
                            'price_unit': course.product_id.list_price,
                        })]
                    }
                    self.env['sale.order'].create([order_vals])

