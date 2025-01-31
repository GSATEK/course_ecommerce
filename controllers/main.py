from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import models, fields, http
from odoo.http import request, Response
from datetime import date, timedelta

from werkzeug.exceptions import NotFound


class CustomWebsiteSale(WebsiteSale):

    def inhit_shop_lookup_products(self, attrib_set, options, post, search, website):
        # No limit because attributes are obtained from complete product list
        search_results = website._search_with_fuzzy("products_only", search,
                                                    limit=None,
                                                    order=self._get_search_order(post),
                                                    options=options)
        # Ensure only three values are unpacked
        product_count, details, fuzzy_search_term = search_results[:3]

        # Ensure details is a dictionary
        if isinstance(details, list) and len(details) > 0:
            details = details[0]

        search_result = details.get('results', request.env['product.template']).with_context(bin_size=True)

        return fuzzy_search_term, product_count, search_result

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        fuzzy_search_term, product_count, products = self.inhit_shop_lookup_products(attrib_set, options, post, search,
                                                                                     website)
        today = fields.Date.today()

        # Filter products with parent_id False and within the date range
        filtered_products = products.filtered(
            lambda p: not p.parent_id and
                      (not p.date_start or p.date_start <= today)
        )

        return fuzzy_search_term, product_count, filtered_products

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()

        request.session['website_sale_cart_quantity'] = order.cart_quantity

        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:
                raise NotFound()
            if abandoned_order.state != 'draft':
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if order:
            config = request.env['res.config.settings'].sudo().get_values()
            if config.get('discount_active'):
                discount_percentage = config.get('discount_percentage')
                discount_duration = config.get('discount_duration')
                discount_duration_type = config.get('discount_duration_type')

                student = request.env['curse.student'].search([('res_partner', '=', order.partner_id.id)], limit=1)
                if student:
                    registration_date = student.registration_date
                    if discount_duration_type == 'year':
                        discount_threshold_date = registration_date + timedelta(days=365 * discount_duration)
                    elif discount_duration_type == 'month':
                        discount_threshold_date = registration_date + timedelta(days=30 * discount_duration)
                    elif discount_duration_type == 'week':
                        discount_threshold_date = registration_date + timedelta(weeks=discount_duration)
                    else:
                        discount_threshold_date = registration_date + timedelta(days=discount_duration)

                    if date.today() >= discount_threshold_date:
                        for line in order.order_line:
                            line.discount = discount_percentage
                        order.write({'order_line': [(1, line.id, {'discount': discount_percentage}) for line in
                                                    order.order_line]})

            values.update(order._get_website_sale_extra_values())
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            values['suggested_products'] = order._cart_accessories()
            values.update(self._get_express_shop_payment_values(order))

        if post.get('type') == 'popover':
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.cart", values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()

        config = request.env['res.config.settings'].sudo().get_values()
        discount_active = config.get('discount_active', False)
        update_pricelist = True

        if discount_active:
            discount_percentage = config.get('discount_percentage')
            discount_duration = config.get('discount_duration')
            discount_duration_type = config.get('discount_duration_type')

            student = request.env['curse.student'].search([('res_partner', '=', order.partner_id.id)], limit=1)
            if student:
                registration_date = student.registration_date
                if discount_duration_type == 'year':
                    discount_threshold_date = registration_date + timedelta(days=365 * discount_duration)
                elif discount_duration_type == 'month':
                    discount_threshold_date = registration_date + timedelta(days=30 * discount_duration)
                elif discount_duration_type == 'week':
                    discount_threshold_date = registration_date + timedelta(weeks=discount_duration)
                else:
                    discount_threshold_date = registration_date + timedelta(days=discount_duration)

                if date.today() >= discount_threshold_date:
                    for line in order.order_line:
                        line.discount = discount_percentage
                    order.write(
                        {'order_line': [(1, line.id, {'discount': discount_percentage}) for line in order.order_line]})
                    update_pricelist = False

        request.website.sale_get_order(update_pricelist=update_pricelist)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")