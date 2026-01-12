# 💇‍♀️ SGA – Sistema de Gerenciamento e Agendamento para Salão

## 📌 Descrição

O **SGA (Sistema de Gerenciamento e Agendamento para Salão de Beleza)** é uma aplicação web desenvolvida em **Python utilizando o framework Flask**, com o objetivo de automatizar e organizar o agendamento de serviços em um salão de beleza.

O sistema foi projetado para atender **regras de negócio reais**, especialmente serviços que envolvem **tempo ativo e tempo de espera**, como progressiva, selagem e outros procedimentos químicos. Durante o tempo de espera, o sistema permite o **encaixe de outros clientes**, garantindo melhor aproveitamento do tempo da profissional.

---

## 🎯 Objetivos do Sistema

* Automatizar o processo de agendamento de serviços;
* Evitar conflitos de horário;
* Permitir encaixes durante tempos de espera;
* Facilitar o controle da agenda;
* Gerar relatórios simples de agendamentos.

---

## ⚙️ Funcionalidades

* Cadastro de serviços com:

  * Tempo ativo inicial;
  * Tempo de espera;
  * Tempo ativo final.
* Agendamento de clientes com validação de conflitos;
* Bloqueio automático de horários ocupados;
* Exibição de mensagens de sucesso ou erro;
* Geração automática de planilha **CSV** com os agendamentos;
* Persistência de dados com **SQLite**;
* Interface web simples e funcional.

---

## 🛠️ Tecnologias Utilizadas

* Python 3
* Flask
* SQLite
* HTML5
* Git e GitHub

---

## 📁 Estrutura do Projeto

```
sga_salao/
│ app.py
│ database.db
│ agendamentos.csv
│ .gitignore
└── templates/
    └── index.html
```

---

## ▶️ Como Executar o Projeto

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/sga-salao.git
cd sga-salao
```

### 2️⃣ Criar e ativar o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Instalar dependências

```bash
pip install flask
```

### 4️⃣ Executar a aplicação

```bash
python app.py
```

Acesse no navegador:

```
http://127.0.0.1:5000/
```

---

## 🧪 Exemplos de Uso

* Cadastro de um serviço de **Progressiva** com:

  * 60 min de tempo ativo inicial;
  * 60 min de tempo de espera;
  * 60 min de tempo ativo final.

* Agendamento permite encaixe de outros serviços durante o tempo de espera.

---

## 📊 Relatórios

O sistema gera automaticamente um arquivo `agendamentos.csv` contendo:

* Cliente
* Serviço
* Data
* Horário de início
* Horário de fim
* Status do agendamento

