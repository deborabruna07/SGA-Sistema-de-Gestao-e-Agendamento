document.addEventListener("DOMContentLoaded", function () {

    const calendarEl = document.getElementById("calendar");
    const horariosContainer = document.getElementById("horarios-container");
    const horariosDiv = document.getElementById("horarios");
    const dadosClienteDiv = document.getElementById("dados-cliente");

    const servicoSelect = document.getElementById("servico");
    const dataInput = document.getElementById("dataSelecionada");
    const horaInput = document.getElementById("horaSelecionada");

    dadosClienteDiv.style.display = "none";

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: "pt-br",
        height: "auto",

        /* 🔒 MARCAR DOMINGO E SEGUNDA COMO FECHADO */
        dayCellDidMount: function(info) {
    // ❌ ignora dias fora do mês atual
    if (info.isOther) return;

    const diaSemana = info.date.getDay(); // 0 = dom, 1 = seg
    const dia = info.date.getDate();

    info.el.setAttribute("data-dia", dia);

    if (diaSemana === 0 || diaSemana === 1) {
        info.el.classList.add("dia-fechado");
    }
},

        dateClick: function (info) {
            const hoje = new Date();
            hoje.setHours(0, 0, 0, 0);

            const dataClicada = new Date(info.dateStr);
            const diaSemana = dataClicada.getDay();

            /* 🚫 BLOQUEAR DOMINGO E SEGUNDA */
            if (diaSemana === 0 || diaSemana === 1) {
                return;
            }

            if (dataClicada < hoje) {
                alert("Não é possível agendar datas passadas.");
                return;
            }

            document.querySelectorAll(".fc-day")
                .forEach(d => d.classList.remove("selecionado"));

            info.dayEl.classList.add("selecionado");

            dataInput.value = info.dateStr;
            dadosClienteDiv.style.display = "none";
            horaInput.value = "";

            if (servicoSelect.value) {
                carregarHorarios(info.dateStr);
            } else {
                horariosContainer.style.display = "none";
                horariosDiv.innerHTML = "<p>Selecione um serviço primeiro.</p>";
            }
        }
    });

    calendar.render();

    servicoSelect.addEventListener("change", function () {
        horariosContainer.style.display = "none";
        horariosDiv.innerHTML = "";
        horaInput.value = "";
        dadosClienteDiv.style.display = "none";

        if (dataInput.value) {
            carregarHorarios(dataInput.value);
        }
    });

    function carregarHorarios(data) {
        const servico = servicoSelect.value;
        if (!servico) return;

        fetch(`/horarios/${data}/${servico}`)
            .then(res => res.json())
            .then(horarios => {
                horariosDiv.innerHTML = "";
                horariosContainer.style.display = "block";

                if (horarios.length === 0) {
                    horariosDiv.innerHTML = "<p>❌ Nenhum horário disponível</p>";
                    return;
                }

                horarios.forEach(h => {
                    const btn = document.createElement("button");
                    btn.type = "button";
                    btn.innerText = h;
                    btn.className = "horario-btn";

                    btn.addEventListener("click", () => {
                        document.querySelectorAll(".horario-btn")
                            .forEach(b => b.classList.remove("ativo"));

                        btn.classList.add("ativo");
                        horaInput.value = h;

                        dadosClienteDiv.style.display = "block";
                    });

                    horariosDiv.appendChild(btn);
                });
            });
    }

});

/* POPUP */
function abrirPopup() {
    document.getElementById("popup-sucesso").style.display = "flex";
}

function fecharPopup() {
    document.getElementById("popup-sucesso").style.display = "none";
    window.location.href = "/";
}