import jwt
import db.dbConnections as db

private_key = open('helpers/keys/es256_private.pem').read()
public_key = open('helpers/keys/es256_public.pem').read()


def create_token(payload):
    """
    Create a new token with the given payload

    Args:
    payload: dict

    Returns:
    str: token
    """
    return jwt.encode(payload, private_key, algorithm='ES256')


def decode_token(token):
    """
    Decode the given token

    Args:
    token: str

    Returns:
    dict: payload
    """
    return jwt.decode(token, public_key, algorithms=['ES256'])


def verify_token(token, user_id):
    """
    Verify the given token

    Args:
    token: str

    Returns:
    bool: True if the token is verified, False otherwise
    """
    try:  # try to decode the token
        decode_token(token)
        if not db_verify_token(token, user_id):  # check if the token is valid in the database
            return False
        return True
    except jwt.exceptions.PyJWTError:  # token is invalid
        return False


def db_verify_token(token, user_id):
    """
    Verifies a token

    Args:
    token: str
    user_id: int

    Returns:
    bool: True if the token is verified, False otherwise
    """
    # get a connection to the database
    connection = db.get_connection()
    try:  # try to verify the token
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to verify the token
                sql = "select * from tokens where token = %s and user_id = %s and valid_until > NOW()"
                cursor.execute(sql, (token, user_id))  # execute the query
                result = cursor.fetchone()  # get the result
                if result:  # if the token exists
                    if result["revoked_at"]:  # check if the token is revoked
                        return False
                    else:
                        return True
                else:
                    return False

    except Exception as e:  # handle exceptions
        return str(e)  # return the exception as a string
