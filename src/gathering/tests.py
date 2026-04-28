from django.test import TestCase
from django.utils import timezone
from django.forms.models import model_to_dict
import json

from .models import Gathering


class GatheringModelTests(TestCase):
    def test_create_gathering_minimal(self):
        dt = timezone.now()
        g = Gathering.objects.create(name="Reunião Rápida", date=dt, location="Sala 2")
        self.assertEqual(g.name, "Reunião Rápida")
        self.assertEqual(g.location, "Sala 2")
        self.assertEqual(g.date, dt)
        self.assertIsNone(g.description)

    def test_str_returns_name(self):
        g = Gathering.objects.create(
            name="Anual", date=timezone.now(), location="Auditório"
        )
        self.assertEqual(str(g), "Anual")

    def test_timestamps_present(self):
        g = Gathering.objects.create(name="T1", date=timezone.now(), location="X")
        self.assertTrue(hasattr(g, "created"))
        self.assertTrue(hasattr(g, "modified"))
        self.assertIsNotNone(g.created)
        self.assertIsNotNone(g.modified)

    def test_json_serialization(self):
        dt = timezone.now()
        g = Gathering.objects.create(
            name="Teste JSON", date=dt, location="Local", description="Desc"
        )
        d = model_to_dict(g)
        d["date"] = d["date"].isoformat()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["name"], "Teste JSON")
        self.assertEqual(parsed["location"], "Local")
        self.assertEqual(parsed["description"], "Desc")
        self.assertEqual(parsed["date"], dt.isoformat())
