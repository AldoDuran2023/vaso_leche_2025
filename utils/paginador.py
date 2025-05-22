from flask import jsonify, url_for

def paginar_query(query, page, per_page, route_name, fields):
    paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)

    data = [
        {field: getattr(item, field) for field in fields} 
        for item in paginated_data.items
    ]

    next_page_url = url_for(route_name, page=page + 1, per_page=per_page, _external=True) if paginated_data.has_next else None
    prev_page_url = url_for(route_name, page=page - 1, per_page=per_page, _external=True) if paginated_data.has_prev else None

    return {
        'data': data,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': query.count(),
            'total_pages': (query.count() + per_page - 1) // per_page,
            'next_page_url': next_page_url,
            'prev_page_url': prev_page_url
        }
    }