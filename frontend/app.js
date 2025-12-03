let currentSection = 'chat';

function showSection(section) {
    document.querySelectorAll('.section').forEach(div => {
        div.style.display = 'none';
    });
    
    document.getElementById(section + '-section').style.display = 'block';
    currentSection = section;
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) {
        alert('يرجى كتابة سؤال');
        return;
    }
    
    const chatBox = document.getElementById('chat-box');
    
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = message;
    chatBox.appendChild(userMessage);
    
    input.value = '';
    
    const loading = document.createElement('div');
    loading.className = 'message system-message';
    loading.textContent = 'جاري البحث عن إجابة...';
    loading.id = 'loading-message';
    chatBox.appendChild(loading);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        });
        
        chatBox.removeChild(loading);
        
        const data = await response.json();
        
        const systemMessage = document.createElement('div');
        systemMessage.className = 'message system-message';
        
        const answer = document.createElement('div');
        answer.textContent = data.answer;
        systemMessage.appendChild(answer);
        
        if (data.sources && data.sources.length > 0) {
            const sourcesContainer = document.createElement('div');
            sourcesContainer.className = 'sources-container';
            
            const sourcesTitle = document.createElement('div');
            sourcesTitle.className = 'sources-title';
            sourcesTitle.innerHTML = '📚 المصادر المستخدمة:';
            sourcesContainer.appendChild(sourcesTitle);
            
            data.sources.forEach((source, index) => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                
                const fileInfo = document.createElement('div');
                fileInfo.className = 'source-file';
                fileInfo.innerHTML = `📄 ${source.file}`;
                sourceItem.appendChild(fileInfo);
                
                const content = document.createElement('div');
                content.className = 'source-content';
                content.textContent = source.content;
                sourceItem.appendChild(content);
                
                const score = document.createElement('div');
                score.className = 'source-score';
                score.textContent = `تشابه: ${source.score.toFixed(3)}`;
                sourceItem.appendChild(score);
                
                sourcesContainer.appendChild(sourceItem);
            });
            
            systemMessage.appendChild(sourcesContainer);
        }
        
        chatBox.appendChild(systemMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
        
    } catch (error) {
        chatBox.removeChild(loading);
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message system-message';
        errorMessage.textContent = '❌ حدث خطأ في الاتصال بالخادم';
        chatBox.appendChild(errorMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

async function performSearch() {
    const query = document.getElementById('search-query').value.trim();
    
    if (!query) {
        alert('يرجى كتابة كلمة للبحث');
        return;
    }
    
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">جاري البحث...</div>';
    
    try {
        const response = await fetch(`/api/search?query=${encodeURIComponent(query)}&top_k=10`);
        const data = await response.json();
        
        resultsDiv.innerHTML = '';
        
        if (data.success && data.results.length > 0) {
            data.results.forEach((result, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const score = document.createElement('div');
                score.className = 'result-score';
                score.textContent = `نتيجة ${index + 1} - تشابه: ${result.score.toFixed(3)}`;
                resultItem.appendChild(score);
                
                const idInfo = document.createElement('div');
                idInfo.style.marginBottom = '10px';
                idInfo.style.color = '#666';
                idInfo.style.fontSize = '14px';
                idInfo.innerHTML = `المعرف: ${result.chunk_id}`;
                resultItem.appendChild(idInfo);
                
                resultsDiv.appendChild(resultItem);
            });
        } else {
            resultsDiv.innerHTML = '<div style="text-align: center; padding: 30px; color: #666;">لم يتم العثور على نتائج</div>';
        }
        
    } catch (error) {
        resultsDiv.innerHTML = '<div style="text-align: center; padding: 30px; color: #f44336;">❌ خطأ في الاتصال بالخادم</div>';
    }
}

document.getElementById('folder-input').addEventListener('change', async function(e) {
    const files = Array.from(e.target.files);
    const txtFiles = files.filter(f => f.name.toLowerCase().endsWith('.txt'));
    
    if (txtFiles.length === 0) {
        alert('لم يتم العثور على ملفات نصية');
        return;
    }
    
    const statusDiv = document.getElementById('upload-status');
    const filesDiv = document.getElementById('uploaded-files');
    
    statusDiv.innerHTML = `📤 جاري رفع ${txtFiles.length} ملف...`;
    statusDiv.className = '';
    filesDiv.innerHTML = '';
    
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
            statusDiv.innerHTML = `✅ ${result.message}`;
            statusDiv.className = 'success';
            
            result.files.forEach(file => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'file-item';
                fileDiv.innerHTML = `📄 ${file.filename}`;
                filesDiv.appendChild(fileDiv);
            });
        } else {
            statusDiv.innerHTML = `❌ ${result.message || 'حدث خطأ'}`;
            statusDiv.className = 'error';
        }
    } catch (error) {
        statusDiv.innerHTML = '❌ خطأ في الاتصال بالخادم';
        statusDiv.className = 'error';
    }
});

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
    statusDiv.innerHTML = '⏳ جاري حفظ الإعدادات وإعادة تحميل النماذج...';
    statusDiv.className = '';
    
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
            statusDiv.innerHTML = '✅ تم حفظ الإعدادات بنجاح';
            statusDiv.className = 'success';
        } else {
            statusDiv.innerHTML = `❌ ${result.message || 'فشل الحفظ'}`;
            statusDiv.className = 'error';
        }
    } catch (error) {
        statusDiv.innerHTML = '❌ خطأ في الاتصال بالخادم';
        statusDiv.className = 'error';
    }
});

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
    
    const chatBox = document.getElementById('chat-box');
    const welcome = document.createElement('div');
    welcome.className = 'message system-message';
    welcome.innerHTML = 'مرحباً بك في نظام RAG العربي! 👋<br><br>يمكنك:<br>1. رفع مستندات نصية من قسم "رفع ملفات"<br>2. طرح أسئلة باللغة العربية<br>3. ضبط إعدادات النظام حسب الحاجة';
    chatBox.appendChild(welcome);
};