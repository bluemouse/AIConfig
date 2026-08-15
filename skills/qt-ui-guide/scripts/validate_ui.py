#!/usr/bin/env python3
"""Validate common structural and UX-oriented conventions in Qt Designer .ui files."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

GENERIC_NAME_RE = re.compile(
    r"^(?:widget|pushButton|toolButton|label|lineEdit|comboBox|checkBox|radioButton|"
    r"groupBox|tabWidget|treeView|tableView|listView|horizontalLayout|verticalLayout|"
    r"gridLayout|formLayout|action|spacer)_?\d+$"
)

BUTTON_CLASSES = {"QPushButton", "QToolButton", "QCommandLinkButton"}
MAINWINDOW_MANAGED = {"centralwidget", "menubar", "statusbar"}


def property_node(element: ET.Element, name: str) -> ET.Element | None:
    for prop in element.findall("property"):
        if prop.get("name") == name:
            return prop
    return None


def property_string(element: ET.Element, name: str) -> str | None:
    prop = property_node(element, name)
    if prop is None:
        return None
    child = next(iter(prop), None)
    if child is None:
        return ""
    return child.text or ""


def has_direct_layout(widget: ET.Element) -> bool:
    return any(child.tag == "layout" for child in widget)


def is_layout_managed(element: ET.Element, parent_map: dict[ET.Element, ET.Element]) -> bool:
    current = element
    while current in parent_map:
        parent = parent_map[current]
        if parent.tag == "item" and parent in parent_map and parent_map[parent].tag == "layout":
            return True
        if parent.tag == "widget":
            return False
        current = parent
    return False


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"], []
    except OSError as exc:
        return [f"Cannot read file: {exc}"], []

    root = tree.getroot()
    if root.tag != "ui":
        errors.append("Root element must be <ui>.")
        return errors, warnings

    if root.get("version") != "4.0":
        warnings.append("Expected Designer UI version 4.0.")

    class_node = root.find("class")
    if class_node is None or not (class_node.text or "").strip():
        errors.append("Missing non-empty <class> element.")

    top = root.find("widget")
    if top is None:
        errors.append("Missing top-level <widget> element.")
        return errors, warnings

    top_class = top.get("class", "")
    top_name = top.get("name", "")
    if not top_class or not top_name:
        errors.append("Top-level widget must have class and name attributes.")

    parent_map = {child: parent for parent in root.iter() for child in parent}

    seen: dict[str, str] = {}
    for element in root.iter():
        if element.tag not in {"widget", "layout", "action", "spacer", "buttongroup"}:
            continue
        name = element.get("name")
        if not name:
            continue
        if name in seen:
            errors.append(f"Duplicate object name '{name}' ({seen[name]} and {element.tag}).")
        else:
            seen[name] = element.tag
        if GENERIC_NAME_RE.match(name):
            warnings.append(f"Generic Designer object name '{name}' should be renamed by purpose.")

    if top_class in {"QWidget", "QDialog", "QFrame", "QGroupBox", "QWizardPage"}:
        if not has_direct_layout(top):
            errors.append(f"Top-level {top_class} '{top_name}' has no top-level layout.")

    if top_class == "QMainWindow":
        central = None
        for child in top.findall("widget"):
            if child.get("name") == "centralwidget" or child.get("class") == "QWidget":
                central = child
                if child.get("name") == "centralwidget":
                    break
        if central is None:
            errors.append("QMainWindow has no central widget.")
        elif not has_direct_layout(central):
            errors.append("QMainWindow central widget has no top-level layout.")

    for widget in root.iter("widget"):
        if widget is top:
            continue
        name = widget.get("name", "<unnamed>")
        klass = widget.get("class", "QWidget")
        parent = parent_map.get(widget)

        direct_mainwindow_child = parent is top and top_class == "QMainWindow"
        if direct_mainwindow_child and (name in MAINWINDOW_MANAGED or klass in {"QMenuBar", "QStatusBar", "QToolBar", "QDockWidget"}):
            pass
        elif property_node(widget, "geometry") is not None and not is_layout_managed(widget, parent_map):
            warnings.append(f"Child widget '{name}' ({klass}) has geometry but is not layout-managed.")

        if klass in BUTTON_CLASSES:
            text = property_string(widget, "text")
            accessible = property_string(widget, "accessibleName")
            icon_prop = property_node(widget, "icon")
            if icon_prop is not None and (text is None or not text.strip()) and not (accessible or "").strip():
                warnings.append(f"Icon-only button '{name}' has no accessibleName.")

        if klass == "QLabel":
            text = property_string(widget, "text") or ""
            if "&" in text and property_node(widget, "buddy") is None:
                warnings.append(f"Label '{name}' has a mnemonic but no buddy property.")

    if root.find("resources") is None:
        warnings.append("Missing <resources> element; Designer files usually include it even when empty.")
    if root.find("connections") is None:
        warnings.append("Missing <connections> element; Designer files usually include it even when empty.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Qt Designer .ui files.")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    any_errors = False
    for path in args.files:
        errors, warnings = validate(path)
        print(f"{path}:")
        if errors:
            any_errors = True
            for message in errors:
                print(f"  ERROR: {message}")
        for message in warnings:
            print(f"  WARN:  {message}")
        if not errors and not warnings:
            print("  OK: structural checks passed")
        elif not errors:
            print(f"  OK: structural checks passed with {len(warnings)} warning(s)")

    return 1 if any_errors else 0


if __name__ == "__main__":
    sys.exit(main())
