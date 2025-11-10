# language: pt
Funcionalidade: Criação de Hábitos em Rotinas
    Como usuário do TimeBlock
    Eu quero criar hábitos com horários específicos
    Para organizar minha rotina diária

    Contexto:
        Dado que existe uma rotina chamada "Matinal"

    Cenário: Criar hábito com dados válidos
        Quando eu crio um hábito com os seguintes dados:
            | Campo             | Valor               |
            | Título            | Exercício Matinal   |
            | Horário Início    | 06:00               |
            | Horário Fim       | 07:00               |
            | Recorrência       | EVERYDAY            |
        Então o hábito deve ser criado com sucesso
        E o hábito deve ter um ID único
        E o título deve ser "Exercício Matinal"

    Cenário: Rejeitar título vazio
        Quando eu tento criar um hábito com título vazio
        Então o sistema deve rejeitar com erro "cannot be empty"

    Cenário: Rejeitar horário inválido
        Quando eu tento criar um hábito com:
            | Campo             | Valor     |
            | Título            | Inválido  |
            | Horário Início    | 07:00     |
            | Horário Fim       | 06:00     |
        Então o sistema deve rejeitar com erro "Start time must be before end time"
