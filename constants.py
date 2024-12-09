ALLOWED_ENDPOINTS = [
    'specs',
    'restx_doc.static',
    'doc',
    'authentication_email_password_login',
    'authentication_google_login'
]

AUTHORIZATIONS = {
    'JWT Token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

PROD = False