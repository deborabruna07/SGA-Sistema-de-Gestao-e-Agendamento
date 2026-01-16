document.addEventListener("DOMContentLoaded", function () {

    const calendarEl = document.getElementById("calendar");
    const horariosContainer = document.getElementById("horarios-container");
    const horariosDiv = document.getElementById("horarios");

    const servicoSelect = document.getElementById("servico");
    const dataInput = document.getElementById("dataSelecionada");
    const horaInput = document.getElementById("horaSelecionada");

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: "pt-br",
        height: "auto",

        dateClick: function (info) {
            // destaque visual da data
            document.querySelectorAll(".fc-day").forEach(d =>
                d.classList.remove("selecionado")
            );
            info.dayEl.classList.add("selecionado");

            dataInput.value = info.dateStr;

            // só carrega horários se serviço estiver selecionado
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

        // se já houver data selecionada, recarrega horários
        if (dataInput.value) {
            carregarHorarios(dataInput.value);
        }
    });
});

function carregarHorarios(data) {
    const servico = document.getElementById("servico").value;
    const horariosDiv = document.getElementById("horarios");
    const container = document.getElementById("horarios-container");

    if (!servico) return;

    fetch(`/horarios/${data}/${servico}`)
        .then(res => res.json())
        .then(horarios => {
            horariosDiv.innerHTML = "";
            container.style.display = "block";

            if (horarios.length === 0) {
                horariosDiv.innerHTML = "<p>❌ Nenhum horário disponível</p>";
                return;
            }

            horarios.forEach(h => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.innerText = h;
                btn.className = "horario-btn";
                btn.onclick = () => selecionarHorario(btn, h);
                horariosDiv.appendChild(btn);
            });
        });
}

function selecionarHorario(btn, hora) {
    document.getElementById("horaSelecionada").value = hora;
    document.querySelectorAll(".horario-btn").forEach(b => b.classList.remove("ativo"));
    btn.classList.add("ativo");
}
