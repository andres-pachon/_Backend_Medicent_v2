from email.message import EmailMessage
from hashlib import sha256
from urllib.parse import urlencode
import hmac
import smtplib

from flask import current_app, jsonify, request
from itsdangerous import BadData, BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.database.database import bcrypt, db
from app.models.usuario import Usuario


class PasswordResetController:
    TOKEN_SALT = "medicent-password-reset-v1"
    TOKEN_MAX_AGE = 30 * 60

    @staticmethod
    def _serializer():
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=PasswordResetController.TOKEN_SALT)

    @staticmethod
    def _version_contrasena(usuario):
        return sha256(usuario.password.encode("utf-8")).hexdigest()

    @staticmethod
    def solicitar():
        data = request.get_json(silent=True) or {}
        correo = str(data.get("correo", "")).strip().lower()
        smtp_host = current_app.config.get("SMTP_HOST")
        smtp_user = current_app.config.get("SMTP_USERNAME")
        smtp_password = current_app.config.get("SMTP_PASSWORD")
        remitente = current_app.config.get("MAIL_FROM") or smtp_user
        if not all((smtp_host, smtp_user, smtp_password, remitente)):
            return jsonify({"message": "La recuperación por correo aún no está configurada en el servidor."}), 503

        usuario = Usuario.query.filter_by(correo=correo).first() if correo else None
        if usuario is not None:
            token = PasswordResetController._serializer().dumps({
                "id": usuario.idUsuario,
                "version": PasswordResetController._version_contrasena(usuario),
            })
            base_url = str(current_app.config.get("FRONTEND_URL", "http://localhost:5173")).rstrip("/")
            enlace = f"{base_url}/restablecer-contrasena?{urlencode({'token': token})}"
            mensaje = EmailMessage()
            mensaje["Subject"] = "Restablece tu contraseña de Medicent"
            mensaje["From"] = remitente
            mensaje["To"] = usuario.correo
            mensaje.set_content(
                "Recibimos una solicitud para restablecer la contraseña de tu cuenta Medicent. "
                f"Abre este enlace en los próximos 30 minutos: {enlace}\n\n"
                "Si no solicitaste el cambio, puedes ignorar este correo."
            )
            try:
                with smtplib.SMTP(smtp_host, current_app.config.get("SMTP_PORT", 587), timeout=10) as servidor:
                    if current_app.config.get("SMTP_USE_TLS", True):
                        servidor.starttls()
                    servidor.login(smtp_user, smtp_password)
                    servidor.send_message(mensaje)
            except (OSError, smtplib.SMTPException):
                current_app.logger.exception("No se pudo enviar el correo de recuperación")
                # Mantener la misma respuesta evita revelar si el correo existe.
                return jsonify({"message": "Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña."}), 200

        return jsonify({"message": "Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña."}), 200

    @staticmethod
    def restablecer():
        data = request.get_json(silent=True) or {}
        token = str(data.get("token", ""))
        nueva = str(data.get("nuevaContrasena", ""))
        if len(nueva) < 8:
            return jsonify({"message": "La nueva contraseña debe tener al menos 8 caracteres."}), 400

        try:
            payload = PasswordResetController._serializer().loads(
                token, max_age=PasswordResetController.TOKEN_MAX_AGE
            )
            usuario = db.session.get(Usuario, int(payload["id"]))
        except SignatureExpired:
            return jsonify({"message": "El enlace de recuperación venció. Solicita uno nuevo."}), 400
        except (BadSignature, BadData, KeyError, TypeError, ValueError):
            return jsonify({"message": "El enlace de recuperación no es válido. Solicita uno nuevo."}), 400

        if usuario is None:
            return jsonify({"message": "El enlace de recuperación no es válido. Solicita uno nuevo."}), 400
        version = payload.get("version", "")
        if not hmac.compare_digest(version, PasswordResetController._version_contrasena(usuario)):
            return jsonify({"message": "El enlace de recuperación no es válido o ya fue usado."}), 400

        usuario.password = bcrypt.generate_password_hash(nueva).decode("utf-8")
        db.session.commit()
        return jsonify({"message": "La contraseña se actualizó correctamente. Ya puedes iniciar sesión."}), 200
