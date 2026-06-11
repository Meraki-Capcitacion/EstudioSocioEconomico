import concurrent.futures

from django.test import TestCase, TransactionTestCase

from apps.configuracion.models import TipoEstudio
from apps.personas.models import Persona


def _crear_persona(**kwargs):
    defaults = {
        'nombre': 'Juan',
        'apellido_paterno': 'García',
        'email': 'juan@example.com',
        'telefono_movil': '5551234567',
        'curp': 'GAAJ900101HDFRNN01',
    }
    defaults.update(kwargs)
    return Persona.objects.create(**defaults)


class TestPersonaFolio(TestCase):

    def test_folio_se_genera_al_crear(self):
        persona = _crear_persona()
        self.assertIsNotNone(persona.folio)
        self.assertNotEqual(persona.folio, '')

    def test_folio_formato_yyyymmnnnnn(self):
        from django.utils import timezone
        persona = _crear_persona()
        now = timezone.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        self.assertTrue(persona.folio.startswith(f'{year}{month}'),
                        f'Folio {persona.folio!r} no empieza con {year}{month}')
        self.assertEqual(len(persona.folio), 10,
                         f'Folio {persona.folio!r} debe tener 10 caracteres')

    def test_folio_inicia_en_0001(self):
        persona = _crear_persona()
        self.assertTrue(persona.folio.endswith('0001'),
                        f'Primer folio del mes debe terminar en 0001, es {persona.folio!r}')

    def test_folio_no_se_sobreescribe_en_update(self):
        persona = _crear_persona()
        folio_original = persona.folio
        persona.nombre = 'Pedro'
        persona.save()
        persona.refresh_from_db()
        self.assertEqual(persona.folio, folio_original)


class TestPersonaFolioSecuencial(TestCase):

    def test_dos_personas_folios_distintos(self):
        p1 = _crear_persona(email='a@example.com', curp='GAAJ900101HDFRNN01')
        p2 = _crear_persona(email='b@example.com', curp='GAAJ900101HDFRNN02')
        self.assertNotEqual(p1.folio, p2.folio)

    def test_segundo_folio_es_consecutivo(self):
        p1 = _crear_persona(email='a@example.com', curp='GAAJ900101HDFRNN01')
        p2 = _crear_persona(email='b@example.com', curp='GAAJ900101HDFRNN02')
        seq1 = int(p1.folio[-4:])
        seq2 = int(p2.folio[-4:])
        self.assertEqual(seq2, seq1 + 1)

    def test_nombre_se_normaliza_a_title_case(self):
        persona = _crear_persona(nombre='JUAN CARLOS', apellido_paterno='garcía')
        self.assertEqual(persona.nombre, 'Juan Carlos')
        self.assertEqual(persona.apellido_paterno, 'García')


class TestPersonaFolioConcurrencia(TransactionTestCase):
    """
    Verifica que pg_advisory_xact_lock serializa la generación de folios bajo carga concurrente.
    Solo aplica a PostgreSQL; en SQLite no hay concurrencia real en tests.
    """

    def tearDown(self):
        from django.db import connections
        connections.close_all()
        super().tearDown()

    def test_folios_unicos_con_creacion_concurrente(self):
        import uuid as uuid_mod
        from django.db import close_old_connections, connection

        if connection.vendor != 'postgresql':
            self.skipTest('Advisory locks solo disponibles en PostgreSQL')

        N = 8

        def crear():
            close_old_connections()
            email = f'{uuid_mod.uuid4().hex[:8]}@test.com'
            curp = f'CONC{uuid_mod.uuid4().hex[:14].upper()}'[:18]
            folio = Persona.objects.create(
                nombre='Test', apellido_paterno='Concurrente',
                email=email, telefono_movil='5550000000', curp=curp,
            ).folio
            close_old_connections()
            return folio

        with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
            folios = list(executor.map(lambda _: crear(), range(N)))

        self.assertEqual(len(folios), len(set(folios)),
                         f'Folios duplicados encontrados: {folios}')
