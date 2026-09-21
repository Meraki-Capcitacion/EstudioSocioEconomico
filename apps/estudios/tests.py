import re
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

SIMPLE_STORAGE = override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
)

from apps.configuracion.models import TipoEstudio
from apps.estudios.models import EstudioSocioeconomico, EstudioToken
from apps.estudios.views import TRANSICIONES_VALIDAS
from apps.personas.models import Persona


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _crear_persona(sufijo='01'):
    return Persona.objects.create(
        nombre='Juan', apellido_paterno='García',
        email=f'juan{sufijo}@test.com', telefono_movil='5551234567',
        curp=f'GARJ9001{sufijo}HDFABC01'[:18],
    )


def _crear_estudio(estado='BOR', sufijo='01'):
    tipo = TipoEstudio.objects.get_or_create(nombre='Estándar', defaults={'orden': 1})[0]
    persona = _crear_persona(sufijo=sufijo)
    return EstudioSocioeconomico.objects.create(
        persona=persona, tipo_estudio=tipo, estado=estado,
    )


def _crear_usuario():
    return User.objects.create_user('analista', password='testpass123')


# ---------------------------------------------------------------------------
# Tests de transiciones de estado
# ---------------------------------------------------------------------------

class TestTransicionesEstado(TestCase):

    def test_bor_puede_ir_a_vis(self):
        self.assertIn('VIS', TRANSICIONES_VALIDAS['BOR'])

    def test_bor_puede_cancelarse(self):
        self.assertIn('CAN', TRANSICIONES_VALIDAS['BOR'])

    def test_bor_no_puede_ir_a_apr(self):
        self.assertNotIn('APR', TRANSICIONES_VALIDAS['BOR'])

    def test_com_no_puede_cancelarse(self):
        self.assertNotIn('CAN', TRANSICIONES_VALIDAS['COM'])

    def test_rev_puede_ir_a_apr_o_rec(self):
        self.assertIn('APR', TRANSICIONES_VALIDAS['REV'])
        self.assertIn('REC', TRANSICIONES_VALIDAS['REV'])

    def test_apr_es_estado_terminal(self):
        self.assertEqual(TRANSICIONES_VALIDAS['APR'], [])

    def test_can_es_estado_terminal(self):
        self.assertEqual(TRANSICIONES_VALIDAS['CAN'], [])

    def test_rec_puede_regresar_a_bor(self):
        self.assertIn('BOR', TRANSICIONES_VALIDAS['REC'])

    def test_flujo_completo_valido(self):
        flujo = ['BOR', 'VIS', 'PRO', 'COM', 'REV', 'APR']
        for i in range(len(flujo) - 1):
            self.assertIn(flujo[i + 1], TRANSICIONES_VALIDAS[flujo[i]],
                          f'{flujo[i]} → {flujo[i+1]} debería ser válido')


# ---------------------------------------------------------------------------
# Tests de CambiarEstadoView
# ---------------------------------------------------------------------------

@SIMPLE_STORAGE
class TestCambiarEstadoView(TestCase):

    def setUp(self):
        self.usuario = _crear_usuario()
        self.client.login(username='analista', password='testpass123')

    def test_transicion_valida_cambia_estado(self):
        estudio = _crear_estudio(estado='BOR')
        url = reverse('estudios:cambiar_estado', kwargs={'pk': estudio.pk})
        self.client.post(url, {'estado': 'VIS'})
        estudio.refresh_from_db()
        self.assertEqual(estudio.estado, 'VIS')

    def test_transicion_invalida_no_cambia_estado(self):
        estudio = _crear_estudio(estado='BOR')
        url = reverse('estudios:cambiar_estado', kwargs={'pk': estudio.pk})
        self.client.post(url, {'estado': 'APR'})
        estudio.refresh_from_db()
        self.assertEqual(estudio.estado, 'BOR')

    def test_transicion_redirige_al_detalle(self):
        estudio = _crear_estudio(estado='BOR', sufijo='02')
        url = reverse('estudios:cambiar_estado', kwargs={'pk': estudio.pk})
        response = self.client.post(url, {'estado': 'VIS'})
        self.assertRedirects(response, reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk}),
                             fetch_redirect_response=False)

    def test_sin_login_redirige_a_login(self):
        self.client.logout()
        estudio = _crear_estudio(sufijo='03')
        url = reverse('estudios:cambiar_estado', kwargs={'pk': estudio.pk})
        response = self.client.post(url, {'estado': 'VIS'})
        self.assertRedirects(response, f'/accounts/login/?next={url}',
                             fetch_redirect_response=False)


# ---------------------------------------------------------------------------
# Tests de EstudioDetailView
# ---------------------------------------------------------------------------

@SIMPLE_STORAGE
class TestEstudioDetailView(TestCase):

    def setUp(self):
        self.usuario = _crear_usuario()
        self.client.login(username='analista', password='testpass123')

    def test_sin_login_redirige(self):
        self.client.logout()
        estudio = _crear_estudio(sufijo='04')
        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_con_login_retorna_200(self):
        estudio = _crear_estudio(sufijo='05')
        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contexto_incluye_transiciones_validas(self):
        estudio = _crear_estudio(estado='BOR', sufijo='06')
        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        response = self.client.get(url)
        self.assertIn('transiciones_validas', response.context)
        self.assertIn('VIS', response.context['transiciones_validas'])

    def test_contexto_token_none_cuando_no_existe(self):
        estudio = _crear_estudio(sufijo='07')
        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        response = self.client.get(url)
        self.assertIsNone(response.context['token_candidato'])


# ---------------------------------------------------------------------------
# Tests de GenerarTokenView
# ---------------------------------------------------------------------------

