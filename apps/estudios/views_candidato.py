"""Vistas del portal público de autogestión del candidato (Escenario A).

Flujo:
  /candidato/<uuid>/          → bienvenida
  /candidato/<uuid>/paso/1/   → datos personales
  /candidato/<uuid>/paso/2/   → domicilio
  /candidato/<uuid>/paso/3/   → educación, idiomas y salud
  /candidato/<uuid>/paso/4/   → grupo familiar
  /candidato/<uuid>/paso/5/   → situación económica
  /candidato/<uuid>/paso/6/   → referencias
  /candidato/<uuid>/paso/7/   → historial laboral + documentos
  /candidato/<uuid>/gracias/  → confirmación
"""
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from .models import EstudioSocioeconomico, EstudioToken
from .forms_candidato import (
    Paso1PersonaForm, Paso1SelfiForm,
    Paso2DomicilioForm, Paso2FotoForm, FOTOS_DOMICILIO,
    Paso3EducacionForm, Paso3IdiomaForm, Paso3SaludForm,
    Paso4FamiliarForm,
    Paso5EconomiaForm,
    Paso6ReferenciaForm,
    Paso7LaboralForm, Paso7DocumentoForm,
)
from apps.domicilios.models import Domicilio
from apps.economia.models import SituacionEconomica
from apps.personas.models import SaludPersona
from apps.documentos.models import Documento

TOTAL_PASOS = 7


def _get_token_or_error(token_uuid):
    """Retorna (token, error_code). error_code es None si el token es válido."""
    try:
        token = EstudioToken.objects.select_related('estudio__persona').get(token=token_uuid)
    except EstudioToken.DoesNotExist:
        return None, 'invalido'
    if not token.vigente:
        if not token.activo:
            return token, 'completado'
        return token, 'expirado'
    return token, None


# ---------------------------------------------------------------------------
# Portal del candidato
# ---------------------------------------------------------------------------

class BienvenidaView(View):
    """Página de bienvenida — valida el token y muestra instrucciones."""
    template_name = 'candidato/bienvenida.html'

    def get(self, request, token):
        tk, error = _get_token_or_error(token)
        if error:
            return render(request, 'candidato/token_invalido.html', {
                'error': error,
                'token': tk,
            })
        persona = tk.estudio.persona
        return render(request, self.template_name, {
            'token': tk,
            'persona': persona,
            'total_pasos': TOTAL_PASOS,
        })


class PasoBaseView(View):
    """Vista base para todos los pasos del wizard."""
    template_name = None
    paso_actual = None

    def _contexto_base(self, token):
        return {
            'token': token,
            'paso_actual': self.paso_actual,
            'total_pasos': TOTAL_PASOS,
            'pasos_list': range(1, TOTAL_PASOS + 1),
            'porcentaje': int((self.paso_actual / TOTAL_PASOS) * 100),
            'paso_anterior': self.paso_actual - 1 if self.paso_actual > 1 else None,
            'paso_siguiente': self.paso_actual + 1 if self.paso_actual < TOTAL_PASOS else None,
        }

    def _validar_token(self, token_uuid):
        return _get_token_or_error(token_uuid)


