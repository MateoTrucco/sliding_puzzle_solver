const projectThemes = {
  argentine_slang_normalizer: ['#8b5cf6', '139, 92, 246', 'AS'],
  braille_visualizer: ['#0ea5e9', '14, 165, 233', 'BR'],
  chance_score_game: ['#f97316', '249, 115, 22', 'CS'],
  django_job_board: ['#22c55e', '34, 197, 94', 'DJ'],
  math_toolkit: ['#6366f1', '99, 102, 241', 'M+'],
  memory_monitor: ['#06b6d4', '6, 182, 212', 'MM'],
  process_inspector: ['#14b8a6', '20, 184, 166', 'PI'],
  python_app_packager: ['#eab308', '234, 179, 8', 'PX'],
  python_practice_collection: ['#a855f7', '168, 85, 247', 'PY'],
  shortcut_auditor: ['#f43f5e', '244, 63, 94', 'SA'],
  sliding_puzzle_solver: ['#3b82f6', '59, 130, 246', 'A*'],
  startup_inspector: ['#fb7185', '251, 113, 133', 'SI'],
  trading_card_estimator: ['#10b981', '16, 185, 129', 'EV'],
};

const slug = location.pathname.split('/').filter(Boolean)[0] || document.title.toLowerCase().replace(/\W+/g, '_');
const [accent, accentRgb, mark] = projectThemes[slug] || projectThemes.argentine_slang_normalizer;
document.documentElement.style.setProperty('--accent', accent);
document.documentElement.style.setProperty('--accent-rgb', accentRgb);

const storedTheme = localStorage.getItem('mt-demo-theme');
const preferredTheme = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
document.documentElement.dataset.theme = storedTheme || preferredTheme;

const brand = document.querySelector('.brand');
if (brand) brand.innerHTML = `<span class="brand-mark" aria-hidden="true">${mark}</span><span>Mateo Trucco · Project Lab</span>`;

const links = document.querySelector('.links');
if (links) {
  const themeButton = document.createElement('button');
  themeButton.type = 'button';
  themeButton.className = 'theme-toggle';
  themeButton.setAttribute('aria-label', 'Switch color theme');
  const syncThemeButton = () => {
    const light = document.documentElement.dataset.theme === 'light';
    themeButton.textContent = light ? '◒' : '◐';
    themeButton.title = light ? 'Use dark theme' : 'Use light theme';
    themeButton.setAttribute('aria-pressed', String(light));
  };
  themeButton.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('mt-demo-theme', next);
    syncThemeButton();
  });
  syncThemeButton();
  links.append(themeButton);
}

for (const output of document.querySelectorAll('.output')) {
  const toolbar = document.createElement('div');
  toolbar.className = 'output-toolbar';
  toolbar.innerHTML = '<span>Result</span>';
  const copy = document.createElement('button');
  copy.type = 'button';
  copy.textContent = 'Copy';
  copy.addEventListener('click', async () => {
    const text = output.innerText.trim();
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      copy.textContent = 'Copied';
    } catch {
      copy.textContent = 'Select to copy';
    }
    setTimeout(() => { copy.textContent = 'Copy'; }, 1400);
  });
  toolbar.append(copy);
  output.before(toolbar);
}

document.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    const primary = document.querySelector('button.primary:not(:disabled)');
    if (primary) {
      event.preventDefault();
      primary.click();
    }
  }
});

const footer = document.querySelector('.footer');
if (footer) {
  const original = footer.innerHTML;
  footer.innerHTML = `<span>${original}</span><span>Built for the web · ${new Date().getFullYear()}</span>`;
}

requestAnimationFrame(() => document.body.classList.add('is-ready'));
