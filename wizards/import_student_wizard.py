from odoo import models, fields, api
import base64
import xlrd

class ImportStudentWizard(models.TransientModel):
    _name = 'import.student.wizard'
    _description = 'Wizard for importing students'

    file = fields.Binary(string='Archivo', required=True)
    filename = fields.Char(string='Nombre del Archivo')

    def import_students(self):
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        for row in range(1, sheet.nrows):
            student_name = sheet.cell(row, 0).value
            registration_date = sheet.cell(row, 1).value
            specialty = sheet.cell(row, 2).value
            course_name = sheet.cell(row, 3).value
            order_status = sheet.cell(row, 4).value


            student = self.env['res.partner'].search([('name', '=', student_name)], limit=1)
            if not student:
                student = self.env['res.partner'].create({'name': student_name})

            course = self.env['curse'].search([('name', '=', course_name)], limit=1)
            if course:
                self.env['curse.student'].create({
                    'res_partner': student.id,
                    'registration_date': registration_date,
                    'specialty': specialty,
                    'curse_id': course.id,
                })

                self.env['sale.order'].create({
                    'partner_id': student.id,
                    'external_order_status': order_status,
                })
