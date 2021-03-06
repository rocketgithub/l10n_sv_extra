# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import time
import datetime
import xlsxwriter
import base64
import io
import logging

class AsistenteKardex(models.TransientModel):
    _name = 'l10n_sv_extra.asistente_kardex'
    _description = 'Kardex'

    def _default_producto(self):
        if len(self.env.context.get('active_ids', [])) > 0:
            return self.env.context.get('active_ids')[0]
        else:
            return None

    ubicacion_id = fields.Many2one("stock.location", string="Ubicacion", required=True)
    producto_ids = fields.Many2many("product.product", string="Productos", required=True)
    fecha_desde = fields.Date(string="Fecha Inicial", required=True)
    fecha_hasta = fields.Date(string="Fecha Final", required=True)
    archivo_excel = fields.Binary('Archivo excel')
    name_excel = fields.Char('Nombre archivo', default='kardex.xlsx', size=32)

    def print_report(self):
        data = {
             'ids': [],
             'model': 'l10n_sv_extra.asistente_kardex',
             'form': self.read()[0]
        }
        return self.env.ref('l10n_sv_extra.action_reporte_kardex').with_context(landscape=True).report_action(self, data=data)

    def reporte_excel(self):
        f = io.BytesIO()
        libro = xlsxwriter.Workbook(f)
        hoja = libro.add_worksheet('reporte')

        hoja.write(0, 0, 'KARDEX')

        datos = {}
        datos['fecha_desde'] = self.fecha_desde
        datos['fecha_hasta'] = self.fecha_hasta
        datos['ubicacion_id'] = []
        datos['ubicacion_id'].append(self.ubicacion_id.id)
        
        y = 2
        for producto in self.producto_ids:
            resultado = self.env['report.l10n_sv_extra.reporte_kardex'].lineas(datos, producto.id)
            hoja.write(y, 0, 'Fecha desde:')
            hoja.write(y, 1, 'Fecha hasta:')
            hoja.write(y, 2, 'Ubicación:')
            hoja.write(y, 3, 'Producto:')
            y += 1
            hoja.write(y, 0, fields.Datetime.from_string(self.fecha_desde).strftime('%d/%m/%Y %H:%M:%S'))
            hoja.write(y, 1, fields.Datetime.from_string(self.fecha_hasta).strftime('%d/%m/%Y %H:%M:%S'))
            hoja.write(y, 2, self.ubicacion_id.display_name)
            hoja.write(y, 3, producto.name)
            y += 1
            hoja.write(y, 0, 'Inicial:')
            hoja.write(y, 1, 'Entradas:')
            hoja.write(y, 2, 'Salidas:')
            hoja.write(y, 3, 'Final:')
            y += 1
            hoja.write(y, 0, resultado['totales']['inicio'])
            hoja.write(y, 1, resultado['totales']['entrada'])
            hoja.write(y, 2, resultado['totales']['salida'])
            hoja.write(y, 3, resultado['totales']['inicio']+resultado['totales']['entrada']+resultado['totales']['salida'])
            y += 2
            hoja.write(y, 0, 'Fecha')
            hoja.write(y, 1, 'Documento')
            hoja.write(y, 2, 'Empresa')
            hoja.write(y, 3, 'Tipo')
            hoja.write(y, 4, 'UOM')
            hoja.write(y, 5, 'Entradas')
            hoja.write(y, 6, 'Salidas')
            hoja.write(y, 7, 'Final')
            hoja.write(y, 8, 'Costo')
            hoja.write(y, 9, 'Total')
            y += 1
            for linea in resultado['lineas']:
                hoja.write(y, 0, fields.Datetime.from_string(linea['fecha']).strftime('%d/%m/%Y %H:%M:%S'))
                hoja.write(y, 1, linea['documento'])
                hoja.write(y, 2, linea['empresa'])
                hoja.write(y, 3, linea['tipo'])
                hoja.write(y, 4, linea['unidad_medida'])
                hoja.write(y, 5, linea['entrada'])
                hoja.write(y, 6, linea['salida'])
                hoja.write(y, 7, linea['saldo'])
                hoja.write(y, 8, linea['costo'])
                hoja.write(y, 9, linea['saldo'] * linea['costo'])
                y += 1
            y += 1

        libro.close()
        datos = base64.b64encode(f.getvalue())
        self.write({'archivo_excel':datos, 'name_excel':'kardex.xls'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_sv_extra.asistente_kardex',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
