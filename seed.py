import os

from app import create_app
from app.database.database import db
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.tipo_documento import TipoDocumento
from app.models.tipo_medicamento import TipoMedicamento
from app.models.via_administracion import ViaAdministracion

app = create_app()

with app.app_context():
    # La primera cuenta administradora se elige explícitamente desde el entorno.
    # El usuario debe registrarse primero desde la aplicación.
    hay_administradores = Administrador.query.first() is not None
    correo_admin_inicial = os.getenv('BOOTSTRAP_ADMIN_EMAIL', '').strip().lower()
    usuario_admin_inicial = None

    if not hay_administradores and correo_admin_inicial:
        usuario_admin_inicial = Usuario.query.filter(
            db.func.lower(Usuario.correo) == correo_admin_inicial
        ).first()
        if usuario_admin_inicial is None:
            raise RuntimeError(
                'BOOTSTRAP_ADMIN_EMAIL debe corresponder a una cuenta ya registrada.'
            )

    tipo_cc = TipoDocumento.query.filter_by(nombre='Cédula de Ciudadanía').first()
    if tipo_cc is None:
        tipo_cc = TipoDocumento(nombre='Cédula de Ciudadanía')
        db.session.add(tipo_cc)
        db.session.flush()

    tipos_medicamento = ['Tableta', 'Cápsula', 'Jarabe', 'Gotas', 'Inyección', 'Crema', 'Inhalador']
    for nombre_tipo in tipos_medicamento:
        if TipoMedicamento.query.filter_by(nombre=nombre_tipo).first() is None:
            db.session.add(TipoMedicamento(nombre=nombre_tipo))

    vias_administracion = ['Oral', 'Intravenosa', 'Subcutánea', 'Tópica', 'Inhalatoria', 'Sublingual']
    for nombre_via in vias_administracion:
        if ViaAdministracion.query.filter_by(nombre=nombre_via).first() is None:
            db.session.add(ViaAdministracion(nombre=nombre_via))

    if usuario_admin_inicial is not None:
        perfil_admin = Administrador(
            nombre=usuario_admin_inicial.nombre,
            apellido=usuario_admin_inicial.apellido,
            correo=usuario_admin_inicial.correo,
            telefono=usuario_admin_inicial.telefono,
            idUsuario=usuario_admin_inicial.idUsuario
        )
        db.session.add(perfil_admin)

    db.session.commit()
    if usuario_admin_inicial is not None:
        print(f'Cuenta registrada promovida a administradora: {correo_admin_inicial}')
    elif not hay_administradores:
        print(
            'Catálogos verificados. No hay administradores; registra una cuenta y configura '
            'BOOTSTRAP_ADMIN_EMAIL para crear el primer perfil administrador.'
        )
    else:
        print('Catálogos verificados. Ya existe al menos un administrador.')
