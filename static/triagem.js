let escolhas = { textura: '', tamanho: '', volume: '' };

function selecionarTextura(tipo) {
    escolhas.textura = tipo;
    document.getElementById('passo-textura').style.display = 'none';
    
    const gridTamanho = document.getElementById('grid-tamanho');
    // Aqui as imagens mudam com base na textura escolhida (ex: cabelo-liso-curto.png)
    gridTamanho.innerHTML = `
        <div class="opcao" onclick="selecionarTamanho('curto')">
            <img src="/static/img/cabelo-${tipo}-curto.png">
            <span>Curto</span>
        </div>
        <div class="opcao" onclick="selecionarTamanho('medio')">
            <img src="/static/img/cabelo-${tipo}-medio.png">
            <span>Médio</span>
        </div>
        <div class="opcao" onclick="selecionarTamanho('longo')">
            <img src="/static/img/cabelo-${tipo}-longo.png">
            <span>Longo</span>
        </div>
    `;
    document.getElementById('passo-tamanho').style.display = 'block';
}

function selecionarTamanho(tam) {
    escolhas.tamanho = tam;
    document.getElementById('passo-tamanho').style.display = 'none';
    
    const gridVolume = document.getElementById('grid-volume');
    // As imagens de volume também seguem a lógica de textura e tamanho
    gridVolume.innerHTML = `
        <div class="opcao" onclick="finalizarTriagem('pouco')">
            <img src="/static/img/cabelo-${escolhas.textura}-${tam}-pouco.png">
            <span>Pouco Volume</span>
        </div>
        <div class="opcao" onclick="finalizarTriagem('cheio')">
            <img src="/static/img/cabelo-${escolhas.textura}-${tam}-cheio.png">
            <span>Muito Volume</span>
        </div>
    `;
    document.getElementById('passo-volume').style.display = 'block';
}

function finalizarTriagem(vol) {
    escolhas.volume = vol;
    const perfilCompleto = `Cabelo ${escolhas.textura}, ${escolhas.tamanho} e volume ${vol}`;
    
    // Envia para o Flask salvar na sessão
    fetch('/salvar-perfil', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ perfil: perfilCompleto })
    }).then(() => {
        document.getElementById('perfil-texto').innerText = perfilCompleto;
        document.getElementById('resultado-triagem').style.display = 'block';
    });
}