class Paso1View(PasoBaseView):
    """Paso 1 — Datos personales, identificaciones y selfie."""
    template_name = 'candidato/paso_1.html'
    paso_actual = 1

    def _ctx_paso1(self, tk):
        persona = tk.estudio.persona
        ctx = self._contexto_base(tk)
        ctx['persona'] = persona
        ctx['selfie'] = persona.documentos.filter(tipo='FSE').first()
        ctx['form_selfie'] = Paso1SelfiForm()
        return ctx, persona

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        ctx, persona = self._ctx_paso1(tk)
        ctx['form'] = Paso1PersonaForm(instance=persona)
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        accion = request.POST.get('accion', '')

        if accion == 'subir_selfie':
            form_selfie = Paso1SelfiForm(request.POST, request.FILES)
            if form_selfie.is_valid() and form_selfie.cleaned_data.get('archivo'):
                archivo = form_selfie.cleaned_data['archivo']
                persona.documentos.filter(tipo='FSE').delete()
                Documento.objects.create(
                    persona=persona,
                    estudio=tk.estudio,
                    tipo='FSE',
                    archivo=archivo,
                    nombre_archivo=archivo.name,
                    tamaño=archivo.size,
                )
                messages.success(request, 'Foto de perfil guardada.')
            return redirect('candidato:paso', token=token, n=1)

        # Guardar datos personales y avanzar
        form = Paso1PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            return redirect('candidato:paso', token=token, n=2)
        ctx, _ = self._ctx_paso1(tk)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class Paso2View(PasoBaseView):
    """Paso 2 — Domicilio, ubicación GPS y fotografías del inmueble."""
    template_name = 'candidato/paso_2.html'
    paso_actual = 2

    _TIPOS_FOTOS_DOM = [t for t, _ in FOTOS_DOMICILIO]

    def _ctx_paso2(self, tk):
        persona = tk.estudio.persona
        fotos_qs = persona.documentos.filter(
            tipo__in=self._TIPOS_FOTOS_DOM,
            estudio=tk.estudio,
        )
        fotos_por_tipo_dict = {f.tipo: f for f in fotos_qs}
        ctx = self._contexto_base(tk)
        ctx['fotos_por_tipo'] = fotos_por_tipo_dict
        ctx['fotos_domicilio'] = FOTOS_DOMICILIO
        # Lista de tuplas (tipo_code, tipo_label, foto_obj_or_None) para uso directo
        # en el template sin necesidad de filtros personalizados de dict lookup.
        ctx['fotos_domicilio_ctx'] = [
            (codigo, label, fotos_por_tipo_dict.get(codigo))
            for codigo, label in FOTOS_DOMICILIO
        ]
        ctx['form_foto'] = Paso2FotoForm()
        return ctx, persona

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        ctx, persona = self._ctx_paso2(tk)
        domicilio = persona.domicilios.filter(tipo='ACT').first()
        ctx['form'] = Paso2DomicilioForm(instance=domicilio)
        ctx['domicilio'] = domicilio
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        accion = request.POST.get('accion', '')

        if accion == 'subir_foto':
            form_foto = Paso2FotoForm(request.POST, request.FILES)
            if form_foto.is_valid() and form_foto.cleaned_data.get('archivo'):
                archivo = form_foto.cleaned_data['archivo']
                tipo = form_foto.cleaned_data['tipo']
                persona.documentos.filter(tipo=tipo, estudio=tk.estudio).delete()
                Documento.objects.create(
                    persona=persona,
                    estudio=tk.estudio,
                    tipo=tipo,
                    archivo=archivo,
                    nombre_archivo=archivo.name,
                    tamaño=archivo.size,
                )
                messages.success(request, 'Foto guardada correctamente.')
            return redirect('candidato:paso', token=token, n=2)

        # Guardar domicilio y continuar
        domicilio = persona.domicilios.filter(tipo='ACT').first()
        form = Paso2DomicilioForm(request.POST, instance=domicilio)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.persona = persona
            obj.tipo = 'ACT'
            obj.save()
            return redirect('candidato:paso', token=token, n=3)
        ctx, _ = self._ctx_paso2(tk)
        ctx['form'] = form
        ctx['domicilio'] = domicilio
        return render(request, self.template_name, ctx)


class Paso3View(PasoBaseView):
    """Paso 3 — Educación, idiomas y salud."""
    template_name = 'candidato/paso_3.html'
    paso_actual = 3

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        educacion_list = persona.educacion.all()
        idioma_list = persona.idiomas.all()
        salud = getattr(persona, 'salud', None)
        ctx = self._contexto_base(tk)
        ctx.update({
            'form_educacion': Paso3EducacionForm(),
            'form_idioma': Paso3IdiomaForm(),
            'form_salud': Paso3SaludForm(instance=salud),
            'educacion_list': educacion_list,
            'idioma_list': idioma_list,
            'salud': salud,
        })
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        accion = request.POST.get('accion', '')

        if accion == 'guardar_educacion':
            form = Paso3EducacionForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.persona = persona
                obj.save()
                messages.success(request, 'Nivel educativo guardado.')
            else:
                salud = getattr(persona, 'salud', None)
                ctx = self._contexto_base(tk)
                ctx.update({
                    'form_educacion': form,
                    'form_idioma': Paso3IdiomaForm(),
                    'form_salud': Paso3SaludForm(instance=salud),
                    'educacion_list': persona.educacion.all(),
                    'idioma_list': persona.idiomas.all(),
                })
                return render(request, self.template_name, ctx)

        elif accion == 'guardar_idioma':
            form = Paso3IdiomaForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.persona = persona
                obj.save()
                messages.success(request, 'Idioma guardado.')
            else:
                salud = getattr(persona, 'salud', None)
                ctx = self._contexto_base(tk)
                ctx.update({
                    'form_educacion': Paso3EducacionForm(),
                    'form_idioma': form,
                    'form_salud': Paso3SaludForm(instance=salud),
                    'educacion_list': persona.educacion.all(),
                    'idioma_list': persona.idiomas.all(),
                })
                return render(request, self.template_name, ctx)

        elif accion == 'guardar_salud':
            salud = getattr(persona, 'salud', None)
            form = Paso3SaludForm(request.POST, instance=salud)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.persona = persona
                obj.save()
                return redirect('candidato:paso', token=token, n=4)
            else:
                ctx = self._contexto_base(tk)
                ctx.update({
                    'form_educacion': Paso3EducacionForm(),
                    'form_idioma': Paso3IdiomaForm(),
                    'form_salud': form,
                    'educacion_list': persona.educacion.all(),
                    'idioma_list': persona.idiomas.all(),
                })
                return render(request, self.template_name, ctx)

        return redirect('candidato:paso', token=token, n=3)


