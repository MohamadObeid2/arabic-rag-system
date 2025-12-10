let currentSection = 'chat';
let chatMessages = [];

function showSection(section) {
    document.querySelectorAll('.section').forEach(div => {
        div.classList.remove('active');
    });
    
    document.querySelectorAll('nav button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(section + '-section').classList.add('active');
    document.querySelector(`nav button[onclick="showSection('${section}')"]`).classList.add('active');
    currentSection = section;
}

function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' });
}

function addMessage(role, content, sources = []) {
    const chatBox = document.getElementById('chat-box');
    
    if (chatMessages.length === 0) {
        chatBox.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    bubble.appendChild(contentDiv);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = formatTime();
    bubble.appendChild(timeDiv);
    
    messageDiv.appendChild(bubble);
    
    if (sources.length > 0) {
        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'sources-container';
        
        const title = document.createElement('div');
        title.className = 'sources-title';
        title.innerHTML = '📚 المصادر المستخدمة';
        sourcesContainer.appendChild(title);
        
        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            
            const fileInfo = document.createElement('div');
            fileInfo.className = 'source-file';
            fileInfo.innerHTML = `📄 ${source.file || (source.metadata?.source && source.metadata.source.split('/').slice(-1)[0])}`;
            sourceItem.appendChild(fileInfo);
            
            const content = document.createElement('div');
            content.className = 'source-content';
            content.textContent = source.content;
            sourceItem.appendChild(content);
            
            const score = document.createElement('div');
            score.className = 'source-score';
            score.textContent = `التشابه: ${source.score.toFixed(3)}`;
            sourceItem.appendChild(score);
            
            sourcesContainer.appendChild(sourceItem);
        });
        
        messageDiv.appendChild(sourcesContainer);
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    chatMessages.push({ role, content, sources });
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const button = document.getElementById('send-button');
    const message = input.value.trim();
    
    if (!message) {
        alert('يرجى كتابة سؤال');
        return;
    }
    
    input.disabled = true;
    button.disabled = true;
    button.innerHTML = '<span>جاري المعالجة...</span><div class="loading"></div>';
    
    addMessage('user', message);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        });
        
        const data = await response.json();
        addMessage('system', data.answer, data.sources);
        
    } catch (error) {
        addMessage('system', '❌ حدث خطأ في الاتصال بالخادم. يرجى المحاولة مرة أخرى.');
    }
    
    input.value = '';
    input.disabled = false;
    button.disabled = false;
    button.innerHTML = '<span>إرسال</span><span>↩️</span>';
    input.focus();
}

async function performSearch() {
    const query = document.getElementById('search-query').value.trim();
    
    if (!query) {
        alert('يرجى كتابة كلمة للبحث');
        return;
    }
    
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<div class="empty-state"><div class="loading"></div><h3>جاري البحث...</h3></div>';
    
    try {
        const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        resultsDiv.innerHTML = '';
        
        if (data.success && data.sources.length > 0) {
            const count = document.createElement('div');
            count.className = 'results-count';
            count.textContent = `تم العثور على ${data.sources.length} نتائج`;
            resultsDiv.appendChild(count);
            
            data.sources.forEach((result, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const header = document.createElement('div');
                header.className = 'result-header';
                
                const id = document.createElement('div');
                id.className = 'result-id';
                id.textContent = `نتيجة ${index + 1}`;
                
                const score = document.createElement('div');
                score.className = 'result-score';
                score.textContent = `التشابه: ${result.score.toFixed(3)}`;
                
                header.appendChild(id);
                header.appendChild(score);
                resultItem.appendChild(header);
                
                if (result.content) {
                    const contentDiv = document.createElement('div');
                    contentDiv.style.marginTop = 'var(--spacing-md)';
                    contentDiv.style.fontSize = '14px';
                    contentDiv.style.color = 'var(--color-text-secondary)';
                    contentDiv.style.lineHeight = '1.5';
                    contentDiv.style.textAlign = 'right';
                    contentDiv.textContent = result.content;
                    resultItem.appendChild(contentDiv);
                }
                
                if (result.file) {
                    const fileDiv = document.createElement('div');
                    fileDiv.style.marginTop = 'var(--spacing-sm)';
                    fileDiv.style.fontSize = '12px';
                    fileDiv.style.color = 'var(--color-primary)';
                    fileDiv.style.display = 'flex';
                    //fileDiv.style.alignItems = 'center';
                    fileDiv.style.gap = '4px';
                    fileDiv.innerHTML = `📄 ${result.file}`;
                    resultItem.appendChild(fileDiv);
                }
                
                resultsDiv.appendChild(resultItem);
            });
        } else {
            resultsDiv.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔍</div><h3>لم يتم العثور على نتائج</h3><p>حاول استخدام كلمات بحث مختلفة</p></div>';
        }
        
    } catch (error) {
        resultsDiv.innerHTML = '<div class="empty-state"><div class="empty-state-icon">❌</div><h3>حدث خطأ في الاتصال</h3><p>يرجى المحاولة مرة أخرى</p></div>';
    }
}

