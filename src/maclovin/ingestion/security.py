"""Security utilities for safe HTTP requests, SSRF protection, and input sanitization."""

import socket
import ipaddress
import urllib.parse
from typing import Tuple, Optional
import httpx

MAX_FEED_BYTES = 5 * 1024 * 1024  # 5 MB max response size


def is_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica se a URL é segura contra SSRF:
    - Esquema estrito (apenas http e https)
    - Bloqueio de localhost, 127.0.0.1, 0.0.0.0 e nomes locais
    - Resolução DNS e bloqueio de IPs privados, loopback, link-local e metadados de nuvem (169.254.169.254)
    """
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "URL malformada"

    if parsed.scheme not in ("http", "https"):
        return False, f"Esquema proibido: '{parsed.scheme}'. Apenas http/https são permitidos."

    hostname = parsed.hostname
    if not hostname:
        return False, "Hostname ausente na URL"

    hostname_lower = hostname.lower()
    if hostname_lower in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False, f"Acesso a loopback bloqueado: {hostname}"

    if hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
        return False, f"Domínio interno bloqueado: {hostname}"

    # Resolução DNS para checagem de IP real
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        # Se não resolver DNS, o httpx falhará de qualquer forma
        return True, None
    except Exception as e:
        return False, f"Falha na resolução DNS: {e}"

    for addr in addr_infos:
        ip_str = addr[4][0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
                or ip_str.startswith("169.254.")  # Cloud metadata endpoint
            ):
                return False, f"Acesso a IP privado/reservado bloqueado: {ip_str} ({hostname})"
        except ValueError:
            return False, f"IP inválido resolvido: {ip_str}"

    return True, None


def safe_fetch_url(url: str, timeout: float = 15.0, max_redirects: int = 3) -> Tuple[Optional[str], Optional[str]]:
    """
    Realiza requisição HTTP segura:
    1. Valida SSRF no destino inicial
    2. Segue redirecionamentos manualmente validando SSRF em CADA salto
    3. Limita o download ao tamanho máximo de 5MB (proteção contra DoS / Zip-bomb)
    """
    current_url = url
    headers = {"User-Agent": "Maclovin-News-Agent/1.0 (Safe Feed Reader; +https://github.com/Cigano-agi/teddy-bear-agent)"}

    for _ in range(max_redirects + 1):
        is_safe, reason = is_safe_url(current_url)
        if not is_safe:
            return None, f"Bloqueio de Segurança (SSRF): {reason}"

        try:
            with httpx.Client(timeout=timeout, follow_redirects=False) as client:
                with client.stream("GET", current_url, headers=headers) as response:
                    # Tratar redirecionamento
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("Location")
                        if not location:
                            return None, "Redirecionamento sem header Location"
                        current_url = urllib.parse.urljoin(current_url, location)
                        continue

                    response.raise_for_status()

                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > MAX_FEED_BYTES:
                        return None, f"Feed excede tamanho máximo permitido ({content_length} bytes > {MAX_FEED_BYTES} bytes)"

                    chunks = []
                    total_bytes = 0
                    for chunk in response.iter_bytes():
                        total_bytes += len(chunk)
                        if total_bytes > MAX_FEED_BYTES:
                            return None, f"Download interrompido: feed excedeu {MAX_FEED_BYTES} bytes (Proteção contra DoS)"
                        chunks.append(chunk)

                    raw_bytes = b"".join(chunks)
                    encoding = response.encoding or "utf-8"
                    try:
                        return raw_bytes.decode(encoding, errors="replace"), None
                    except Exception:
                        return raw_bytes.decode("utf-8", errors="replace"), None

        except httpx.HTTPStatusError as e:
            return None, f"Erro HTTP {e.response.status_code} ao consultar '{current_url}'"
        except httpx.RequestError as e:
            return None, f"Falha de rede/timeout ao consultar '{current_url}': {e}"
        except Exception as e:
            return None, f"Erro inesperado ao consultar '{current_url}': {e}"

    return None, f"Limite de redirecionamentos excedido ({max_redirects})"


def sanitize_markdown_text(text: Optional[str]) -> str:
    """Sanitiza texto bruto para inserção segura em relatórios Markdown/HTML."""
    if not text:
        return ""
    # Evitar injeção de HTML puro perigoso
    safe = text.replace("<", "&lt;").replace(">", "&gt;")
    return safe.strip()


def sanitize_url(url: Optional[str]) -> str:
    """Garante que apenas URLs com esquemas seguros (http/https) sejam renderizadas como links."""
    if not url:
        return "#"
    clean = url.strip()
    if not (clean.startswith("http://") or clean.startswith("https://")):
        return "#"
    return clean