class Paso4View(PasoBaseView):
    """Paso 4 — Grupo familiar."""
    template_name = 'candidato/paso_4.html'
    paso_actual = 4

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        ctx = self._contexto_base(tk)
        ctx.update({
            'form': Paso4FamiliarForm(),
            'familiares': persona.grupo_familiar.all(),
        })
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        accion = request.POST.get('accion', '')

        if accion == 'agregar':
            form = Paso4FamiliarForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.persona = persona
                obj.save()
                messages.success(request, 'Familiar agregado.')
            else:
                ctx = self._contexto_base(tk)
                ctx.update({'form': form, 'familiares': persona.grupo_familiar.all()})
                return render(request, self.template_name, ctx)
        elif accion == 'continuar':
            return redirect('candidato:paso', token=token, n=5)

        return redirect('candidato:paso', token=token, n=4)


class Paso5View(PasoBaseView):
    """Paso 5 — Situación económica y patrimonio."""
    template_name = 'candidato/paso_5.html'
    paso_actual = 5

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        estudio = tk.estudio
        economia = getattr(estudio, 'situacion_economica', None)
        form = Paso5EconomiaForm(instance=economia)
        ctx = self._contexto_base(tk)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        estudio = tk.estudio
        economia = getattr(estudio, 'situacion_economica', None)
        form = Paso5EconomiaForm(request.POST, instance=economia)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.estudio = estudio
            obj.save()
            return redirect('candidato:paso', token=token, n=6)
        ctx = self._contexto_base(tk)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class Paso6View(PasoBaseView):
    """Paso 6 — Referencias personales (mínimo 3)."""
    template_name = 'candidato/paso_6.html'
    paso_actual = 6

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        ctx = self._contexto_base(tk)
        ctx.update({
            'form': Paso6ReferenciaForm(),
            'referencias': persona.referencias.all(),
            'minimo_referencias': 3,
        })
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        accion = request.POST.get('accion', '')

        if accion == 'agregar':
            form = Paso6ReferenciaForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.persona = persona
                obj.save()
                messages.success(request, 'Referencia agregada.')
            else:
                ctx = self._contexto_base(tk)
                ctx.update({
                    'form': form,
                    'referencias': persona.referencias.all(),
                    'minimo_referencias': 3,
                })
                return render(request, self.template_name, ctx)
        elif accion == 'continuar':
            total_refs = persona.referencias.count()
            if total_refs < 3:
                messages.warning(request, f'Por favor agrega al menos 3 referencias. Tienes {total_refs}.')
                return redirect('candidato:paso', token=token, n=6)
            return redirect('candidato:paso', token=token, n=7)

        return redirect('candidato:paso', token=token, n=6)


