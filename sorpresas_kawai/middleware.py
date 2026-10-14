import logging
from django.contrib.auth import logout

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Obtiene la IP real del cliente considerando posibles proxies o túneles.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


class SessionSecurityMiddleware:
    """
    Middleware de seguridad contra suplantación y secuestro de sesión (Session Hijacking).
    Vincula la sesión activa al User-Agent y a la dirección IP del cliente.
    Si se detecta un cambio en las cabeceras del cliente, la sesión se invalida de inmediato.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_agent = request.META.get('HTTP_USER_AGENT', 'Desconocido')
            client_ip = get_client_ip(request)

            session_ua = request.session.get('_sec_user_agent')
            session_ip = request.session.get('_sec_client_ip')

            # Si es el primer acceso autenticado de la sesión, guardamos las credenciales de entorno
            if session_ua is None or session_ip is None:
                request.session['_sec_user_agent'] = user_agent
                request.session['_sec_client_ip'] = client_ip
            else:
                # Validar coincidencia de User-Agent (mismo navegador / SO)
                ua_mismatch = session_ua != user_agent
                
                # Validar IP (permitimos cambios dentro de la misma subred /24 para redes dinámicas razonables si se desea,
                # o validación estricta de IP completa)
                ip_mismatch = False
                if session_ip and client_ip:
                    # Si ambas son IPv4, comparamos prefijo de subred o IP completa
                    if '.' in session_ip and '.' in client_ip:
                        subnet_saved = '.'.join(session_ip.split('.')[:3])
                        subnet_current = '.'.join(client_ip.split('.')[:3])
                        if subnet_saved != subnet_current:
                            ip_mismatch = True
                    elif session_ip != client_ip:
                        ip_mismatch = True

                if ua_mismatch or ip_mismatch:
                    logger.warning(
                        f"Alerta de seguridad: Posible suplantación de cookie detectada para el usuario "
                        f"'{request.user.username}'. "
                        f"UA original: {session_ua} | UA actual: {user_agent} | "
                        f"IP original: {session_ip} | IP actual: {client_ip}"
                    )
                    logout(request)
                    request.session.flush()

        response = self.get_response(request)
        return response
