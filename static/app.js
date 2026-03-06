/**
 * AI 资讯聚合工具 - 前端逻辑
 */

// ===================== 状态 =====================
const state = {
    currentPage: 1,
    perPage: 20,
    category: '全部',
    language: 'all',
    search: '',
    totalPages: 1,
};

// ===================== 工具函数 =====================

/** 格式化时间为相对时间 */
function timeAgo(dateStr) {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr.replace(' ', 'T'));
        const now = new Date();
        const diffMs = now - date;
        const diffMin = Math.floor(diffMs / 60000);
        const diffHour = Math.floor(diffMs / 3600000);
        const diffDay = Math.floor(diffMs / 86400000);

        if (diffMin < 1) return '刚刚';
        if (diffMin < 60) return `${diffMin} 分钟前`;
        if (diffHour < 24) return `${diffHour} 小时前`;
        if (diffDay < 7) return `${diffDay} 天前`;
        return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    } catch {
        return dateStr?.slice(0, 10) || '';
    }
}

/** 防抖 */
function debounce(fn, delay = 400) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

/** 显示 Toast */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(40px)';
        toast.style.transition = 'all 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===================== API 调用 =====================

async function fetchArticles() {
    const params = new URLSearchParams({
        page: state.currentPage,
        per_page: state.perPage,
    });
    if (state.category && state.category !== '全部') params.set('category', state.category);
    if (state.language && state.language !== 'all') params.set('language', state.language);
    if (state.search) params.set('search', state.search);

    const resp = await fetch(`/api/articles?${params}`);
    return await resp.json();
}

async function fetchStats() {
    const resp = await fetch('/api/stats');
    return await resp.json();
}

async function markRead(articleId) {
    await fetch(`/api/articles/${articleId}/read`, { method: 'POST' });
}

async function manualFetch() {
    const btn = document.getElementById('btnRefresh');
    btn.classList.add('spinning');
    btn.disabled = true;

    try {
        const resp = await fetch('/api/fetch', { method: 'POST' });
        const data = await resp.json();
        showToast(data.message || '抓取任务已启动', 'success');
    } catch (e) {
        showToast('刷新失败，请重试', 'error');
    }

    // 15秒后停止动画，并刷新数据
    setTimeout(async () => {
        btn.classList.remove('spinning');
        btn.disabled = false;
        await loadData();
    }, 15000);
}

// ===================== 渲染 =====================

function renderArticles(articles) {
    const grid = document.getElementById('articlesGrid');
    const loading = document.getElementById('loadingState');
    const empty = document.getElementById('emptyState');

    loading.style.display = 'none';

    if (!articles || articles.length === 0) {
        grid.innerHTML = '';
        empty.style.display = 'flex';
        return;
    }

    empty.style.display = 'none';

    grid.innerHTML = articles
        .map(
            (a) => `
        <article class="article-card ${a.is_read ? 'is-read' : ''}" 
                 data-id="${a.id}" 
                 onclick="openArticle(${a.id}, '${encodeURIComponent(a.url)}')">
            <div class="card-header">
                <div class="card-meta">
                    <span class="source-tag">${escapeHtml(a.source)}</span>
                    <span class="lang-tag ${a.language}">${a.language === 'zh' ? '中文' : 'EN'}</span>
                    ${a.category && a.category !== '综合' ? `<span class="category-tag">${escapeHtml(a.category)}</span>` : ''}
                    <span class="time-label">${timeAgo(a.published_at || a.fetched_at)}</span>
                </div>
            </div>
            <h3 class="card-title">${escapeHtml(a.title)}</h3>
            ${
                a.summary && a.summary !== '（摘要生成失败）'
                    ? `<div class="card-summary"><span class="ai-badge">AI</span>${escapeHtml(a.summary)}</div>`
                    : ''
            }
            ${
                a.content_snippet && !a.summary
                    ? `<p class="card-snippet">${escapeHtml(a.content_snippet.slice(0, 150))}</p>`
                    : ''
            }
        </article>
    `
        )
        .join('');

    // 入场动画
    grid.querySelectorAll('.article-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, i * 40);
    });
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function renderPagination(data) {
    const { page, total_pages } = data;
    state.totalPages = total_pages;
    const container = document.getElementById('pagination');

    if (total_pages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // 上一页
    html += `<button class="page-btn" onclick="goPage(${page - 1})" ${page <= 1 ? 'disabled' : ''}>‹</button>`;

    // 页码
    const pages = generatePageNumbers(page, total_pages);
    for (const p of pages) {
        if (p === '...') {
            html += `<span class="page-ellipsis">…</span>`;
        } else {
            html += `<button class="page-btn ${p === page ? 'active' : ''}" onclick="goPage(${p})">${p}</button>`;
        }
    }

    // 下一页
    html += `<button class="page-btn" onclick="goPage(${page + 1})" ${page >= total_pages ? 'disabled' : ''}>›</button>`;

    container.innerHTML = html;
}

function generatePageNumbers(current, total) {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages = [];
    pages.push(1);
    if (current > 3) pages.push('...');
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
        pages.push(i);
    }
    if (current < total - 2) pages.push('...');
    pages.push(total);
    return pages;
}

