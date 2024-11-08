ALLOWED_ENDPOINTS = [
    'specs',
    'restx_doc.static',
    'doc',
    "/swagger.json",
    "swagger.json",
    "/api/fsl13/swagger.json",
    "api/fsl13/swagger.json",
    # "/swaggerui",

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