class Paso7View(PasoBaseView):
    """Paso 7 — Historial laboral y subida de documentos."""
    template_name = 'candidato/paso_7.html'
    paso_actual = 7

    def get(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        ctx = self._contexto_base(tk)
        ctx.update({
            'form_laboral': Paso7LaboralForm(),
            'form_documento': Paso7DocumentoForm(),
            'empleos': persona.historial_laboral.all(),
            'documentos': tk.estudio.documentos.all(),
        })
        return render(request, self.template_name, ctx)

    def post(self, request, token):
        tk, error = self._validar_token(token)
        if error:
            return redirect('candidato:token_invalido', token=token)
        persona = tk.estudio.persona
        accion = request.POST.get('accion', '')

        if accion == 'agregar_empleo':
            form = Paso7LaboralForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.persona = persona
                obj.save()
                messages.success(request, 'Empleo guardado.')
            else:
                ctx = self._contexto_base(tk)
                ctx.update({
                    'form_laboral': form,
                    'form_documento': Paso7DocumentoForm(),
                    'empleos': persona.historial_laboral.all(),
                    'documentos': tk.estudio.documentos.all(),
                })
                return render(request, self.template_name, ctx)

        elif accion == 'subir_documento':
            form = Paso7DocumentoForm(request.POST, request.FILES)
            if form.is_valid():
                archivo = form.cleaned_data['archivo']
                doc = Documento(
                    persona=persona,
                    estudio=tk.estudio,
                    tipo=form.cleaned_data['tipo'],
                    archivo=archivo,
                    nombre_archivo=archivo.name,
                    tamaño=archivo.size,
                )
                doc.save()
                messages.success(request, 'Documento subido correctamente.')
            else:
                ctx = self._contexto_base(tk)
                ctx.update({
                    'form_laboral': Paso7LaboralForm(),
                    'form_documento': form,
                    'empleos': persona.historial_laboral.all(),
                    'documentos': tk.estudio.documentos.all(),
                })
                return render(request, self.template_name, ctx)

        elif accion == 'finalizar':
            # Marcar el token como inactivo (completado) y avanzar el estudio a PRO si está en BOR
            tk.activo = False
            tk.save()
            estudio = tk.estudio
            if estudio.estado == 'BOR':
                estudio.estado = 'PRO'
                estudio.save()
            return redirect('candidato:gracias', token=token)

        return redirect('candidato:paso', token=token, n=7)


class GraciasView(View):
    """Página de confirmación de envío."""
    template_name = 'candidato/gracias.html'

    def get(self, request, token):
        try:
            tk = EstudioToken.objects.select_related('estudio__persona').get(token=token)
        except EstudioToken.DoesNotExist:
            return redirect('home')
        return render(request, self.template_name, {'token': tk})


class TokenInvalidoView(View):
    """Página de error para tokens inválidos, expirados o ya completados."""
    template_name = 'candidato/token_invalido.html'

    def get(self, request, token):
        tk, error = _get_token_or_error(token)
        return render(request, self.template_name, {'error': error, 'token': tk})


# ---------------------------------------------------------------------------
# Vistas del analista para gestionar tokens (requieren login)
# ---------------------------------------------------------------------------

class GenerarTokenView(LoginRequiredMixin, View):
    """Genera un nuevo token para un estudio. Invalida el anterior si existe."""

    def post(self, request, pk):
        from datetime import timedelta
        estudio = get_object_or_404(EstudioSocioeconomico, pk=pk)

        # Invalidar token anterior si existe
        try:
            token_anterior = estudio.token
            token_anterior.activo = False
            token_anterior.save()
        except EstudioToken.DoesNotExist:
            pass

        # Crear nuevo token con expiración de 30 días
        EstudioToken.objects.create(
            estudio=estudio,
            fecha_expiracion=timezone.now() + timedelta(days=30),
        )
        messages.success(request, 'Link generado para el candidato. Copíalo y compártelo.')
        return redirect('estudios:estudio_detail', pk=pk)


class RegenerarTokenView(LoginRequiredMixin, View):
    """Regenera el token de un estudio, invalidando el anterior."""

    def post(self, request, pk):
        from datetime import timedelta
        estudio = get_object_or_404(EstudioSocioeconomico, pk=pk)

        try:
            token_anterior = estudio.token
            token_anterior.delete()
        except EstudioToken.DoesNotExist:
            pass

        EstudioToken.objects.create(
            estudio=estudio,
            fecha_expiracion=timezone.now() + timedelta(days=30),
        )
        messages.success(request, 'Token regenerado. El link anterior ya no es válido.')
        return redirect('estudios:estudio_detail', pk=pk)


# ---------------------------------------------------------------------------
# Dispatcher de pasos (router hacia la vista correcta)
# ---------------------------------------------------------------------------

PASO_VIEWS = {
    1: Paso1View,
    2: Paso2View,
    3: Paso3View,
    4: Paso4View,
    5: Paso5View,
    6: Paso6View,
    7: Paso7View,
}


class PasoDispatcherView(View):
    """Despacha la petición al PasoXView correspondiente."""

    def dispatch(self, request, token, n):
        vista_class = PASO_VIEWS.get(n)
        if vista_class is None:
            return redirect('candidato:bienvenida', token=token)
        return vista_class.as_view()(request, token=token)
