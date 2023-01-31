import datetime
import json
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.views.generic.base import View
from contadores.fn_contador import get_contador_sucdiv
from inventario.models import InvFisico, InvBodegas, InvIngresos, InvConteo
from sistema.constantes import DIVISA_ID


