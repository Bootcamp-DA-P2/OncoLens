#!/usr/bin/env python3
"""
oncocheck.py — smoke-test para el proyecto OncoLens.

Qué hace:
    Recorre una carpeta, encuentra todos los .ipynb y .py, y los EJECUTA de
    principio a fin. Si todas las celdas/el script corren sin excepción, el
    archivo pasa (OK!). Si algo falla, se reporta el archivo, la celda o línea
    y el error exacto.

Qué NO hace:
    No comprueba estilo (PEP8, nombres de variables, longitud de línea, etc.)
    ni la calidad de los resultados (accuracy, F1...). Solo si el código
    revienta o no.

Uso:
    python oncocheck.py                     # revisa el directorio actual
    python oncocheck.py ruta/al/proyecto     # revisa esa carpeta
    python oncocheck.py --quick              # solo valida sintaxis (rápido, no ejecuta)
    python oncocheck.py --timeout 1200        # timeout por archivo, en segundos (def: 600)
    python oncocheck.py --jobs 8              # cuántos archivos en paralelo (def: 4)
    python oncocheck.py --changed-only        # solo lo que cambió sin commitear (día a día)
    python oncocheck.py --changed-only=main   # solo lo que cambió vs la rama main

Config opcional (oncocheck.config.json en la raíz del proyecto):
    {
      "exclude": ["notebooks/01-exploring_eda.ipynb"],
      "timeouts": {"notebooks/02_feature_selection_&_modeling.ipynb": 1800}
    }

Requisitos:
    pip install nbclient nbformat
    (nbclient ejecuta notebooks sin necesidad de abrir Jupyter)

Recomendación de uso:
    - Día a día, mientras cada quien trabaja en su rama: --changed-only y --quick.
    - Antes de fusionar a main / antes de la entrega: chequeo completo, sin flags.

Código de salida:
    0 si todo pasó, 1 si algún archivo falló (útil para usarlo en CI).
"""

import os
import sys
import json
import time
import argparse
import subprocess
import py_compile
import concurrent.futures as cf
from pathlib import Path

EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".ipynb_checkpoints",
                "node_modules", "outputs_modelado_ml", "models"}

CONFIG_FILENAME = "oncocheck.config.json"


def load_config(root: Path):
    """
    Config opcional en la raíz del proyecto (oncocheck.config.json), por si
    cada quien quiere ajustar el chequeo sin tocar el script. Ejemplo:

    {
      "exclude": ["notebooks/01-exploring_eda.ipynb"],
      "timeouts": {"notebooks/02_feature_selection_&_modeling.ipynb": 1800}
    }

    Si no existe el archivo, se usan los valores por defecto y ya.
    """
    path = root / CONFIG_FILENAME
    if not path.exists():
        return {"exclude": [], "timeouts": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Aviso: no se pudo leer {CONFIG_FILENAME} ({e}), se ignora.")
        return {"exclude": [], "timeouts": {}}
    data.setdefault("exclude", [])
    data.setdefault("timeouts", {})
    return data


def get_changed_files(root: Path, against: str):
    """
    Devuelve el set de archivos (rutas relativas, con /) que cambiaron según
    git: diferencias contra `against` (rama o commit) + cambios sin commitear
    + archivos nuevos sin trackear. Si algo falla (no es un repo git, git no
    instalado, etc.), devuelve None para que el caller haga un chequeo normal.
    """
    def run(args):
        r = subprocess.run(["git", *args], cwd=str(root),
                            capture_output=True, text=True)
        return r.stdout.splitlines() if r.returncode == 0 else []

    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                        cwd=str(root), capture_output=True, text=True, check=True)
    except Exception:
        return None

    changed = set(run(["diff", "--name-only", against]))
    changed |= set(run(["diff", "--name-only", "--cached"]))
    changed |= set(run(["ls-files", "--others", "--exclude-standard"]))
    return changed


