(function initFractalUiLibrary() {
	const STORAGE_KEY = "fractal-mini-apps-theme";

	function getSystemPreferredTheme() {
		return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
			? "dark"
			: "light";
	}

	function getStoredTheme() {
		const value = localStorage.getItem(STORAGE_KEY);
		return value === "dark" || value === "light" ? value : null;
	}

	function applyTheme(theme) {
		const resolved = theme === "dark" ? "dark" : "light";
		document.documentElement.setAttribute("data-theme", resolved);
		if (document.body) {
			document.body.setAttribute("data-theme", resolved);
			document.body.classList.toggle("theme-dark", resolved === "dark");
			document.body.classList.toggle("theme-light", resolved === "light");
		}
		return resolved;
	}

	function setTheme(theme) {
		const resolved = applyTheme(theme);
		localStorage.setItem(STORAGE_KEY, resolved);
		return resolved;
	}

	function initializeTheme(defaultTheme) {
		const theme = getStoredTheme() || defaultTheme || getSystemPreferredTheme();
		return applyTheme(theme);
	}

	function getToggleLabel(theme) {
		return theme === "dark" ? "Use light mode" : "Use dark mode";
	}

	function syncToggleButton(button) {
		const current = document.documentElement.getAttribute("data-theme") || "light";
		const label = getToggleLabel(current);
		button.textContent = label.toUpperCase();
		button.setAttribute("aria-label", label);
		button.setAttribute("aria-pressed", current === "dark" ? "true" : "false");
		button.dataset.theme = current;
	}

	function wireThemeToggle(button) {
		if (!button) return;

		button.type = button.type || "button";
		syncToggleButton(button);

		button.addEventListener("click", () => {
			const current = document.documentElement.getAttribute("data-theme") || "light";
			const next = current === "dark" ? "light" : "dark";
			setTheme(next);
			syncToggleButton(button);
		});
	}

	function initLandingThemeToggle(options) {
		const settings = options || {};
		const theme = initializeTheme(settings.defaultTheme);

		const selector = settings.buttonSelector || "[data-theme-toggle]";
		const button = document.querySelector(selector);
		if (button) {
			button.dataset.theme = theme;
			wireThemeToggle(button);
		}
	}

	function autoInitLandingThemeToggle() {
		const run = () => {
			if (document.querySelector("[data-theme-toggle]")) {
				initLandingThemeToggle();
			}
		};

		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", run, { once: true });
		} else {
			run();
		}
	}

	autoInitLandingThemeToggle();

	window.FractalUI = {
		initializeTheme,
		setTheme,
		applyTheme,
		initLandingThemeToggle
	};

	window.initLandingThemeToggle = initLandingThemeToggle;
})();