function renderStats(stats) {
    document.getElementById('statTotal').textContent = stats.total || 0;
    document.getElementById('statToday').textContent = stats.today || 0;
    document.getElementById('statUnread').textContent = stats.unread || 0;
    document.getElementById('statSources').textContent = Object.keys(stats.sources || {}).length;

    // 更新分类计数
    const cats = stats.categories || {};
    document.getElementById('countAll').textContent = stats.total || 0;
    document.getElementById('countLLM').textContent = cats['大模型'] || 0;
    document.getElementById('countApp').textContent = cats['AI应用'] || 0;
    document.getElementById('countPaper').textContent = cats['论文'] || 0;
    document.getElementById('countIndustry').textContent = cats['行业动态'] || 0;
    document.getElementById('countOpenSource').textContent = cats['开源'] || 0;
    document.getElementById('countGeneral').textContent = cats['综合'] || 0;
}

function updateSectionTitle() {
    const title = document.getElementById('sectionTitle');
    const langLabel = state.language === 'zh' ? '中文' : state.language === 'en' ? '英文' : '';
    if (state.search) {
        title.textContent = `搜索: ${state.search}`;
    } else {
        title.textContent = `${langLabel} ${state.category === '全部' ? '全部资讯' : state.category}`.trim();
    }
}

// ===================== 交互 =====================

function openArticle(id, encodedUrl) {
    markRead(id);
    // 更新 UI
    const card = document.querySelector(`.article-card[data-id="${id}"]`);
    if (card) card.classList.add('is-read');
    // 打开链接
    window.open(decodeURIComponent(encodedUrl), '_blank');
}

async function goPage(page) {
    if (page < 1 || page > state.totalPages) return;
    state.currentPage = page;
    await loadArticles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadArticles() {
    const loading = document.getElementById('loadingState');
    const grid = document.getElementById('articlesGrid');
    loading.style.display = 'flex';
    grid.innerHTML = '';

    try {
        const data = await fetchArticles();
        renderArticles(data.articles);
        renderPagination(data);
        document.getElementById('articlesCount').textContent =
            data.total > 0 ? `共 ${data.total} 篇` : '';
    } catch (e) {
        loading.style.display = 'none';
        showToast('加载文章失败', 'error');
    }
}

async function loadData() {
    await Promise.all([loadArticles(), fetchStats().then(renderStats)]);
}

// ===================== 事件绑定 =====================

document.addEventListener('DOMContentLoaded', () => {
    // 初始加载
    loadData();

    // 分类切换
    document.getElementById('categoryNav').addEventListener('click', (e) => {
        const btn = e.target.closest('.category-btn');
        if (!btn) return;
        document.querySelectorAll('.category-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.category = btn.dataset.category;
        state.currentPage = 1;
        updateSectionTitle();
        loadArticles();
    });

    // 语言切换
    document.getElementById('langFilter').addEventListener('click', (e) => {
        const btn = e.target.closest('.lang-btn');
        if (!btn) return;
        document.querySelectorAll('.lang-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.language = btn.dataset.lang;
        state.currentPage = 1;
        updateSectionTitle();
        loadArticles();
    });

    // 搜索
    const searchInput = document.getElementById('searchInput');
    const debouncedSearch = debounce((val) => {
        state.search = val.trim();
        state.currentPage = 1;
        updateSectionTitle();
        loadArticles();
    }, 500);
    searchInput.addEventListener('input', (e) => debouncedSearch(e.target.value));
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            state.search = e.target.value.trim();
            state.currentPage = 1;
            updateSectionTitle();
            loadArticles();
        }
    });

    // 刷新按钮
    document.getElementById('btnRefresh').addEventListener('click', manualFetch);

    // 定时刷新统计
    setInterval(async () => {
        try {
            const stats = await fetchStats();
            renderStats(stats);
        } catch {}
    }, 60000);
});
