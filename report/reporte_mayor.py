# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from odoo.release import version_info
import logging

class ReporteMayor(models.AbstractModel):
    _name = 'report.l10n_sv_extra.reporte_mayor'

    def retornar_saldo_inicial_todos_anios(self, cuenta, fecha_desde):
        saldo_inicial = 0
        if version_info[0] == 13:
            self.env.cr.execute('select g.id, g.code_prefix as codigo, g.name as cuenta, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id = %s and l.date < %s group by g.id, g.code_prefix, g.name, l.debit, l.credit', (cuenta,fecha_desde))
        else:
            self.env.cr.execute('select g.id, g.code_prefix_start as codigo, g.name as cuenta, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id = %s and l.date < %s group by g.id, g.code_prefix_start, g.name, l.debit, l.credit', (cuenta,fecha_desde))

#        self.env.cr.execute('select a.id, a.code as codigo, a.name as cuenta, sum(l.debit) as debe, sum(l.credit) as haber '\
#        'from account_move_line l join account_account a on(l.account_id = a.id)'\
#        'where a.id = %s and l.date < %s group by a.id, a.code, a.name,l.debit,l.credit', (cuenta,fecha_desde))

        for m in self.env.cr.dictfetchall():
            saldo_inicial += m['debe'] - m['haber']
        return saldo_inicial

    def retornar_saldo_inicial_inicio_anio(self, cuenta, fecha_desde):
        saldo_inicial = 0
        fecha = fields.Date.from_string(fecha_desde)
        if version_info[0] == 13:
            self.env.cr.execute('select g.id, g.code_prefix as codigo, g.name as cuenta, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id = %s and l.date < %s and l.date >= %s group by g.id, g.code_prefix, g.name, l.debit, l.credit', (cuenta,fecha_desde,fecha.strftime('%Y-1-1')))
        else:
            self.env.cr.execute('select g.id, g.code_prefix_start as codigo, g.name as cuenta, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id = %s and l.date < %s and l.date >= %s group by g.id, g.code_prefix_start, g.name, l.debit, l.credit', (cuenta,fecha_desde,fecha.strftime('%Y-1-1')))

#        self.env.cr.execute('select a.id, a.code as codigo, a.name as cuenta, sum(l.debit) as debe, sum(l.credit) as haber '\
#        'from account_move_line l join account_account a on(l.account_id = a.id)'\
#        'where a.id = %s and l.date < %s and l.date >= %s group by a.id, a.code, a.name,l.debit,l.credit', (cuenta,fecha_desde,fecha.strftime('%Y-1-1')))
        for m in self.env.cr.dictfetchall():
            saldo_inicial += m['debe'] - m['haber']
        return saldo_inicial

    def lineas(self, datos):
        totales = {}
        lineas_resumidas = {}
        lineas=[]
        totales['debe'] = 0
        totales['haber'] = 0
        totales['saldo_inicial'] = 0
        totales['saldo_final'] = 0

        grupos_str = ','.join([str(x) for x in datos['grupos_id']])
        if datos['agrupado_por_dia']:
            if version_info[0] == 13:
                self.env.cr.execute('select g.id, g.code_prefix as codigo, g.name as cuenta, l.date as fecha, t.include_initial_balance as balance_inicial, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_account_type t on (t.id = a.user_type_id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id in ('+grupos_str+') and l.date >= %s and l.date <= %s group by g.id, g.code_prefix, g.name, l.date, t.include_initial_balance ORDER BY g.code_prefix', (datos['fecha_desde'], datos['fecha_hasta']))
            else:
                self.env.cr.execute('select g.id, g.code_prefix_start as codigo, g.name as cuenta, l.date as fecha, t.include_initial_balance as balance_inicial, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_account_type t on (t.id = a.user_type_id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id in ('+grupos_str+') and l.date >= %s and l.date <= %s group by g.id, g.code_prefix_start, g.name, l.date, t.include_initial_balance ORDER BY g.code_prefix_start', (datos['fecha_desde'], datos['fecha_hasta']))

