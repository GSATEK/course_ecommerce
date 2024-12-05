from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import models, fields, http
from odoo.http import request, Response

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
                      (not p.date_start or p.date_start <= today) and
                      (not p.date_end or p.date_end >= today)
        )

        return fuzzy_search_term, product_count, filtered_products