function setupDragAndDrop() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('drag-over');
    });
    
    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('drag-over');
    });
    
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(Array.from(e.dataTransfer.files));
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(Array.from(e.target.files));
        }
    });
}

async function handleFileUpload(files) {
    const txtFiles = files.filter(f => f.name.toLowerCase().endsWith('.txt'));
    
    if (txtFiles.length === 0) {
        showStatus('لم يتم العثور على ملفات نصية (.txt)', 'error');
        return;
    }
    
    const statusDiv = document.getElementById('upload-status');
    const filesList = document.getElementById('uploaded-files-list');
    
    showStatus(`📤 جاري رفع ${txtFiles.length} ملف...`, 'info');
    filesList.innerHTML = '';
    
    const formData = new FormData();
    txtFiles.forEach(file => {
        formData.append('files', file);
    });
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus(`✅ ${result.message}`, 'success');
            
            result.files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-icon">📄</div>
                        <div class="file-details">
                            <div class="file-name">${file.filename}</div>
                            <div class="file-size">${formatFileSize(file.size)}</div>
                        </div>
                    </div>
                    <div class="file-status success">تم الرفع</div>
                `;
                
                filesList.appendChild(fileItem);
            });
        } else {
            showStatus(`❌ ${result.message || 'حدث خطأ'}`, 'error');
        }
    } catch (error) {
        showStatus('❌ خطأ في الاتصال بالخادم', 'error');
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 بايت';
    const k = 1024;
    const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('upload-status');
    statusDiv.className = `status-message ${type}`;
    statusDiv.textContent = message;
}

document.getElementById('config-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const config = {
        embedding_model: document.getElementById('embedding-model').value || 'all-MiniLM-L6-v2',
        llm_model: document.getElementById('llm-model').value || 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        chunk_size: parseInt(document.getElementById('chunk-size').value) || 500,
        chunk_overlap: parseInt(document.getElementById('chunk-overlap').value) || 50,
        top_k: parseInt(document.getElementById('top-k').value) || 5,
        similarity_threshold: parseFloat(document.getElementById('similarity-threshold').value) || 0.3
    };
    
    const statusDiv = document.getElementById('config-status');
    statusDiv.className = 'status-message info';
    statusDiv.textContent = '⏳ جاري حفظ الإعدادات...';
    
    try {
        const response = await fetch('/api/system', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.className = 'status-message success';
            statusDiv.textContent = '✅ تم حفظ الإعدادات بنجاح';
        } else {
            statusDiv.className = 'status-message error';
            statusDiv.textContent = `❌ ${result.message || 'فشل الحفظ'}`;
        }
    } catch (error) {
        statusDiv.className = 'status-message error';
        statusDiv.textContent = '❌ خطأ في الاتصال بالخادم';
    }
});

function resetConfig() {
    document.getElementById('embedding-model').value = 'all-MiniLM-L6-v2';
    document.getElementById('llm-model').value = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0';
    document.getElementById('chunk-size').value = 500;
    document.getElementById('chunk-overlap').value = 50;
    document.getElementById('top-k').value = 5;
    document.getElementById('similarity-threshold').value = 0.3;
    
    const statusDiv = document.getElementById('config-status');
    statusDiv.className = 'status-message info';
    statusDiv.textContent = 'تم تعيين القيم الافتراضية، قم بالحفظ لتطبيقها';
}

document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById('search-query').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        performSearch();
    }
});

async function loadConfig() {
    try {
        const response = await fetch('/api/system');
        const config = await response.json();
        
        document.getElementById('embedding-model').value = config.embedding_model || 'all-MiniLM-L6-v2';
        document.getElementById('llm-model').value = config.llm_model || 'TinyLlama/TinyLlama-1.1B-Chat-v1.0';
        document.getElementById('chunk-size').value = config.chunk_size || 500;
        document.getElementById('chunk-overlap').value = config.chunk_overlap || 50;
        document.getElementById('top-k').value = config.top_k || 5;
        document.getElementById('similarity-threshold').value = config.similarity_threshold || 0.3;
    } catch (error) {
        console.log('فشل تحميل الإعدادات');
    }
}

window.onload = function() {
    showSection('chat');
    loadConfig();
    setupDragAndDrop();
};