#            self.env.cr.execute('select a.id, a.code as codigo, a.name as cuenta, l.date as fecha, t.include_initial_balance as balance_inicial, sum(l.debit) as debe, sum(l.credit) as haber ' \
#                'from account_move_line l join account_account a on(l.account_id = a.id)' \
#                'join account_account_type t on (t.id = a.user_type_id)' \
#                'where a.id in ('+accounts_str+') and l.date >= %s and l.date <= %s group by a.id, a.code, a.name, l.date, t.include_initial_balance ORDER BY a.code',
#            (datos['fecha_desde'], datos['fecha_hasta']))

            grupos_iniciales = []
            for r in self.env.cr.dictfetchall():
                grupos_iniciales.append(r['id'])
                totales['debe'] += r['debe']
                totales['haber'] += r['haber']
                linea = {
                    'id': r['id'],
                    'fecha': r['fecha'],
                    'codigo': r['codigo'],
                    'cuenta': r['cuenta'],
                    'saldo_inicial': 0,
                    'debe': r['debe'],
                    'haber': r['haber'],
                    'saldo_final': 0,
                    'balance_inicial': r['balance_inicial']
                }
                lineas.append(linea)

            lineas_adicionales = []
            for grupo in self.env['account.group'].search([('id', 'in', datos['grupos_id']), ('id', 'not in', grupos_iniciales)]):
                dict = {'id': grupo.id, 'fecha': False, 'codigo': grupo.code_prefix_start, 'cuenta': grupo.name, 'saldo_inicial': 0, 'debe': 0, 'haber': 0, 'saldo_final': 0, 'total_debe': 0, 'total_haber': 0, 'balance_inicial': False, 'fechas': []}
                lineas_adicionales.append(dict)

            lineas = lineas + lineas_adicionales
            lineas.sort(key=lambda i: i['codigo'])

            cuentas_agrupadas = {}
            llave = 'codigo'
            for l in lineas:
                if l[llave] not in cuentas_agrupadas:
                    cuentas_agrupadas[l[llave]] = {
                        'codigo': l[llave],
                        'cuenta': l['cuenta'],
                        'saldo_inicial': 0,
                        'saldo_final': 0,
                        'fechas': [],
                        'total_debe': 0,
                        'total_haber': 0
                    }

                    if not l['balance_inicial']:
                        cuentas_agrupadas[l[llave]]['saldo_inicial'] = self.retornar_saldo_inicial_inicio_anio(l['id'], datos['fecha_desde'])
                    else:
                        cuentas_agrupadas[l[llave]]['saldo_inicial'] = saldo = self.retornar_saldo_inicial_todos_anios(l['id'], datos['fecha_desde'])
                cuentas_agrupadas[l[llave]]['fechas'].append(l)

            for cuenta in cuentas_agrupadas.values():
                for fecha in cuenta['fechas']:
                    cuenta['total_debe'] += fecha['debe']
                    cuenta['total_haber'] += fecha['haber']
                cuenta['saldo_final'] += cuenta['saldo_inicial'] + cuenta['total_debe'] - cuenta['total_haber']

            lineas = cuentas_agrupadas.values()
        else:
            if version_info[0] == 13:
                self.env.cr.execute('select g.id, g.code_prefix as codigo, g.name as cuenta, t.include_initial_balance as balance_inicial, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_account_type t on (t.id = a.user_type_id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id in ('+grupos_str+') and l.date >= %s and l.date <= %s group by g.id, g.code_prefix, g.name,t.include_initial_balance ORDER BY g.code_prefix', (datos['fecha_desde'], datos['fecha_hasta']))
            else:
                self.env.cr.execute('select g.id, g.code_prefix_start as codigo, g.name as cuenta, t.include_initial_balance as balance_inicial, sum(l.debit) as debe, sum(l.credit) as haber from account_move_line l join account_account a on(l.account_id = a.id) join account_account_type t on (t.id = a.user_type_id) join account_group g on(a.group_id = g.id) where l.parent_state = \'posted\' and g.id in ('+grupos_str+') and l.date >= %s and l.date <= %s group by g.id, g.code_prefix_start, g.name,t.include_initial_balance ORDER BY g.code_prefix_start', (datos['fecha_desde'], datos['fecha_hasta']))

#            self.env.cr.execute('select a.id, a.code as codigo, a.name as cuenta, t.include_initial_balance as balance_inicial, sum(l.debit) as debe, sum(l.credit) as haber ' \
#            	'from account_move_line l join account_account a on(l.account_id = a.id)' \
#            	'join account_account_type t on (t.id = a.user_type_id)' \
#            	'where a.id in ('+accounts_str+') and l.date >= %s and l.date <= %s group by a.id, a.code, a.name,t.include_initial_balance ORDER BY a.code',
#            (datos['fecha_desde'], datos['fecha_hasta']))

            grupos_iniciales = []
            for r in self.env.cr.dictfetchall():
                grupos_iniciales.append(r['id'])
                totales['debe'] += r['debe']
                totales['haber'] += r['haber']
                linea = {
                    'id': r['id'],
                    'codigo': r['codigo'],
                    'cuenta': r['cuenta'],
                    'saldo_inicial': 0,
                    'debe': r['debe'],
                    'haber': r['haber'],
                    'saldo_final': 0,
                    'balance_inicial': r['balance_inicial']
                }
                lineas.append(linea)

            for l in lineas:
                if not l['balance_inicial']:
                    l['saldo_inicial'] += self.retornar_saldo_inicial_inicio_anio(l['id'], datos['fecha_desde'])
                    l['saldo_final'] += l['saldo_inicial'] + l['debe'] - l['haber']
                    totales['saldo_inicial'] += l['saldo_inicial']
                    totales['saldo_final'] += l['saldo_final']
                else:
                    l['saldo_inicial'] += self.retornar_saldo_inicial_todos_anios(l['id'], datos['fecha_desde'])
                    l['saldo_final'] += l['saldo_inicial'] + l['debe'] - l['haber']
                    totales['saldo_inicial'] += l['saldo_inicial']
                    totales['saldo_final'] += l['saldo_final']

            lineas_adicionales = []
            for grupo in self.env['account.group'].search([('id', 'in', datos['grupos_id']), ('id', 'not in', grupos_iniciales)]):
                dict = {'id': grupo.id, 'codigo': grupo.code_prefix_start, 'cuenta': grupo.name, 'saldo_inicial': 0, 'debe': 0, 'haber': 0, 'saldo_final': 0}
                lineas_adicionales.append(dict)

            lineas = lineas + lineas_adicionales
            lineas.sort(key=lambda i: i['codigo'])
        
        return {'lineas': lineas,'totales': totales }

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'lineas': self.lineas,
            'current_company_id': self.env.company,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
