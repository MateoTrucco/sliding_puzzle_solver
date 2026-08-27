const PYODIDE_VERSION = "314.0.4";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

export async function bootPython(files = [], beforeImport = "") {
  const status = document.querySelector('[data-runtime-status]');
  const setStatus = (message, state = '') => {
    if (!status) return;
    status.textContent = message;
    status.dataset.state = state;
  };
  setStatus(`Loading Python in the browser (Pyodide ${PYODIDE_VERSION})…`);
  try {
    if (typeof loadPyodide !== 'function') throw new Error('Pyodide loader is unavailable.');
    const pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });
    for (const file of files) {
      const response = await fetch(file, { cache: 'no-cache' });
      if (!response.ok) throw new Error(`Could not load ${file} (${response.status}).`);
      const text = await response.text();
      const slash = file.lastIndexOf('/');
      if (slash > 0) pyodide.FS.mkdirTree(file.slice(0, slash));
      pyodide.FS.writeFile(file, text);
    }
    pyodide.runPython("import sys; sys.path.insert(0, '.')");
    if (beforeImport) pyodide.runPython(beforeImport);
    setStatus('Python runtime ready — this demo is executing repository logic.', 'ready');
    return pyodide;
  } catch (error) {
    console.error(error);
    setStatus(`Runtime error: ${error.message}`, 'error');
    throw error;
  }
}

export function parsePythonJson(value) {
  return JSON.parse(String(value));
}
