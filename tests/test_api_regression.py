import unittest
from datetime import date, time
import re
from unittest.mock import patch

from app import create_app
from app.database.database import bcrypt, db
from app.models.administrador import Administrador
from app.models.biomarcador import Biomarcador
from app.models.medicamento import Medicamento
from app.models.paciente import Paciente, TipoSangreEnum
from app.models.stock_disponible import StockDisponible
from app.models.tipo_documento import TipoDocumento
from app.models.tipo_medicamento import TipoMedicamento
from app.models.tratamiento import Tratamiento
from app.models.usuario import Usuario
from app.models.via_administracion import ViaAdministracion


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "medicent-test-jwt-secret-key-32-bytes-min"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SMTP_HOST = "smtp.test.local"
    SMTP_PORT = 587
    SMTP_USERNAME = "medicent@test.local"
    SMTP_PASSWORD = "test-only-password"
    SMTP_USE_TLS = True
    MAIL_FROM = "medicent@test.local"
    FRONTEND_URL = "http://localhost:5173"


class MedicentApiRegressionTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

        db.session.add(TipoDocumento(idTipoDocumento=1, nombre="Cédula"))
        db.session.add(TipoMedicamento(idTipoMedicamento=1, nombre="Tableta"))
        db.session.add(ViaAdministracion(idViaAdministracion=1, nombre="Oral"))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def crear_usuario(self, correo, documento, *, admin=False, paciente=False):
        usuario = Usuario(
            nombre="Prueba",
            apellido="Medicent",
            documento=documento,
            correo=correo,
            fechaNacimiento=date(1990, 1, 1),
            password=bcrypt.generate_password_hash("Clave123").decode("utf-8"),
            idTipoDocumento=1,
        )
        db.session.add(usuario)
        db.session.flush()

        if admin:
            db.session.add(Administrador(
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                correo=usuario.correo,
                idUsuario=usuario.idUsuario,
            ))
        if paciente:
            db.session.add(Paciente(
                estatura=1.7,
                peso=70,
                tipoSangre=TipoSangreEnum.O_POSITIVO,
                idUsuario=usuario.idUsuario,
            ))
        db.session.commit()
        return usuario

    def token_para(self, correo):
        response = self.client.post("/api/login", json={"correo": correo, "password": "Clave123"})
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()["accessToken"], response.get_json()["user"]

    def test_login_devuelve_rol_y_perfil_para_redireccionar(self):
        admin = self.crear_usuario("admin@test.local", "A-1", admin=True)
        paciente = self.crear_usuario("paciente@test.local", "P-1", paciente=True)

        _, admin_user = self.token_para(admin.correo)
        _, patient_user = self.token_para(paciente.correo)

        self.assertEqual(admin_user["rol"], "admin")
        self.assertEqual(admin_user["perfil"], None)
        self.assertEqual(patient_user["rol"], "usuario")
        self.assertEqual(patient_user["perfil"], "paciente")
        self.assertEqual(patient_user["idUsuario"], paciente.idUsuario)

    def test_rutas_admin_requieren_autenticacion_y_rol_admin(self):
        paciente = self.crear_usuario("paciente@test.local", "P-1", paciente=True)
        sin_token = self.client.get("/api/admin/usuarios")
        token, _ = self.token_para(paciente.correo)
        como_paciente = self.client.get(
            "/api/admin/usuarios",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(sin_token.status_code, 401)
        self.assertEqual(como_paciente.status_code, 403)

    def test_paneles_admin_exponen_solo_resumenes_agregados(self):
        admin = self.crear_usuario("admin@test.local", "A-1", admin=True)
        paciente = self.crear_usuario("paciente@test.local", "P-1", paciente=True)
        db.session.add(Biomarcador(
            tipo="Presión arterial",
            nombre="Sistólica",
            valor=120,
            unidad="mmHg",
            fecha=date(2026, 2, 1),
            hora=time(9, 0),
            idPaciente=paciente.paciente.idPaciente,
        ))
        db.session.commit()

        token_admin, _ = self.token_para(admin.correo)
        token_paciente, _ = self.token_para(paciente.correo)
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        headers_paciente = {"Authorization": f"Bearer {token_paciente}"}

        medicamentos = self.client.get("/api/admin/medicamentos/resumen", headers=headers_admin)
        biomarcadores = self.client.get("/api/admin/biomarcadores/resumen", headers=headers_admin)

        self.assertEqual(medicamentos.status_code, 200)
        self.assertEqual(biomarcadores.status_code, 200)
        self.assertEqual(biomarcadores.get_json()["porTipo"], [{"tipo": "Presión arterial", "cantidad": 1}])
        self.assertNotIn("valor", str(biomarcadores.get_json()))
        self.assertEqual(self.client.get("/api/admin/biomarcadores/resumen", headers=headers_paciente).status_code, 403)

    def test_recuperacion_cambia_contrasena_y_el_enlace_se_usa_una_sola_vez(self):
        usuario = self.crear_usuario("persona@test.local", "P-1")

        with patch("app.Controllers.password_reset_controller.smtplib.SMTP") as smtp_mock:
            servidor = smtp_mock.return_value.__enter__.return_value
            solicitud = self.client.post(
                "/api/password/solicitar-restablecimiento",
                json={"correo": usuario.correo},
            )
            self.assertEqual(solicitud.status_code, 200)
            mensaje = servidor.send_message.call_args.args[0]
            token = re.search(r"token=([^\s]+)", mensaje.get_content()).group(1)

        cambio = self.client.post("/api/password/restablecer", json={
            "token": token,
            "nuevaContrasena": "NuevaClave456",
        })
        repetido = self.client.post("/api/password/restablecer", json={
            "token": token,
            "nuevaContrasena": "OtraClave789",
        })
        acceso = self.client.post("/api/login", json={
            "correo": usuario.correo,
            "password": "NuevaClave456",
        })

        self.assertEqual(cambio.status_code, 200, cambio.get_json())
        self.assertEqual(repetido.status_code, 400)
        self.assertEqual(acceso.status_code, 200)

    def test_admin_desactiva_y_reactiva_cuenta_sin_borrar_su_historial(self):
        admin = self.crear_usuario("admin@test.local", "A-1", admin=True)
        paciente = self.crear_usuario("paciente@test.local", "P-1", paciente=True)
        token_admin, _ = self.token_para(admin.correo)
        token_paciente, _ = self.token_para(paciente.correo)
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        headers_paciente = {"Authorization": f"Bearer {token_paciente}"}

        desactivar = self.client.patch(
            f"/api/admin/usuarios/{paciente.idUsuario}/estado",
            headers=headers_admin,
            json={"activo": False},
        )
        sesion_abierta = self.client.get("/api/perfil", headers=headers_paciente)
        nuevo_login = self.client.post("/api/login", json={"correo": paciente.correo, "password": "Clave123"})
        reactivar = self.client.patch(
            f"/api/admin/usuarios/{paciente.idUsuario}/estado",
            headers=headers_admin,
            json={"activo": True},
        )
        login_reactivado = self.client.post("/api/login", json={"correo": paciente.correo, "password": "Clave123"})
        desactivar_admin = self.client.patch(
            f"/api/admin/usuarios/{admin.idUsuario}/estado",
            headers=headers_admin,
            json={"activo": False},
        )

        self.assertEqual(desactivar.status_code, 200, desactivar.get_json())
        self.assertEqual(sesion_abierta.status_code, 401)
        self.assertEqual(nuevo_login.status_code, 401)
        self.assertEqual(reactivar.status_code, 200, reactivar.get_json())
        self.assertEqual(login_reactivado.status_code, 200)
        self.assertEqual(desactivar_admin.status_code, 409)
        self.assertIsNotNone(db.session.get(Paciente, paciente.paciente.idPaciente))

    def test_opciones_de_medicamento_y_creacion_aceptan_ids_del_catalogo(self):
        paciente = self.crear_usuario("paciente@test.local", "P-1", paciente=True)
        token, _ = self.token_para(paciente.correo)
        headers = {"Authorization": f"Bearer {token}"}

        opciones = self.client.get("/api/medicamentos/opciones", headers=headers)
        self.assertEqual(opciones.status_code, 200, opciones.get_json())
        self.assertEqual(opciones.get_json()["tipos"][0]["id"], 1)
        self.assertEqual(opciones.get_json()["vias"][0]["id"], 1)

        creado = self.client.post("/api/medicamentos", headers=headers, json={
            "nombre": "Medicamento de prueba",
            "dosis": "500 mg",
            "idTipoMedicamento": 1,
            "idViaAdministracion": 1,
            "fechaInicio": "2026-01-01",
            "fechaFin": "2026-12-31",
            "fechaVencimiento": "2027-12-31",
            "horario": "09:00",
            "frecuencia": "Diario",
            "cantidadInicial": 5,
        })

        self.assertEqual(creado.status_code, 201, creado.get_json())
        self.assertEqual(creado.get_json()["via"], "Oral")

    def test_usuario_solo_ve_medicamentos_de_su_paciente(self):
        propio = self.crear_usuario("propio@test.local", "P-1", paciente=True)
        ajeno = self.crear_usuario("ajeno@test.local", "P-2", paciente=True)

        for paciente, nombre in ((propio.paciente, "Propio"), (ajeno.paciente, "Ajeno")):
            tratamiento = Tratamiento(
                fechaInicio=date(2026, 1, 1),
                fechaFin=date(2027, 1, 1),
                idPaciente=paciente.idPaciente,
            )
            stock = StockDisponible(
                fechaActualizacion=date(2026, 1, 1),
                cantidadFrascos=0,
                cantidadPastillas=0,
            )
            db.session.add_all((tratamiento, stock))
            db.session.flush()
            db.session.add(Medicamento(
                nombre=nombre,
                concentracion=500,
                unidadConcentracion="mg",
                frecuenciaDiaria=1,
                horario=time(9, 0),
                frecuencia="Diario",
                fechaVencimiento=date(2027, 1, 1),
                idTratamiento=tratamiento.idTratamiento,
                idTipoMedicamento=1,
                idViaAdministracion=1,
                idStock=stock.idStock,
            ))
        db.session.commit()

        token, _ = self.token_para(propio.correo)
        response = self.client.get(
            "/api/medicamentos",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual([med["nombre"] for med in response.get_json()], ["Propio"])


if __name__ == "__main__":
    unittest.main()
