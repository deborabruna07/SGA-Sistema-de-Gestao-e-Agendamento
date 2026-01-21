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
        firstDay: 0,
        fixedWeekCount: true,
        height: "auto",
        selectable: false,

        /* 🔒 DOMINGO E SEGUNDA */
        dayCellClassNames: function (arg) {
            const dia = arg.date.getDay();
            if (dia === 0 || dia === 1) {
                return ["dia-fechado"];
            }
            return [];
        },

        dateClick: function (info) {
            const diaSemana = info.date.getDay();

            const hoje = new Date();
            hoje.setHours(0,0,0,0);

            const dataClicada = new Date(info.date);
            dataClicada.setHours(0,0,0,0);

            if (diaSemana === 0 || diaSemana === 1) {
                alert("❌ O salão não funciona aos domingos e segundas.");
                return;
            }

            if (dataClicada <= hoje) {
                alert("❌ Não é possível agendar para hoje ou datas anteriores.");
                horariosContainer.style.display = "none";
                return;
            }

            document.querySelectorAll(".fc-daygrid-day")
                .forEach(d => d.classList.remove("selecionado"));

            info.dayEl.classList.add("selecionado");

            dataInput.value = info.dateStr;
            horaInput.value = "";
            dadosClienteDiv.style.display = "none";

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
        fetch(`/horarios/${data}/${servicoSelect.value}`)
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

                    btn.onclick = () => {
                        document.querySelectorAll(".horario-btn")
                            .forEach(b => b.classList.remove("ativo"));

                        btn.classList.add("ativo");
                        horaInput.value = h;
                        dadosClienteDiv.style.display = "block";
                    };

                    horariosDiv.appendChild(btn);
                });
            });
    }
});

function abrirPopup() {
    document.getElementById("popup-sucesso").style.display = "flex";
}

function fecharPopup() {
    document.getElementById("popup-sucesso").style.display = "none";
}

