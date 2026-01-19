// Carrega serviços ao abrir a página
window.addEventListener("DOMContentLoaded", carregarServicos);

// SUBMIT DO FORMULÁRIO
document.getElementById("formServico").addEventListener("submit", async function (e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);

    try {
        const res = await fetch("/servico", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!data.sucesso) {
            alert("Erro ao cadastrar serviço");
            return;
        }

        // Atualiza lista após cadastrar
        await carregarServicos();

        // Limpa formulário
        form.reset();

    } catch (err) {
        alert("Erro de comunicação com o servidor");
    }
});


// FUNÇÃO QUE BUSCA E MONTA A LISTA
async function carregarServicos() {
    try {
        const res = await fetch("/servico");
        const servicos = await res.json();

        const container = document.getElementById("lista-servicos");
        container.innerHTML = "";

        // Se não houver serviços
        if (!servicos || servicos.length === 0) {
            container.innerHTML = `<p id="nenhum-servico">Nenhum serviço cadastrado</p>`;
            return;
        }

        // Cria tabela
        const tabela = document.createElement("table");
        tabela.className = "admin-table";
        tabela.id = "tabela-servicos";

        tabela.innerHTML = `
            <tr>
                <th>Serviço</th>
                <th>Ação</th>
            </tr>
        `;

        servicos.forEach(servico => {
    const linha = document.createElement("tr");
    linha.innerHTML = `
        <td>${servico.nome}</td>
        <td>
            <a href="/remover-servico/${servico.id}"
            onclick="return confirm('Tem certeza que deseja remover este serviço?')"
            class="link-remover">
                ❌ Remover
            </a>
        </td>
    `;
    tabela.appendChild(linha);
});

        container.appendChild(tabela);

    } catch (err) {
        console.error(err);
        document.getElementById("lista-servicos").innerHTML =
            "<p>Erro ao carregar serviços</p>";
    }
}


// REMOVER SERVIÇO
async function removerServico(id) {
    if (!confirm("Deseja remover este serviço?")) return;

    try {
        const res = await fetch(`/servico/${id}`, {
            method: "DELETE"
        });

        const data = await res.json();

        if (!data.sucesso) {
            alert("Erro ao remover serviço");
            return;
        }

        carregarServicos();

    } catch (err) {
        alert("Erro ao remover serviço");
    }
}
