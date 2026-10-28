const form = document.querySelector(".cmd-form");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const telefone = document.getElementById("numero_tlm").value;
    const codigo = document.getElementById("pin").value;

    const response = await fetch("http://localhost:8001/login_cmd", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            telefone: telefone,
            codigo: codigo
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail);
        return;
    }

    alert("Login realizado com sucesso!");

    localStorage.setItem("user_id", data.id);
    localStorage.setItem("user_nome", data.nome);

    window.location.href = "eleitor-dashboard.html";
});