@SIMPLE_STORAGE
class TestGenerarTokenView(TestCase):

    def setUp(self):
        self.usuario = _crear_usuario()
        self.client.login(username='analista', password='testpass123')

    def test_genera_token_en_estudio_sin_token(self):
        estudio = _crear_estudio(sufijo='08')
        url = reverse('estudios:generar_token', kwargs={'pk': estudio.pk})
        self.client.post(url)
        self.assertTrue(EstudioToken.objects.filter(estudio=estudio).exists())

    def test_token_generado_es_vigente(self):
        estudio = _crear_estudio(sufijo='09')
        url = reverse('estudios:generar_token', kwargs={'pk': estudio.pk})
        self.client.post(url)
        token = EstudioToken.objects.get(estudio=estudio)
        self.assertTrue(token.vigente)

    def test_regenerar_invalida_token_anterior(self):
        estudio = _crear_estudio(sufijo='10')
        # Generar primer token
        gen_url = reverse('estudios:generar_token', kwargs={'pk': estudio.pk})
        self.client.post(gen_url)
        token_anterior = EstudioToken.objects.get(estudio=estudio)
        uuid_anterior = token_anterior.token

        # Regenerar
        regen_url = reverse('estudios:regenerar_token', kwargs={'pk': estudio.pk})
        self.client.post(regen_url)

        # El token anterior ya no existe
        self.assertFalse(EstudioToken.objects.filter(token=uuid_anterior).exists())
        # Existe uno nuevo
        self.assertTrue(EstudioToken.objects.filter(estudio=estudio).exists())


# ---------------------------------------------------------------------------
# Tests de coherencia de pestañas del expediente
# ---------------------------------------------------------------------------

def _tabs_renderizadas(html):
    """
    Devuelve (claves de los botones, claves de los paneles) del detalle.

    Los botones se leen solo dentro de <nav>, porque más abajo el bloque
    de JavaScript también contiene la cadena `data-tab=` dentro de
    selectores construidos en tiempo de ejecución.
    """
    nav = re.search(
        r'<nav\b[^>]*aria-label="Secciones del estudio".*?</nav>', html, re.DOTALL
    )
    botones = set(re.findall(r'data-tab="([^"]+)"', nav.group(0) if nav else ''))
    paneles = set(re.findall(r'id="tab-([^"]+)"', html))
    return botones, paneles


@SIMPLE_STORAGE
class TestTabsExpediente(TestCase):
    """
    Protege el contrato entre la vista y la plantilla: cada botón
    `data-tab="X"` necesita un panel `id="tab-X"`. Cuando ambos se
    desincronizan, la pestaña se abre vacía sin ningún error visible,
    que es exactamente el fallo que este test evita que regrese.
    """

    def setUp(self):
        self.usuario = _crear_usuario()
        self.client.login(username='analista', password='testpass123')

    def _html_detalle(self, estudio):
        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        return self.client.get(url).content.decode()

    def test_cada_boton_tiene_su_panel(self):
        estudio = _crear_estudio(sufijo='20')
        estudio.tipo_estudio.secciones = [
            clave for clave, _ in TipoEstudio.SECCIONES_DISPONIBLES
        ]
        estudio.tipo_estudio.save()

        botones, paneles = _tabs_renderizadas(self._html_detalle(estudio))

        self.assertTrue(botones, 'La plantilla no renderizó ningún botón de pestaña')
        self.assertEqual(
            botones - paneles, set(),
            'Hay botones de pestaña sin su panel correspondiente',
        )

    def test_toda_seccion_del_catalogo_tiene_panel(self):
        """Ninguna sección configurable puede quedarse sin panel."""
        estudio = _crear_estudio(sufijo='21')
        estudio.tipo_estudio.secciones = [
            clave for clave, _ in TipoEstudio.SECCIONES_DISPONIBLES
        ]
        estudio.tipo_estudio.save()

        _, paneles = _tabs_renderizadas(self._html_detalle(estudio))
        catalogo = {clave for clave, _ in TipoEstudio.SECCIONES_DISPONIBLES}

        self.assertEqual(catalogo - paneles, set())

    def test_tab_list_respeta_las_secciones_configuradas(self):
        estudio = _crear_estudio(sufijo='22')
        estudio.tipo_estudio.secciones = ['domicilios', 'economia']
        estudio.tipo_estudio.save()

        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        tab_list = self.client.get(url).context['tab_list']

        self.assertEqual([clave for clave, _ in tab_list],
                         ['resumen', 'domicilios', 'economia'])

    def test_seccion_desconocida_se_descarta(self):
        """Un valor obsoleto en `secciones` no debe generar una pestaña rota."""
        estudio = _crear_estudio(sufijo='23')
        estudio.tipo_estudio.secciones = ['domicilio', 'economico', 'familia']
        estudio.tipo_estudio.save()

        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        response = self.client.get(url)
        claves = [clave for clave, _ in response.context['tab_list']]

        self.assertEqual(claves, ['resumen', 'familia'])
        botones, paneles = _tabs_renderizadas(response.content.decode())
        self.assertEqual(botones - paneles, set())

    def test_sin_secciones_muestra_todas_las_pestanas(self):
        estudio = _crear_estudio(sufijo='24')
        estudio.tipo_estudio.secciones = []
        estudio.tipo_estudio.save()

        url = reverse('estudios:estudio_detail', kwargs={'pk': estudio.pk})
        claves = [c for c, _ in self.client.get(url).context['tab_list']]
        catalogo = [clave for clave, _ in TipoEstudio.SECCIONES_DISPONIBLES]

        self.assertEqual(claves, ['resumen'] + catalogo)
