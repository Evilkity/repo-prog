import csv
import json
import logging
import os
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from core.models import Task

logger = logging.getLogger("import_tasks")


class Command(BaseCommand):
    help = "Importa tareas desde múltiples proveedores (JSON, CSV, XML)"

    def handle(self, *args, **options):
        # Tarea Clase 2: Logging a archivo import.log
        handler = logging.FileHandler("import.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)

        total = 0
        total += self._import_json("data/tasks_provider_a.json", "proveedor_a")
        total += self._import_csv("data/tasks_provider_b.csv", "proveedor_b")
        total += self._import_xml("data/tasks_provider_c.xml", "proveedor_c")
        if os.path.exists("data/tasks_provider_d.json"):
            total += self._import_json("data/tasks_provider_d.json", "proveedor_d")

        self.stdout.write(
            self.style.SUCCESS(f"Importación finalizada: {total} tareas cargadas.")
        )
        logger.info(f"Importación finalizada. Total tareas: {total}")

    def _import_json(self, path, source):
        count = 0
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                if self._crear_task(item, source):
                    count += 1
        except (FileNotFoundError, json.JSONDecodeError) as e:
            msg = f"Error importando {path}: {e}"
            self.stderr.write(self.style.ERROR(msg))
            logger.error(msg)
        return count

    def _import_csv(self, path, source):
        count = 0
        try:
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if self._crear_task(row, source):
                        count += 1
        except FileNotFoundError as e:
            msg = f"Error importando {path}: {e}"
            self.stderr.write(self.style.ERROR(msg))
            logger.error(msg)
        return count

    def _import_xml(self, path, source):
        count = 0
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for task_el in root.findall("task"):
                item = {
                    "title": task_el.find("title").text if task_el.find("title") is not None else "",
                    "priority": task_el.find("priority").text if task_el.find("priority") is not None else "media",
                    "status": task_el.find("status").text if task_el.find("status") is not None else "pendiente",
                }
                if self._crear_task(item, source):
                    count += 1
        except (FileNotFoundError, ET.ParseError) as e:
            msg = f"Error importando {path}: {e}"
            self.stderr.write(self.style.ERROR(msg))
            logger.error(msg)
        return count

    def _crear_task(self, item, source):
        title = item.get("title")
        if not title:
            msg = f"Item sin título en {source}, se ignora: {item}"
            self.stderr.write(self.style.WARNING(msg))
            logger.warning(msg)
            return False
        Task.objects.create(
            title=title,
            priority=item.get("priority", "media"),
            status=item.get("status", "pendiente"),
            source=source,
        )
        return True
