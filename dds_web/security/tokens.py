####################################################################################################
# IMPORTS ################################################################################ IMPORTS #
####################################################################################################

# Standard library
import datetime
import secrets

# Installed
import flask
from jwcrypto import jwk, jwt

# Own modules
import dds_web.utils
import dds_web.forms


# Functions ############################################################################ FUNCTIONS #
def encrypted_jwt_token(
    username, sensitive_content, expires_in=datetime.timedelta(hours=48), additional_claims=None
):
    """
    Encrypts a signed JWT token. This is to be used for any encrypted token regardless of the sensitive content.

    :param str username: Username must be obtained through authentication
    :param str or None sensitive_content: This is the content that must be protected by encryption.
        Can be set to None for protecting the signed token.
    :param timedelta expires_in: This is the maximum allowed age of the token. (default 2 days)
    :param Dict or None additional_claims: Any additional token claims can be added. e.g., {"iss": "DDS"}
    """
    token = jwt.JWT(
        header={
            "alg": "A256KW",
            "enc": "A256GCM",
            # exp: This registered claim according to JWT specification identifies the time on or after which the JWT MUST NOT be accepted for processing.
            "exp": (dds_web.utils.current_time() + expires_in).timestamp(),
            # iat: issued at value is a registered claim and identifies the time at which the token was issued.
            "iat": (dds_web.utils.current_time()).timestamp(),
            # csg: consignee claim for transmitting the user name to which the token was issued. Is not registered according to JWT specification.
            "csg": username,
        },
        claims=__signed_jwt_token(
            username=username,
            sensitive_content=sensitive_content,
            expires_in=expires_in,
            additional_claims=additional_claims,
        ),
    )
    key = jwk.JWK.from_password(flask.current_app.config.get("SECRET_KEY"))
    token.make_encrypted_token(key)
    return token.serialize()


def update_token_with_mfa(token_claims):
    expires_in = (
        datetime.datetime.fromtimestamp(token_claims.get("exp")) - dds_web.utils.current_time()
    )
    return encrypted_jwt_token(
        username=token_claims.get("sub"),
        sensitive_content=None,
        expires_in=expires_in,
        additional_claims={"mfa_auth_time": dds_web.utils.current_time().timestamp()},
    )


def __signed_jwt_token(
    username,
    sensitive_content=None,
    expires_in=datetime.timedelta(hours=48),
    additional_claims=None,
):
    """
    Generic signed JWT token. This is to be used by both signed-only and signed-encrypted tokens.

    :param str username: Username must be obtained through authentication
    :param str or None sensitive_content: This is the content that must be protected by encryption. (default None)
    :param timedelta expires_in: This is the maximum allowed age of the token. (default 2 days)
    :param Dict or None additional_claims: Any additional token claims can be added. e.g., {"iss": "DDS"}
    """
    expiration_time = dds_web.utils.current_time() + expires_in
    data = {"sub": username, "exp": expiration_time.timestamp(), "nonce": secrets.token_hex(32)}
    if additional_claims is not None:
        data.update(additional_claims)
    if sensitive_content is not None:
        data["sen_con"] = sensitive_content

    key = jwk.JWK.from_password(flask.current_app.config.get("SECRET_KEY"))
    token = jwt.JWT(
        header={
            "alg": "HS256",
            # exp: This registered claim according to JWT specification identifies the time on or after which the JWT MUST NOT be accepted for processing.
            "exp": expiration_time.timestamp(),
            # iat: issued at value is a registered claim and identifies the time at which the token was issued.
            "iat": (dds_web.utils.current_time()).timestamp(),
            # csg: consignee claim for transmitting the user name to which the token was issued. Is not registered according to JWT specification.
            "csg": username,
        },
        claims=data,
        algs=["HS256"],
    )
    token.make_signed_token(key)
    return token.serialize()


def jwt_token(username, expires_in=datetime.timedelta(hours=48), additional_claims=None):
    """
    Generates a signed JWT token. This is to be used for general purpose signed token.
    :param str username: Username must be obtained through authentication
    :param timedelta expires_in: This is the maximum allowed age of the token. (default 2 days)
    :param Dict or None additional_claims: Any additional token claims can be added. e.g., {"iss": "DDS"}
    """
    return __signed_jwt_token(
        username=username, expires_in=expires_in, additional_claims=additional_claims
    )
