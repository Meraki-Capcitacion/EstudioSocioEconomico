import uuid
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.configuracion.models import TipoEstudio
from apps.estudios.models import EstudioSocioeconomico, EstudioToken
from apps.personas.models import Persona


def _crear_token(activo=True, dias_expiracion=30, sufijo='01'):
    tipo = TipoEstudio.objects.get_or_create(nombre='Estándar', defaults={'orden': 1})[0]
    persona = Persona.objects.create(
        nombre='María', apellido_paterno='Hernández',
        email=f'maria{sufijo}@test.com', telefono_movil='5559876543',
        curp=f'HEMM9001{sufijo}MDFABC01'[:18],
    )
    estudio = EstudioSocioeconomico.objects.create(persona=persona, tipo_estudio=tipo)
    token = EstudioToken.objects.create(
        estudio=estudio,
        activo=activo,
        fecha_expiracion=timezone.now() + timedelta(days=dias_expiracion),
    )
    return token


# ---------------------------------------------------------------------------
# Tests de BienvenidaView
# ---------------------------------------------------------------------------

class TestBienvenidaView(TestCase):

    def test_token_valido_retorna_200(self):
        token = _crear_token(sufijo='01')
        url = reverse('candidato:bienvenida', kwargs={'token': token.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidato/bienvenida.html')

    def test_token_invalido_muestra_pagina_error(self):
        uuid_inexistente = uuid.uuid4()
        url = reverse('candidato:bienvenida', kwargs={'token': uuid_inexistente})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidato/token_invalido.html')

    def test_token_completado_muestra_pagina_error(self):
        token = _crear_token(activo=False, sufijo='02')
        url = reverse('candidato:bienvenida', kwargs={'token': token.token})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'candidato/token_invalido.html')

    def test_token_expirado_muestra_pagina_error(self):
        token = _crear_token(dias_expiracion=-1, sufijo='03')
        url = reverse('candidato:bienvenida', kwargs={'token': token.token})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'candidato/token_invalido.html')

    def test_contexto_incluye_nombre_candidato(self):
        token = _crear_token(sufijo='04')
        url = reverse('candidato:bienvenida', kwargs={'token': token.token})
        response = self.client.get(url)
        self.assertContains(response, 'María')


# ---------------------------------------------------------------------------
# Tests de acceso a pasos con token inválido
# ---------------------------------------------------------------------------

class TestPasoConTokenInvalido(TestCase):

    def test_paso1_con_uuid_inexistente_redirige_a_token_invalido(self):
        uuid_inexistente = uuid.uuid4()
        url = reverse('candidato:paso', kwargs={'token': uuid_inexistente, 'n': 1})
        response = self.client.get(url)
        # Paso1View hace redirect a candidato:token_invalido cuando el token no existe
        self.assertEqual(response.status_code, 302)
        self.assertIn('/invalido/', response['Location'])

    def test_paso1_con_token_completado_redirige_a_token_invalido(self):
        token = _crear_token(activo=False, sufijo='05')
        url = reverse('candidato:paso', kwargs={'token': token.token, 'n': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/invalido/', response['Location'])


# ---------------------------------------------------------------------------
# Tests de Paso1View
# ---------------------------------------------------------------------------

class TestPaso1View(TestCase):

    def test_get_paso1_retorna_200(self):
        token = _crear_token(sufijo='06')
        url = reverse('candidato:paso', kwargs={'token': token.token, 'n': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidato/paso_1.html')

    def test_post_paso1_datos_validos_redirige_a_paso2(self):
        token = _crear_token(sufijo='07')
        url = reverse('candidato:paso', kwargs={'token': token.token, 'n': 1})
        datos = {
            'nombre': 'María',
            'apellido_paterno': 'Hernández',
            'apellido_materno': '',
            'fecha_nacimiento': '1990-01-15',
            'tipo_identificacion': 'INE',
            'numero_identificacion': 'ABC123456',
            'curp': 'HEMM900115MDFABC01',
            'email': 'maria07@test.com',
            'telefono_movil': '5559876543',
            'estado_civil': 'SOL',
            'numero_dependientes': 0,
        }
        response = self.client.post(url, datos)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/paso/2/', response['Location'])

    def test_post_paso1_datos_invalidos_retorna_200_con_errores(self):
        token = _crear_token(sufijo='08')
        url = reverse('candidato:paso', kwargs={'token': token.token, 'n': 1})
        # POST vacío — faltarán campos requeridos
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidato/paso_1.html')


# ---------------------------------------------------------------------------
# Test de GraciasView y ciclo de vida del token
# ---------------------------------------------------------------------------

class TestGraciasView(TestCase):

    def test_gracias_con_token_completado_retorna_200(self):
        token = _crear_token(activo=False, sufijo='09')
        url = reverse('candidato:gracias', kwargs={'token': token.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidato/gracias.html')
