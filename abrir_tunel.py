import subprocess
import re
import sys
import os

print("\n" + "="*60)
print("💖 SORPRESAS KAWAII - INICIANDO TÚNEL PÚBLICO SEGURO")
print("="*60 + "\n")
print("Iniciando conexión segura directa a 127.0.0.1:8000...")

# Usar 127.0.0.1 en lugar de localhost para evitar conflictos de IPv6 en Windows (ERR_EMPTY_RESPONSE)
cmd = [
    "ssh",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ServerAliveInterval=30",
    "-R", "80:127.0.0.1:8000",
    "nokey@localhost.run"
]

try:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    url_mostrada = False

    for line in iter(process.stdout.readline, ''):
        match = re.search(r'https://[a-zA-Z0-9\.\-]+\.lhr\.life', line)
        if match:
            url = match.group(0)
            print("\n" + "="*60)
            print("🎉 ¡TÚNEL CONECTADO Y FUNCIONANDO!")
            print("="*60)
            print(f"\n👉 Tu enlace público para celular e Internet es:\n")
            print(f"   \033[1;32m{url}\033[0m\n")
            print("="*60)
            print("💡 Abre ese enlace en tu celular o navegador.")
            print("   Tus 14 productos, imágenes y WhatsApp están activos en vivo.")
            print("   (Mantén esta ventana abierta. Presiona Ctrl + C para salir).")
            print("="*60 + "\n")
            url_mostrada = True
        elif not url_mostrada:
            if "tunneled with tls" in line or "authenticated as" in line:
                print("Enlace establecido correctamente con Django...")

    process.stdout.close()
    process.wait()

except KeyboardInterrupt:
    print("\nCerrando túnel...")
    if 'process' in locals():
        process.terminate()
    print("Túnel cerrado.")
except Exception as e:
    print(f"\nError: {e}")
