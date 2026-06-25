// ===== Toast notification component =====
function toast() {
    return {
        visible: false,
        message: '',
        type: 'success',
        timer: null,

        show(msg, t = 'success') {
            this.message = msg;
            this.type = t;
            this.visible = true;
            clearTimeout(this.timer);
            this.timer = setTimeout(() => this.hide(), 4000);
        },

        hide() {
            this.visible = false;
            clearTimeout(this.timer);
        },
    };
}

// ===== Generator page component =====
function generatorApp() {
    return {
        // Form state
        prompt: '',
        size: '2K',
        imageCount: 1,
        seed: -1,
        templateId: null,
        collectionId: null,

        // UI state
        isGenerating: false,
        results: [],
        error: null,
        charCount: 0,

        // Sidebar
        sidebarOpen: true,
        activeCategory: 'all',
        searchQuery: '',

        init() {
            this.updateCharCount();
            this.$watch('prompt', () => this.updateCharCount());
        },

        updateCharCount() {
            this.charCount = this.prompt.length;
        },

        useTemplate(template) {
            this.prompt = template.prompt_text;
            this.templateId = template.id;
            this.$refs.promptTextarea.focus();
        },

        clearForm() {
            this.prompt = '';
            this.templateId = null;
            this.error = null;
        },

        filterByCategory(cat) {
            this.activeCategory = cat;
        },

        get filteredTemplates() {
            const templates = JSON.parse(
                document.getElementById('templates-data')?.textContent || '[]'
            );
            let filtered = templates;
            if (this.activeCategory !== 'all') {
                filtered = filtered.filter(t => t.category === this.activeCategory);
            }
            if (this.searchQuery) {
                const q = this.searchQuery.toLowerCase();
                filtered = filtered.filter(
                    t => t.name.toLowerCase().includes(q) ||
                         t.description.toLowerCase().includes(q) ||
                         (t.tags || '').toLowerCase().includes(q)
                );
            }
            return filtered;
        },

        async generate() {
            if (!this.prompt.trim()) return;
            if (this.isGenerating) return;

            this.isGenerating = true;
            this.error = null;
            this.results = [];

            try {
                const resp = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: this.prompt,
                        size: this.size,
                        n: this.imageCount,
                        seed: this.seed,
                        template_id: this.templateId || null,
                        collection_id: this.collectionId || null,
                    }),
                });

                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.detail || 'Generation failed');
                }

                const data = await resp.json();
                this.results = data.images || [];
                if (data.images && data.images.length > 0) {
                    window.__dispatchToast('Images generated successfully!', 'success');
                }
            } catch (e) {
                this.error = e.message;
                window.__dispatchToast(e.message, 'error');
            } finally {
                this.isGenerating = false;
            }
        },

        setSize(s) {
            this.size = s;
        },

        get sizeLabel() {
            const labels = {
                '1K': '1K Standard',
                '2K': '2K HD',
                '4K': '4K Ultra HD',
                '1024x1024': '1:1 Square',
                '1664x936': '16:9 Landscape',
                '936x1664': '9:16 Portrait',
            };
            return labels[this.size] || this.size;
        },
    };
}

// ===== Lightbox component =====
function lightbox() {
    return {
        open: false,
        imageSrc: '',
        prompt: '',
        metadata: {},

        init() {
            // Register globally so any element can trigger the lightbox
            window.__lightbox = this;
        },

        show(src, promptText, meta = {}) {
            this.imageSrc = src;
            this.prompt = promptText;
            this.metadata = meta;
            this.open = true;
            document.body.style.overflow = 'hidden';
        },

        close() {
            this.open = false;
            document.body.style.overflow = '';
        },

        closeOnBackdrop(e) {
            if (e.target === e.currentTarget) this.close();
        },
    };
}

// Global lightbox helper — call from any onclick handler
window.showLightbox = function (src, promptText, size) {
    if (window.__lightbox) {
        window.__lightbox.show(src, promptText, { size: size || '' });
    }
};

// ===== Template Library component =====
function templateLibrary() {
    return {
        activeCategory: 'all',
        categories: ['megastructure', 'contrast', 'post_human', 'interior', 'landscape'],

        filter(cat) {
            this.activeCategory = cat;
            document.querySelectorAll('.template-card').forEach(el => {
                if (cat === 'all' || el.dataset.category === cat) {
                    el.style.display = '';
                } else {
                    el.style.display = 'none';
                }
            });
        },

        catLabel(cat) {
            const labels = {
                'all': 'All',
                'megastructure': 'Megastructures',
                'contrast': 'Contrast / Scale',
                'post_human': 'Post-Human',
                'interior': 'Interiors',
                'landscape': 'Landscapes',
            };
            return labels[cat] || cat;
        },
    };
}

// ===== Global collection creation =====
window.createCollection = async function (name, description) {
    if (!name.trim()) return false;
    try {
        const r = await fetch('/api/collections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name.trim(), description: description.trim() || null }),
        });
        if (r.ok) {
            window.__dispatchToast('Collection created!', 'success');
            return true;
        }
        const err = await r.json();
        window.__dispatchToast(err.detail || 'Failed to create collection', 'error');
    } catch (e) {
        window.__dispatchToast('Network error', 'error');
    }
    return false;
};

// ===== Global toast dispatch =====
window.__dispatchToast = function (message, type) {
    const el = document.querySelector('[x-data="toast()"]');
    if (el && el.__x) {
        el.__x.$data.show(message, type);
    }
};

// ===== HTMX Configuration =====
document.addEventListener('htmx:configRequest', (evt) => {
    // Add any global HTMX config here
});

document.addEventListener('htmx:responseError', (evt) => {
    const detail = evt.detail;
    try {
        const body = JSON.parse(detail.xhr.responseText);
        window.__dispatchToast(body.detail || 'An error occurred', 'error');
    } catch {
        window.__dispatchToast('An unexpected error occurred', 'error');
    }
});

// ===== Keyboard shortcut: Ctrl+Enter to generate =====
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const genBtn = document.querySelector('[data-generate-btn]');
        if (genBtn && !genBtn.disabled) {
            genBtn.click();
        }
    }
});
