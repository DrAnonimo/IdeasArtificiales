/* -------------- CONFIG -------------- */
const PERSONAJES = {
  sherlock: {
    nombre: "Sherlock Holmes",
    prompt: `Eres Sherlock Holmes, Londres 1895. Sabes: lord Huxley fue hallado con una daga; puerta cerrada por dentro; ventana abierta. No ocultas nada. 40 palabras máx, primera persona, tono victoriano.`
  },
  rose: {
    nombre: "Rose, camarera",
    prompt: `Eres Rose, 25 años, camarera. Sabes: a las 22:00 llevó brandy; lord discutía con Arthur; a las 23:00 oyó portazo. Ocultas: robaste 50 libras y temes ser descubierta. Si te preguntan por dinero, evade. 40 palabras máx, época.`
  },
  arthur: {
    nombre: "Arthur Huxley, sobrino",
    prompt: `Eres Arthur, 28 años, sobrino heredero. Sabes: tu tío amenazó con desheredarte; estuviste en el club hasta 23:30 (testigos). Ocultas: volviste a casa 00:10 y viste a Rose cerca del estudio. Si te presionan, desvías hacia ella. 40 palabras máx.`
  }
};

const SOLUCION = {culpable: "arthur", arma: "daga", motivo: "herencia"};

/* -------------- ESTADO -------------- */
let keyOpenAI = "";
let historia   = [];
let personajeActual = "sherlock";
let pistasDescubiertas = new Set();

/* -------------- INIT -------------- */
window.onload = () => {
  keyOpenAI = localStorage.getItem("openai_key");
  if (!keyOpenAI) {
    document.getElementById("auth").style.display = "block";
  } else {
    iniciarJuego();
  }
};

function guardarKey() {
  const k = document.getElementById("keyIn").value.trim();
  if (!k.startsWith("sk-")) { alert("Clave inválida"); return; }
  localStorage.setItem("openai_key", k);
  keyOpenAI = k;
  document.getElementById("auth").style.display = "none";
  iniciarJuego();
}

function iniciarJuego() {
  document.getElementById("game").style.display = "block";
  addMsg("narrador", "Narrador", "Lord Huxley ha sido encontrado muerto. La biblioteca estaba cerrada por dentro y solo la ventana entreabierta deja entrar aire helado. Interroga a quien quieras.");
  addMsg("npc", PERSONAJES[personajeActual].nombre, "Estoy a tu disposición. ¿Qué deseas saber?");
  console.log("[DEV] Partida iniciada. Solución:", SOLUCION);
}

/* -------------- CHAT -------------- */
function addMsg(tipo, autor, texto) {
  const div = document.createElement("div");
  div.className = "msg " + (tipo === "user" ? "user" : "npc");
  div.textContent = autor + ": " + texto;
  document.getElementById("chat").appendChild(div);
  div.scrollIntoView({behavior:"smooth"});
}

function enviar() {
  const txt = document.getElementById("input").value.trim();
  if (!txt) return;
  addMsg("user", "Tú", txt);
  document.getElementById("input").value = "";
  historia.push({role: "user", content: txt});
  consultarIA();
}

async function consultarIA() {
  const sys = PERSONAJES[personajeActual].prompt;
  const messages = [{role: "system", content: sys}, ...historia];
  const raw = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + keyOpenAI
    },
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: messages,
      max_tokens: 120,
      temperature: 0.7
    })
  });
  if (!raw.ok) {
    const err = await raw.text();
    addMsg("npc", "Error", "OpenAI: " + err);
    return;
  }
  const json = await raw.json();
  const reply = json.choices[0].message.content;
  addMsg("npc", PERSONAJES[personajeActual].nombre, reply);
  historia.push({role: "assistant", content: reply});
  detectarPista(reply);
}

/* -------------- PISTAS -------------- */
const PISTAS = [
  ["ventana", "abierta"],
  ["daga", "puñal"],
  ["herencia", "desheredado"],
  ["00:10", "medianoche"],
  ["50 libras", "robado", "dinero"]
];
function detectarPista(texto) {
  const low = texto.toLowerCase();
  for (const arr of PISTAS) {
    if (arr.some(p => low.includes(p))) {
      const key = arr[0];
      if (!pistasDescubiertas.has(key)) {
        pistasDescubiertas.add(key);
        addNota(arr.join("/"));
        console.log("[DEV] Nueva pista detectada:", key);
      }
    }
  }
}
function addNota(str) {
  const li = document.createElement("li");
  li.textContent = str;
  document.getElementById("notas").appendChild(li);
}

/* -------------- CAMBIAR PERSONAJE -------------- */
function cambiarPersonaje() {
  const nicks = Object.keys(PERSONAJES);
  const idx = (nicks.indexOf(personajeActual) + 1) % nicks.length;
  personajeActual = nicks[idx];
  addMsg("narrador", "Narrador", `Ahora hablas con ${PERSONAJES[personajeActual].nombre}.`);
}

/* -------------- RESOLVER -------------- */
function resolver() {
  const culp = prompt("¿Quién es el culpable? (sherlock / rose / arthur)");
  const arma = prompt("¿Qué arma se usó? (daga / …)");
  const moti = prompt("¿Motivo? (herencia / …)");
  if (!culp || !arma || !moti) return;

  const okC = culp.toLowerCase().trim() === SOLUCION.culpable;
  const okA = arma.toLowerCase().trim() === SOLUCION.arma;
  const okM = moti.toLowerCase().trim() === SOLUCION.motivo;
  const total = okC && okA && okM;

  const title = total ? "¡Caso resuelto!" : "Solución incorrecta";
  const text  = total
    ? `Enhorabuena. ${SOLUCION.culpable} mató a lord Huxley con la ${SOLUCION.arma} por ${SOLUCION.motivo}.`
    : `Todavía hay lagunas. Repasa las pistas.`;

  mostrarModal(title, text);
  console.log("[DEV] Intento de resolución:", {culp, arma, moti, okC, okA, okM, total});
}

/* -------------- MODAL -------------- */
function mostrarModal(title, text) {
  document.getElementById("modal-title").textContent = title;
  document.getElementById("modal-text").textContent  = text;
  document.getElementById("modal").style.display = "block";
}
function cerrarModal() {
  document.getElementById("modal").style.display = "none";
}
