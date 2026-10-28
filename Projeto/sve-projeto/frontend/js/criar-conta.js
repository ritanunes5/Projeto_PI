const form = document.getElementById("formCriarConta");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const dados = {
        nome: document.getElementById("nome").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        role: document.getElementById("role").value.toLowerCase(),
        codigo_admin: document.getElementById("codigo_admin")?.value || null,
        codigo: document.getElementById("codigo")?.value || null,
        numero_identificacao: document.getElementById("numero_identificacao").value,
        telefone: document.getElementById("telefone")?.value || null,
        freguesia: document.getElementById("freguesia")?.value || null,
        data_nascimento: document.getElementById("data_nascimento").value,
        recenseado: document.getElementById("recenseado").checked
    };

    try {
        const response = await fetch("http://localhost:8001/users", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        const resultado = await response.json();

        if (!response.ok) {
            alert("Erro ao criar conta: " + JSON.stringify(resultado));
            return;
        }

        alert("Conta criada com sucesso!");
        console.log(resultado);

    } catch (error) {
        console.error(error);
        alert("Erro ao ligar à API.");
    }
});