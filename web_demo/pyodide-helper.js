const PYODIDE_VERSION = "314.0.4";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

export async function bootPython(files = [], beforeImport = "") {
  const status = document.querySelector('[data-runtime-status]');
  let statusKey = 'loading';
  const messages = {
    loading: { en: `Loading Python in the browser (Pyodide ${PYODIDE_VERSION})…`, es: `Cargando Python en el navegador (Pyodide ${PYODIDE_VERSION})…` },
    ready: { en: 'Python runtime ready — this demo is executing repository logic.', es: 'Python está listo: esta demo ejecuta la lógica real del repositorio.' },
  };
  const currentLanguage = () => localStorage.getItem('mateo-ui-language') || (navigator.language.toLowerCase().startsWith('es') ? 'es' : 'en');
  const setStatus = (message, state = '', key = '') => {
    if (!status) return;
    if (key) statusKey = key;
    status.textContent = messages[statusKey]?.[currentLanguage()] || message;
    status.dataset.state = state;
  };
  document.addEventListener('mt:language', () => setStatus(status.textContent, status.dataset.state));
  setStatus(messages.loading.en, '', 'loading');
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
    setStatus(messages.ready.en, 'ready', 'ready');
    return pyodide;
  } catch (error) {
    console.error(error);
    statusKey = '';
    setStatus(`${currentLanguage() === 'es' ? 'Error de ejecución' : 'Runtime error'}: ${error.message}`, 'error');
    throw error;
  }
}

export function parsePythonJson(value) {
  return JSON.parse(String(value));
}
