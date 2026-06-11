import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.configuracion.models import TipoEstudio
from apps.estudios.models import EstudioSocioeconomico
from apps.personas.models import Persona


def _crear_estudio(sufijo='01'):
    tipo = TipoEstudio.objects.get_or_create(nombre='Estándar', defaults={'orden': 1})[0]
    persona = Persona.objects.create(
        nombre='Roberto', apellido_paterno='Sánchez',
        email=f'roberto{sufijo}@test.com', telefono_movil='5554445566',
        curp=f'SARR9001{sufijo}HDFABC01'[:18],
    )
    return EstudioSocioeconomico.objects.create(persona=persona, tipo_estudio=tipo)


def _mock_respuesta_ia(contenido_json: dict):
    """Crea un mock de respuesta de openai.OpenAI compatible con la vista."""
    mock_mensaje = MagicMock()
    mock_mensaje.content = json.dumps(contenido_json)
    mock_choice = MagicMock()
    mock_choice.message = mock_mensaje
    mock_respuesta = MagicMock()
    mock_respuesta.choices = [mock_choice]
    return mock_respuesta


# ---------------------------------------------------------------------------
# Tests de AnalizarEstudioIAView
# ---------------------------------------------------------------------------

class TestAnalizarEstudioIAView(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user('analista_ia', password='pass123')
        self.client.login(username='analista_ia', password='pass123')

    def test_sin_api_key_retorna_503(self):
        estudio = _crear_estudio(sufijo='01')
        url = reverse('estudios:analizar_ia', kwargs={'pk': estudio.pk})
        with self.settings(DO_MODEL_ACCESS_KEY=''):
            response = self.client.post(url)
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertIn('error', data)

    @patch('apps.estudios.views_ia._cliente_ia')
    def test_analisis_exitoso_guarda_en_bd(self, mock_cliente_factory):
        estudio = _crear_estudio(sufijo='02')
        payload = {
            'aspectos_positivos': 'Perfil sólido con experiencia comprobable.',
            'aspectos_negativos': 'Sin comentarios negativos relevantes.',
            'conclusion': 'Se recomienda al candidato para el puesto.',
        }
        mock_cliente_factory.return_value.chat.completions.create.return_value = (
            _mock_respuesta_ia(payload)
        )

        url = reverse('estudios:analizar_ia', kwargs={'pk': estudio.pk})
        with self.settings(DO_MODEL_ACCESS_KEY='fake-key'):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('ok'))

        estudio.refresh_from_db()
        self.assertEqual(estudio.aspectos_positivos, payload['aspectos_positivos'])
        self.assertEqual(estudio.aspectos_negativos, payload['aspectos_negativos'])
        self.assertEqual(estudio.conclusion, payload['conclusion'])

    @patch('apps.estudios.views_ia._cliente_ia')
    def test_respuesta_json_malformado_retorna_500(self, mock_cliente_factory):
        estudio = _crear_estudio(sufijo='03')
        mock_mensaje = MagicMock()
        mock_mensaje.content = 'esto no es json válido'
        mock_choice = MagicMock()
        mock_choice.message = mock_mensaje
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        mock_cliente_factory.return_value.chat.completions.create.return_value = mock_resp

        url = reverse('estudios:analizar_ia', kwargs={'pk': estudio.pk})
        with self.settings(DO_MODEL_ACCESS_KEY='fake-key'):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_sin_login_retorna_302(self):
        self.client.logout()
        estudio = _crear_estudio(sufijo='04')
        url = reverse('estudios:analizar_ia', kwargs={'pk': estudio.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# Tests de SugerirEvaluacionIAView
# ---------------------------------------------------------------------------

class TestSugerirEvaluacionIAView(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user('analista_eval', password='pass123')
        self.client.login(username='analista_eval', password='pass123')

    def test_sin_api_key_retorna_503(self):
        estudio = _crear_estudio(sufijo='05')
        url = reverse('estudios:evaluar_ia', kwargs={'pk': estudio.pk})
        with self.settings(DO_MODEL_ACCESS_KEY=''):
            response = self.client.post(url)
        self.assertEqual(response.status_code, 503)

    @patch('apps.estudios.views_ia._cliente_ia')
    def test_sugerencia_retorna_json_con_seis_puntuaciones(self, mock_cliente_factory):
        estudio = _crear_estudio(sufijo='06')
        payload = {
            'puntuacion_identificacion': 85,
            'puntuacion_domicilio': 75,
            'puntuacion_laboral': 90,
            'puntuacion_economica': 70,
            'puntuacion_crediticia': 80,
            'puntuacion_referencias': 88,
            'factores_riesgo': 'Ninguno relevante.',
            'factores_atenuantes': 'Estabilidad laboral.',
            'recomendacion_final': 'Se recomienda su contratación.',
        }
        mock_cliente_factory.return_value.chat.completions.create.return_value = (
            _mock_respuesta_ia(payload)
        )

        url = reverse('estudios:evaluar_ia', kwargs={'pk': estudio.pk})
        with self.settings(DO_MODEL_ACCESS_KEY='fake-key'):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('ok'))
        for campo in ('puntuacion_identificacion', 'puntuacion_domicilio', 'puntuacion_laboral',
                      'puntuacion_economica', 'puntuacion_crediticia', 'puntuacion_referencias'):
            self.assertIn(campo, data)

    @patch('apps.estudios.views_ia._cliente_ia')
    def test_sugerencia_no_guarda_en_bd(self, mock_cliente_factory):
        estudio = _crear_estudio(sufijo='07')
        payload = {
            'puntuacion_identificacion': 85, 'puntuacion_domicilio': 75,
            'puntuacion_laboral': 90, 'puntuacion_economica': 70,
            'puntuacion_crediticia': 80, 'puntuacion_referencias': 88,
            'factores_riesgo': 'Ninguno.', 'factores_atenuantes': 'Estable.',
            'recomendacion_final': 'Apto.',
        }
        mock_cliente_factory.return_value.chat.completions.create.return_value = (
            _mock_respuesta_ia(payload)
        )

        url = reverse('estudios:evaluar_ia', kwargs={'pk': estudio.pk})
        with self.settings(DO_MODEL_ACCESS_KEY='fake-key'):
            self.client.post(url)

        # No debe haber creado EvaluacionRiesgo
        from apps.evaluacion.models import EvaluacionRiesgo
        self.assertFalse(EvaluacionRiesgo.objects.filter(estudio=estudio).exists())
