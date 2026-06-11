from decimal import Decimal

from django.test import TestCase

from apps.configuracion.models import TipoEstudio
from apps.economia.models import SituacionEconomica
from apps.estudios.models import EstudioSocioeconomico
from apps.personas.models import Persona


def _crear_estudio(orden=1, sufijo='01'):
    tipo = TipoEstudio.objects.create(nombre=f'Tipo{sufijo}', orden=orden)
    persona = Persona.objects.create(
        nombre='Ana', apellido_paterno='López',
        email=f'ana{sufijo}@example.com', telefono_movil='5551111111',
        curp=f'LOAA9001{sufijo}MDFPNN01'[:18],
    )
    return EstudioSocioeconomico.objects.create(persona=persona, tipo_estudio=tipo)


class TestSituacionEconomicaProperties(TestCase):

    def setUp(self):
        estudio = _crear_estudio()
        self.eco = SituacionEconomica.objects.create(
            estudio=estudio,
            salario_mensual=Decimal('20000.00'),
            bonos_comisiones=Decimal('2000.00'),
            ingresos_extra=Decimal('500.00'),
            apoyo_familiar=Decimal('0.00'),
            otros_ingresos=Decimal('300.00'),
            gasto_alimentacion=Decimal('4000.00'),
            gasto_vivienda=Decimal('3000.00'),
            gasto_servicios=Decimal('500.00'),
            gasto_transporte=Decimal('1500.00'),
            gasto_educacion=Decimal('1000.00'),
            gasto_salud=Decimal('200.00'),
            gasto_deudas=Decimal('2000.00'),
            otros_gastos=Decimal('300.00'),
        )

    def test_ingreso_total_mensual(self):
        self.assertEqual(self.eco.ingreso_total_mensual, Decimal('22800.00'))

    def test_egreso_total_mensual(self):
        self.assertEqual(self.eco.egreso_total_mensual, Decimal('12500.00'))

    def test_capacidad_ahorro_positiva(self):
        self.assertEqual(self.eco.capacidad_ahorro, Decimal('10300.00'))

    def test_capacidad_ahorro_negativa_cuando_egresos_superan_ingresos(self):
        estudio2 = _crear_estudio(orden=2, sufijo='02')
        eco2 = SituacionEconomica.objects.create(
            estudio=estudio2,
            salario_mensual=Decimal('5000.00'),
            gasto_alimentacion=Decimal('8000.00'),
        )
        self.assertLess(eco2.capacidad_ahorro, Decimal('0'))

    def test_ingreso_total_con_todos_ceros_salvo_salario(self):
        estudio3 = _crear_estudio(orden=3, sufijo='03')
        eco3 = SituacionEconomica.objects.create(
            estudio=estudio3,
            salario_mensual=Decimal('15000.00'),
        )
        self.assertEqual(eco3.ingreso_total_mensual, Decimal('15000.00'))
        self.assertEqual(eco3.egreso_total_mensual, Decimal('0.00'))
        self.assertEqual(eco3.capacidad_ahorro, Decimal('15000.00'))