def find_targets(root: Path, config: dict, changed_only_against: str = None):
    notebooks, scripts = [], []
    self_path = Path(__file__).resolve()
    exclude_patterns = set(config.get("exclude", []))

    changed = None
    if changed_only_against:
        changed = get_changed_files(root, changed_only_against)
        if changed is None:
            print("Aviso: no parece un repo git (o git no está disponible); "
                  "se hace un chequeo completo en vez de --changed-only.\n")

    for p in sorted(root.rglob("*")):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.resolve() == self_path:
            continue  # no revisarse a sí mismo
        rel_str = str(p.relative_to(root)).replace(os.sep, "/")
        if rel_str in exclude_patterns:
            continue
        if changed is not None and rel_str not in changed:
            continue
        if p.suffix == ".ipynb":
            notebooks.append(p)
        elif p.suffix == ".py":
            scripts.append(p)
    return notebooks, scripts


def check_notebook_syntax(path: Path):
    """Validación rápida: el .ipynb es JSON válido y cada celda de código compila."""
    import nbformat
    try:
        nb = nbformat.read(path, as_version=4)
    except Exception as e:
        return False, f"Notebook ilegible / JSON corrupto: {e}"
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        try:
            compile(cell.source, f"<celda {i}>", "exec")
        except SyntaxError as e:
            return False, f"SyntaxError en celda {i}, línea {e.lineno}: {e.msg}"
    return True, ""


def run_notebook(path: Path, timeout: int):
    """Ejecuta el notebook completo con nbclient y reporta la primera celda que falle."""
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    try:
        nb = nbformat.read(path, as_version=4)
    except Exception as e:
        return False, f"Notebook ilegible / JSON corrupto: {e}"

    client = NotebookClient(nb, timeout=timeout, kernel_name="python3",
                             resources={"metadata": {"path": str(path.parent)}})
    try:
        client.execute()
        return True, ""
    except CellExecutionError as e:
        # nbclient ya indica el índice de celda en el mensaje
        msg = str(e).splitlines()[0] if str(e) else "error de ejecución"
        return False, msg
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_script_syntax(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except py_compile.PyCompileError as e:
        return False, str(e.exc_value)


MODULE_ERROR_MARKERS = ("ModuleNotFoundError", "attempted relative import")


def module_name_for(path: Path, root: Path):
    """Convierte una ruta tipo streamlit_app/pages/dashboard.py en 'streamlit_app.pages.dashboard'."""
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def try_import_as_module(path: Path, root: Path, timeout: int):
    """
    Para archivos que son parte de un paquete (no scripts independientes):
    en vez de ejecutarlos como __main__, los importa desde la raíz del
    proyecto, tal como los importaría el resto de la app. Así valida el
    código sin los falsos ModuleNotFoundError que da ejecutarlos sueltos.
    """
    mod = module_name_for(path, root)
    code = f"import importlib; importlib.import_module({mod!r})"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(root),
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace", env=env,
        )
    except subprocess.TimeoutExpired:
        return False, f"Timeout tras {timeout}s (import como módulo)"
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        last_line = (err.splitlines() or ["(sin salida)"])[-1]
        return False, last_line
    return True, ""


