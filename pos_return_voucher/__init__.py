# -*- coding: utf-8 -*-
# © 2016 FactorLibre - Ismael Calvo <ismael.calvo@factorlibre.com>
#        SDI Soluciones Informaticas - Juan Carlos Montoya <jcmontoya@sdi.es>
#        SDI Soluciones Informaticas - Javier Garcia Panach <jgarcia@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def create_journals_company(cr, registry):
    from openerp import SUPERUSER_ID
    import time
    company_obj = registry['res.company']
    account_obj = registry['account.account']
    journal_obj = registry['account.journal']
    pos_config_obj = registry['pos.config']
    sequence_obj = registry['ir.sequence']
    year = time.strftime('%Y')
    company_ids = company_obj.search(cr, SUPERUSER_ID, [])
    for company in company_obj.browse(cr, SUPERUSER_ID, company_ids):

        vals = {
            'name': u'Account Voucher sequence - ' + company.name,
            'padding': 4,
            'number_next_actual': 1,
            'number_increment': 1,
            'implementation': 'no_gap',
            'prefix': 'VALE/' + year,
            'company_id': company.id
        }
        sequence_id = sequence_obj.create(cr, SUPERUSER_ID, vals)

        debit_credit_id = account_obj.search(cr, SUPERUSER_ID,
                                             [('code', 'like', '438000'),
                                              ('company_id', '=', company.id)])
        d_c_id = debit_credit_id and debit_credit_id[0] or False

        if not d_c_id:
            continue

        vals = {
            'name': u'Vale devolución - ' + company.name,
            'code': u'VALES',
            'type': 'cash',
            'sequence_id': sequence_id,
            'default_debit_account_id': d_c_id,
            'default_credit_account_id': d_c_id,
            'user_id': SUPERUSER_ID,
            'journal_user': True,
            'entry_posted': True,
            'update_posted': True,
            'group_invoice_lines': True,
            'voucher_journal': True,
            'company_id': company.id
        }
        journal_id = journal_obj.create(cr, SUPERUSER_ID, vals)
        pos_config_ids = pos_config_obj.search(cr, SUPERUSER_ID,
                                               [('company_id', '=',
                                                 company.id)])
        for conf in pos_config_obj.browse(cr, SUPERUSER_ID, pos_config_ids):
            conf.write({'journal_ids': [(4, journal_id)]})
