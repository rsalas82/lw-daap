#
# Some helper functions to deal with proxies.
#

from datetime import datetime
import subprocess
from tempfile import NamedTemporaryFile

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
import humanize
import pytz

from flask import current_app, request

CFG_PRIV_KEY_PASSWD = b'lwdaap-passwd'
import re
CERT_RE = re.compile("-----BEGIN CERTIFICATE-----\r?\n"
                     ".+?\r?\n"
                     "-----END CERTIFICATE-----\r?\n?", re.DOTALL)


def get_client_proxy_info(profile):
    """
    Returns information on the current proxy (if available)
    """
    info = {'user_proxy': False}
    if ('SSL_CLIENT_M_SERIAL' not in request.environ or
        'SSL_CLIENT_V_END' not in request.environ or
        'SSL_CLIENT_I_DN' not in request.environ or
        request.environ.get('SSL_CLIENT_VERIFY') != 'SUCCESS'):
        return info 
    info['user_dn'] = request.environ['SSL_CLIENT_S_DN']
    info['user_cert'] = request.environ['SSL_CLIENT_CERT']
    if profile.user_proxy:
        px = x509.load_pem_x509_certificate(
            profile.user_proxy.encode('ascii', 'ignore'),
            default_backend()
        )
        time_left = (px.not_valid_after.replace(tzinfo=pytz.utc)
                     - datetime.now(tz=pytz.utc))
        # let's consider a valid proxy if you have at least 10 min
        if time_left.total_seconds > 600:
            info['user_proxy'] = True
            info['user_proxy_time_left'] = humanize.naturaldelta(time_left)
    return info


def generate_proxy_request():
    """
    Generates a proxy request to be signed by the user to create the proxy
    returns back a pair (private_key, CSR)
    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=default_backend()
    )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Dummy"),
    ])).sign(key, hashes.SHA256(), default_backend())

    csr_public = csr.public_bytes(serialization.Encoding.PEM)

    return (private_key, csr_public)


def build_proxy(user_proxy, csr_priv_key):
    """
    Builds a new proxy with the chain sent by the user plus our private key
    Returns the proxy and the time left (humanized)
    """
    pem_chain = CERT_RE.findall(user_proxy)
    x509_chain = [x509.load_pem_x509_certificate(c.encode('ascii', 'ignore'),
                                                 default_backend())
                  for c in pem_chain]
    if len(x509_chain) < 2:
        # should have 2 certs in the chain
        abort(400)

    proxy = x509_chain[0]
    issuer = x509_chain[1]

    issuer_names = [n for n in proxy.issuer]
    subject_names = [n for n in proxy.subject]

    # should be the same but the last CN
    if issuer_names != subject_names[:-1]:
        abort(400)
    if subject_names[-1].oid != NameOID.COMMON_NAME:
        abort(400)

    private_key = serialization.load_pem_private_key(
        csr_priv_key.encode('ascii'), password=None,
        backend=default_backend()
    )

    p_mod = proxy.public_key().public_numbers().n
    priv_mod = private_key.private_numbers().public_numbers.n

    if p_mod != priv_mod:
        # signed with a different key!?
        abort(400)

    # build the new proxy
    new_proxy_chain = [pem_chain[0], csr_priv_key]
    new_proxy_chain.extend(pem_chain[1:])

    time_left = (proxy.not_valid_after.replace(tzinfo=pytz.utc)
                 - datetime.now(tz=pytz.utc))
 
    return ''.join(new_proxy_chain), time_left


def add_voms_info(user_proxy, vo):
    """
    Adds voms information to existing proxy.
    
    Uses the voms-proxy-init command (no voms API for Python)
    """
    with NamedTemporaryFile() as old_proxy:
        with NamedTemporaryFile(mode='rw') as new_proxy:
            old_proxy.write(user_proxy)
            old_proxy.flush()

            current_app.logger.debug("PROXY\n%s" % user_proxy)
            cmd = ['voms-proxy-init',
                   '--out', new_proxy.name,
                   '--voms', vo,
                   '-rfc', '--debug',
                   '--noregen', '--ignorewarn']
            proc = subprocess.Popen(cmd, shell=False,
                                    env={'X509_USER_PROXY': old_proxy.name},
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            current_app.logger.debug("CMD %s" % ' '.join(cmd))
            out = ''.join([l for l in proc.stdout])
            proc.wait()
            if proc.returncode != 0: #  and not _check_proxy_validity(new_proxy):
                current_app.logger.debug("Failed to generate a proxy (%d): %s" % (proc.returncode, out))
            return new_proxy.read()
    return user_proxy
