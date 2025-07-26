import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Historico() {
  const [historico, setHistorico] = useState([]);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    fetch("http://10.1.1.171:8000/api/historico/todos")
      .then((res) => res.json())
      .then((data) => setHistorico(data))
      .catch(() => setHistorico([]));
  }, []);

  return (
    <div className={`min-h-screen ${darkMode ? "bg-black text-green-400" : "bg-white text-zinc-800"} font-mono px-4 py-6`}>
      <header className="flex justify-between items-center mb-6 max-w-4xl mx-auto">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">
            <span className={darkMode ? "text-green-500" : "text-purple-700"}>debuga.ai</span>
            <span className="text-sm text-gray-400"> | Histórico</span>
          </h1>
          <Link to="/" className="text-sm underline hover:text-green-300 ml-2">? Voltar ao chat</Link>
        </div>
        <button
          onClick={() => setDarkMode((prev) => !prev)}
          className="px-3 py-1 text-sm rounded border border-gray-400 hover:bg-gray-200 dark:hover:bg-zinc-800"
        >
          {darkMode ? "?? Claro" : "?? Escuro"}
        </button>
      </header>

      <div className="max-w-4xl mx-auto space-y-4">
        {historico.length === 0 && <p>Nenhum histórico encontrado.</p>}
        {historico.map((item, index) => (
          <div
            key={index}
            className={`border rounded-md p-4 shadow-md ${darkMode ? "bg-zinc-900 border-zinc-700" : "bg-zinc-100 border-zinc-300"}`}
          >
            <p><span className="font-bold text-green-500">Pergunta:</span> {item.prompt}</p>
            <p><span className="font-bold text-purple-600">Resposta:</span> {item.resposta}</p>
            <p className="text-sm text-gray-500 mt-2">
              Agente: <strong>{item.agente}</strong> | {new Date(item.timestamp).toLocaleString("pt-BR")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Historico;