def run_script(path: Path, root: Path, timeout: int):
    """
    Intenta correr el archivo como script independiente (cwd = su propia
    carpeta, como si alguien hiciera `python archivo.py` parado ahí).
    Si falla por un problema de resolución de paquete (ModuleNotFoundError,
    import relativo), reintenta importándolo como módulo del proyecto —
    muchos archivos (managers/, streamlit_app/pages/, etc.) están hechos
    para ser importados, no para correr solos, y no deben reportarse como
    rotos solo por eso.
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(path.parent),
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace", env=env,
        )
    except subprocess.TimeoutExpired:
        return False, f"Timeout tras {timeout}s"

    if result.returncode == 0:
        return True, ""

    stderr = result.stderr.strip()
    stdout_tail = result.stdout.strip()
    looks_like_module = any(marker in stderr for marker in MODULE_ERROR_MARKERS)

    if looks_like_module:
        ok, msg = try_import_as_module(path, root, timeout)
        if ok:
            return True, "(es un módulo del paquete, no un script — validado por import)"
        # ni como script ni como módulo funciona: reportar el más informativo
        script_err = (stderr.splitlines() or ["(sin stderr)"])[-1]
        return False, f"{script_err}  ·  tampoco importable: {msg}"

    if not stderr and stdout_tail:
        # Algunos scripts imprimen el error real en stdout, no en stderr
        return False, stdout_tail.splitlines()[-1]

    last_line = (stderr.splitlines() or ["(sin stderr — revisar manualmente)"])[-1]
    return False, last_line


def check_one(kind, path, root, quick, timeout):
    """Une los 4 tipos de chequeo (notebook/script × quick/completo) en una
    sola función para poder mandarlas al pool de hilos de forma uniforme."""
    t0 = time.time()
    if kind == "notebook":
        ok, msg = check_notebook_syntax(path) if quick else run_notebook(path, timeout)
    else:
        ok, msg = check_script_syntax(path) if quick else run_script(path, root, timeout)
    return path, kind, ok, msg, time.time() - t0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", default=".", help="Carpeta del proyecto")
    parser.add_argument("--quick", action="store_true",
                         help="Solo valida sintaxis, no ejecuta el código")
    parser.add_argument("--timeout", type=int, default=600,
                         help="Timeout por archivo en segundos (default: 600)")
    parser.add_argument("--jobs", "-j", type=int, default=4,
                         help="Cuántos archivos revisar en paralelo (default: 4)")
    parser.add_argument("--changed-only", metavar="REF", nargs="?", const="HEAD",
                         help="Solo revisa archivos que cambiaron vs REF (default: HEAD, "
                              "o usa --changed-only=main para comparar contra esa rama). "
                              "Útil en el día a día; antes de entregar, correr sin este flag.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    config = load_config(root)
    notebooks, scripts = find_targets(root, config, args.changed_only)
    total = len(notebooks) + len(scripts)

    if total == 0:
        msg = "No se encontraron .ipynb ni .py"
        if args.changed_only:
            msg += " que hayan cambiado (o ya está todo al día)"
        print(f"{msg} en {root}")
        sys.exit(0)

    mode = "sintaxis (--quick)" if args.quick else "ejecución completa"
    scope = f" [solo cambios vs {args.changed_only}]" if args.changed_only else ""
    print(f"oncocheck — {total} archivo(s) encontrados en {root}  "
          f"[modo: {mode}]{scope}  [paralelo: {args.jobs}]\n")

    jobs = [("notebook", p) for p in notebooks] + [("script", p) for p in scripts]
    results = {}

    with cf.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = []
        for kind, path in jobs:
            rel_str = str(path.relative_to(root)).replace(os.sep, "/")
            file_timeout = config.get("timeouts", {}).get(rel_str, args.timeout)
            futures.append(pool.submit(check_one, kind, path, root, args.quick, file_timeout))
        for fut in cf.as_completed(futures):
            path, kind, ok, msg, dt = fut.result()
            results[path] = (ok, msg, dt)

    failures = []
    # Se imprime en el mismo orden siempre (alfabético), aunque hayan
    # terminado en paralelo en cualquier orden — así el reporte es estable
    # y comparable entre corridas.
    for path in notebooks + scripts:
        rel = path.relative_to(root)
        ok, msg, dt = results[path]
        status = "OK!" if ok else "KO"
        print(f"[{status}] {rel}  ({dt:.1f}s)")
        if ok and msg:
            print(f"       Nota: {msg}")
        if not ok:
            print(f"       Error: {msg}")
            failures.append(str(rel))

    print()
    if failures:
        print(f"RESULTADO: {len(failures)}/{total} archivo(s) con errores:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"RESULTADO: {total}/{total} archivos OK. Todo corre sin errores.")
        sys.exit(0)


if __name__ == "__main__":
    main()
