ALLOWED_ENDPOINTS = [
    'specs',
    'restx_doc.static',
    'doc',
    'tokens_register',
    'tokens_login'
]

AUTHORIZATIONS = {
    'JWT Token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

PROD = False